import os
import json
import uuid
import logging
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# Es mejor usar variables de entorno, Secrets Manager es mas lento y costoso 
TASKS_TABLE_NAME = os.environ["TASKS_TABLE_NAME"]  
AUDIT_BUCKET_NAME = os.environ["AUDIT_BUCKET_NAME"]
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

table = dynamodb.Table(TASKS_TABLE_NAME)
VALID_STATUS = {"pending", "in_progress", "done"}

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def error_response(status_code: int, message: str, **extra):
    payload = {"message": message}
    payload.update(extra)
    return response(status_code, payload)

def parse_body(event: dict) -> dict:
    body = event.get("body")
    if not body:
        return {}
    return json.loads(body)

def get_path_param(event: dict, key: str):
    return (event.get("pathParameters") or {}).get(key)

def get_method(event: dict) -> str:
    return event.get("requestContext", {}).get("http", {}).get("method", "")

def get_jwt_claims(event: dict) -> dict:
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )

def require_authenticated_claims(event: dict) -> dict:
    claims = get_jwt_claims(event)
    if not claims:
        # Normalmente API Gateway bloquearía esto antes,
        # pero lo dejamos por seguridad defensiva.
        raise PermissionError("Missing or invalid JWT claims")
    return claims

def audit_event(event_type: str, payload: dict):
    ts = now_utc()
    date_prefix = ts[0:10].replace("-", "/")
    object_key = f"events/{date_prefix}/{event_type}_{uuid.uuid4()}.json"
    
    document = {
        "event_type": event_type,
        "timestamp": ts,
        "payload": payload
    }
    
    s3.put_object(
        Bucket=AUDIT_BUCKET_NAME,
        Key=object_key,
        Body=json.dumps(document).encode("utf-8"),
        ContentType="application/json"
    )


def get_actor_sub(claims: dict) -> str:
    return claims.get("sub", "unknown")


def get_actor_username(claims: dict) -> str:
    return claims.get("username") or claims.get("cognito:username") or claims.get("email", "unknown")


def ensure_task_owner(task: dict, actor_sub: str):
    if task.get("created_by") != actor_sub:
        raise PermissionError("You are not allowed to modify this task")


def get_task_item(task_id: str):
    result = table.get_item(Key={"task_id": task_id})
    return result.get("Item")


def list_tasks():
    result = table.scan()
    items = result.get("Items", [])

    return response(
        200,
        {
            "message": "Tasks retrieved successfully",
            "count": len(items),
            "tasks": items,
            "timestamp": now_utc()
        }
    )


def get_task(task_id: str):
    item = get_task_item(task_id)

    if not item:
        return error_response(404, "Task not found", task_id=task_id)

    return response(
        200,
        {
            "message": "Task retrieved successfully",
            "task": item,
            "timestamp": now_utc()
        }
    )


def create_task(event: dict):
    claims = require_authenticated_claims(event)
    body = parse_body(event)

    title = body.get("title")
    if not title or not isinstance(title, str):
        raise ValueError("Field 'title' is required and must be a string")

    status = body.get("status", "pending")
    if status not in VALID_STATUS:
        raise ValueError("Field 'status' must be one of: pending, in_progress, done")

    task_id = str(uuid.uuid4())
    ts = now_utc()

    actor_sub = get_actor_sub(claims)
    actor_username = get_actor_username(claims)

    item = {
        "task_id": task_id,
        "title": title,
        "status": status,
        "created_at": ts,
        "updated_at": ts,
        "created_by": actor_sub,
        "created_by_username": actor_username
    }

    table.put_item(Item=item)

    audit_event(
        event_type="task_created",
        payload={
            "task_id": task_id,
            "actor_sub": actor_sub,
            "actor_username": actor_username,
            "task": item
        }
    )
    
    return response(
        201,
        {
            "message": "Task created successfully",
            "task": item,
            "timestamp": ts
        }
    )


def update_task(event: dict, task_id: str):
    claims = require_authenticated_claims(event)
    body = parse_body(event)

    allowed_fields = {}
    if "title" in body:
        if not isinstance(body["title"], str) or not body["title"].strip():
            raise ValueError("Field 'title' must be a non-empty string")
        allowed_fields["title"] = body["title"].strip()

    if "status" in body:
        if body["status"] not in VALID_STATUS:
            raise ValueError("Field 'status' must be one of: pending, in_progress, done")
        allowed_fields["status"] = body["status"]

    if not allowed_fields:
        raise ValueError("Nothing to update. Provide 'title' and/or 'status'")

    actor_sub = get_actor_sub(claims)
    existing = get_task_item(task_id)
    if not existing:
        return error_response(404, "Task not found", task_id=task_id)

    ensure_task_owner(existing, actor_sub)

    ts = now_utc()

    expr_attr_names = {
        "#updated_at": "updated_at",
        "#updated_by": "updated_by"
    }
    expr_attr_values = {
        ":updated_at": ts,
        ":updated_by": actor_sub
    }
    set_parts = [
        "#updated_at = :updated_at",
        "#updated_by = :updated_by"
    ]

    for field, value in allowed_fields.items():
        expr_attr_names[f"#{field}"] = field
        expr_attr_values[f":{field}"] = value
        set_parts.append(f"#{field} = :{field}")

    result = table.update_item(
        Key={"task_id": task_id},
        UpdateExpression="SET " + ", ".join(set_parts),
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
        ConditionExpression="attribute_exists(task_id)",
        ReturnValues="ALL_NEW"
    )

    updated_item = result["Attributes"]

    audit_event(
        event_type="task_updated",
        payload={
            "task_id": task_id,
            "actor_sub": actor_sub,
            "changes": allowed_fields,
            "task": updated_item
        }
    )
    
    return response(
        200,
        {
            "message": "Task updated successfully",
            "task": updated_item,
            "timestamp": ts
        }
    )


def delete_task(event: dict, task_id: str):
    claims = require_authenticated_claims(event)
    actor_sub = get_actor_sub(claims)

    existing = get_task_item(task_id)
    if not existing:
        return error_response(404, "Task not found", task_id=task_id)

    ensure_task_owner(existing, actor_sub)

    table.delete_item(Key={"task_id": task_id})

    audit_event(
        event_type="task_deleted",
        payload={
            "task_id": task_id,
            "actor_sub": actor_sub,
            "deleted_task": existing
        }
    )

    return response(
        200,
        {
            "message": "Task deleted successfully",
            "task_id": task_id,
            "timestamp": now_utc()
        }
    )


def lambda_handler(event, context):
    method = get_method(event)
    task_id = get_path_param(event, "task_id")

    try:
        if method == "GET" and not task_id:
            return list_tasks()

        if method == "GET" and task_id:
            return get_task(task_id)

        if method == "POST" and not task_id:
            return create_task(event)

        if method == "PATCH" and task_id:
            return update_task(event, task_id)

        if method == "DELETE" and task_id:
            return delete_task(event, task_id)

        return error_response(405, "Method not allowed")
    except PermissionError as exc:
        return error_response(403, str(exc))
    except json.JSONDecodeError:
        return error_response(400, "Request body must be valid JSON")
    except ValueError as exc:
        return error_response(400, str(exc))
    except ClientError:
        logger.exception("AWS client error while processing request")
        return error_response(500, "Internal server error")
    except Exception:
        logger.exception("Unhandled error while processing request")
        return error_response(500, "Internal server error")
