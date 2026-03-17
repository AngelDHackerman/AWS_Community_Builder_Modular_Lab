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

def parse_body(event: dict) -> dict:
    body = event.get("body")
    if not body:
        return{}
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
    
def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path_params = event.get("pathParameters") or {}
    task_id = path_params.get("task_id")

    jwt_claims = (
        event.get("requestContext", {})
             .get("authorizer", {})
             .get("jwt", {})
             .get("claims", {})
    )

    if method == "GET" and not task_id:
        return response(200, {"message": "list tasks"})

    if method == "GET" and task_id:
        return response(200, {"message": "get task", "task_id": task_id})

    if method == "POST" and not task_id:
        body = json.loads(event.get("body") or "{}")
        return response(201, {
            "message": "create task",
            "body": body,
            "user": jwt_claims.get("email") or jwt_claims.get("sub")
        })

    if method == "PATCH" and task_id:
        body = json.loads(event.get("body") or "{}")
        return response(200, {
            "message": "update task",
            "task_id": task_id,
            "body": body,
            "user": jwt_claims.get("email") or jwt_claims.get("sub")
        })

    if method == "DELETE" and task_id:
        return response(200, {
            "message": "delete task",
            "task_id": task_id,
            "user": jwt_claims.get("email") or jwt_claims.get("sub")
        })

    return response(405, {"message": "Method not allowed"})
    
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
    
def get_task (task_id: str):
    result = table.get_item(Key={"task_id": task_id})
    item = result.get("Item")
    
    if not item:
        return response(404, {"message": "Task not found", "task_id": task_id})

    audit_event(
        event_type="task_retrieved",
        payload={"task_id": task_id}
    )
    
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
    if status not in {"pending", "in_progress", "done"}:
        raise ValueError("Field 'status' must be one of: pending, in_progress, done")
    
    task_id = str(uuid.uuid4())
    ts = now_utc()
    
    actor_sub = claims.get("sub", "unknown")
    actor_username = claims.get("username") or claims.get("cognito:username") or claims.get("email", "unknown")
    
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
        allowed_fields["title"] = body["title"]
        
    if "status" in body:
        if body["status"] not in {"pending", "in_progress", "done"}:
            raise ValueError("Field 'status' must be one of: pending, in_progress, done")
        allowed_fields["status"] = body["status"]
        
    if not allowed_fields:
        raise ValueError("Nothing to update. Provide 'title' and/or 'status'")
    
    actor_sub = claims.get("sub", "unknown")
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

    try:
        result = table.update_item(
            Key={"task_id": task_id},
            UpdateExpression="SET " + ", ".join(set_parts),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ConditionExpression="attribute_exists(task_id)",
            ReturnValues="ALL_NEW"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return response(404, {"message": "Task not found", "task_id": task_id})
        raise

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
    actor_sub = claims.get("sub", "unknown")

    existing = table.get_item(Key={"task_id": task_id}).get("Item")
    if not existing:
        return response(404, {"message": "Task not found", "task_id": task_id})

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