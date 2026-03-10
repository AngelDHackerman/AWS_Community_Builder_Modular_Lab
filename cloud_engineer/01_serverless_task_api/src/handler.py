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