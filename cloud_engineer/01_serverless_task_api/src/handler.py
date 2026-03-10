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

TASKS_TABLE_NAME = os.environ["TASKS_TABLE_NAME"]  # Se puede mejorar usando AWS Secrets Manager 
AUDIT_BUCKET_NAME = os.environ["AUDIT_BUCKET_NAME"]

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
    logger.info("Incoming event: %s", json.dumps(event))
    
    method = get_method(event)
    task_id = get_path_param(event, "task_id")
    
    try:
        if method == "GET" and task_id:
            return get_task(task_id)
        
        if method == "GET":
            return list_task()
        
        if method == "POST": 
            return create_task(event)
        
        if method == "PATCH" and task_id:
            return update_task(event, task_id)
        
        if method == "DELETE" and task_id:
            return delete_task(event, task_id)
        
        return response(405, {"message": "Method not allowed"})
    
    except PermissionError as e:
        logger.warning("Unauthorized request: %s", str(e))
        return response(401, {"message": str(e)})
    
    except ClientError as e:
        logger.exception("AWS client error")
        return response(500, {"message": "Internal AWS error", "error": str(e)})
    
    except ValueError as e:
        logger.warning("Bad request: %s", str(e))
        return response(400, {"message": str(e)})
    
    except Exception as e:
        logger.exception("Unhandled exception")
        return response(500, {"message": "Unexpected internal error", "error": str(e)})