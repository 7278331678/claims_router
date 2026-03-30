import json
import logging
import os
from typing import Any, Dict, Optional, Tuple

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
ENV = os.getenv("ENV", "dev")

LAMBDA_CLIENT = boto3.client("lambda", config=Config(read_timeout=10, connect_timeout=3, retries={"max_attempts": 2}))
BEDROCK_CLIENT = boto3.client(
    "bedrock-runtime",
    config=Config(read_timeout=15, connect_timeout=3, retries={"max_attempts": 3, "mode": "standard"}),
)

TARGETS = {
    "claim": {
        "public": os.getenv("TARGET_CLAIM_PUBLIC", ""),
        "private": os.getenv("TARGET_CLAIM_PRIVATE", ""),
    },
    "claim_summary": {
        "public": os.getenv("TARGET_CLAIM_SUMMARY_PUBLIC", ""),
        "private": os.getenv("TARGET_CLAIM_SUMMARY_PRIVATE", ""),
    },
    "create": {
        "public": os.getenv("TARGET_CREATE_PUBLIC", ""),
        "private": os.getenv("TARGET_CREATE_PRIVATE", ""),
    },
    "update": {
        "public": os.getenv("TARGET_UPDATE_PUBLIC", ""),
        "private": os.getenv("TARGET_UPDATE_PRIVATE", ""),
    },
}


def _json_log(level: str, message: str, **fields: Any) -> None:
    log_record = {"level": level, "message": message, "env": ENV, **fields}
    getattr(LOGGER, level.lower(), LOGGER.info)(json.dumps(log_record, default=str))


def _parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body")
    if not body:
        return {}
    if event.get("isBase64Encoded"):
        import base64

        body = base64.b64decode(body).decode("utf-8")
    if isinstance(body, dict):
        return body
    try:
        return json.loads(body)
    except (TypeError, json.JSONDecodeError):
        return {"raw_body": str(body)}


def _normalize_endpoint_type(headers: Dict[str, Any], body: Dict[str, Any]) -> str:
    endpoint_type = (
        str(headers.get("x-endpoint-type") or body.get("endpoint_type") or "public")
        .strip()
        .lower()
    )
    return "private" if endpoint_type == "private" else "public"


def _rule_based_route(method: str, body: Dict[str, Any], path: str) -> Optional[str]:
    action = str(body.get("action") or "").lower()
    api_type = str(body.get("api_type") or "").lower()
    if method == "GET":
        return None
    if method == "POST":
        if api_type in ("claim", "claim_api"):
            return "claim"
        if api_type in ("claim_summary", "summary", "claim-summary"):
            return "claim_summary"
        if "create" in action or "create" in path:
            return "create"
        if "update" in action or "update" in path:
            return "update"
    return None


def _route_get_request(query_params: Dict[str, Any], body: Dict[str, Any], headers: Dict[str, Any]) -> Optional[str]:
    api_type = str(
        query_params.get("api_type")
        or headers.get("x-claim-api")
        or body.get("api_type")
        or ""
    ).strip().lower()
    if api_type in ("claim", "claim_api"):
        return "claim"
    if api_type in ("claim_summary", "summary", "claim-summary"):
        return "claim_summary"

    # Heuristic fallback when explicit api_type is not provided.
    if "mostrecentindicator" in {str(k).lower() for k in query_params.keys()}:
        return "claim"
    return "claim_summary"


def _ask_bedrock(
    method: str, path: str, headers: Dict[str, Any], body: Dict[str, Any], query_params: Dict[str, Any]
) -> Optional[Dict[str, str]]:
    prompt = {
        "task": "Route API requests to one of: claim, claim_summary, create, update and endpoint_type public/private.",
        "routing_rules": [
            "GET for claim summary should map to target=claim_summary.",
            "GET for claim detail should map to target=claim.",
            "POST for creating resources should map to target=create.",
            "POST for changing existing resources should map to target=update.",
            "endpoint_type comes from x-endpoint-type header when present, otherwise infer from payload, else public.",
        ],
        "request": {
            "method": method,
            "path": path,
            "headers": headers,
            "body": body,
            "query_params": query_params,
        },
        "response_format": {
            "type": "json_only",
            "schema": {"target": "claim|claim_summary|create|update", "endpoint_type": "public|private"},
        },
    }

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 120,
        "temperature": 0,
        "messages": [{"role": "user", "content": json.dumps(prompt)}],
    }

    try:
        response = BEDROCK_CLIENT.invoke_model(modelId=BEDROCK_MODEL_ID, body=json.dumps(payload))
        raw = response["body"].read().decode("utf-8")
        data = json.loads(raw)
        text = data["content"][0]["text"]
        decision = json.loads(text)
        target = str(decision.get("target", "")).lower()
        endpoint = str(decision.get("endpoint_type", "public")).lower()
        if target in TARGETS and endpoint in ("public", "private"):
            return {"target": target, "endpoint_type": endpoint}
        return None
    except (ClientError, BotoCoreError, KeyError, ValueError, json.JSONDecodeError) as exc:
        _json_log("ERROR", "Bedrock routing failed", error=str(exc))
        return None


def _fallback_route(method: str, endpoint_type: str) -> Tuple[str, str]:
    if method == "GET":
        return "claim_summary", endpoint_type
    return "create", endpoint_type


def _invoke_target(function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = LAMBDA_CLIENT.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    status_code = response.get("StatusCode", 500)
    response_payload_raw = response["Payload"].read().decode("utf-8")
    try:
        response_payload = json.loads(response_payload_raw) if response_payload_raw else {}
    except json.JSONDecodeError:
        response_payload = {"raw_response": response_payload_raw}
    return {"status_code": status_code, "payload": response_payload}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method = str(event.get("requestContext", {}).get("http", {}).get("method", "GET")).upper()
    headers = {str(k).lower(): v for k, v in (event.get("headers") or {}).items()}
    body = _parse_body(event)
    path = str(event.get("rawPath", "/router"))
    query_params = event.get("queryStringParameters") or {}
    endpoint_type = _normalize_endpoint_type(headers, body)

    _json_log("INFO", "Incoming request", method=method, path=path, endpoint_type=endpoint_type)

    if method == "GET":
        target = _route_get_request(query_params, body, headers)
    else:
        target = _rule_based_route(method, body, path)
    if target:
        decision_source = "rule"
    else:
        bedrock_decision = _ask_bedrock(method, path, headers, body, query_params)
        if bedrock_decision:
            target = bedrock_decision["target"]
            endpoint_type = bedrock_decision["endpoint_type"]
            decision_source = "bedrock"
        else:
            target, endpoint_type = _fallback_route(method, endpoint_type)
            decision_source = "fallback"

    function_name = TARGETS.get(target, {}).get(endpoint_type)
    if not function_name:
        _json_log("ERROR", "No lambda mapping found", target=target, endpoint_type=endpoint_type)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Routing configuration error"}),
        }

    _json_log(
        "INFO",
        "Routing decision",
        decision_source=decision_source,
        target=target,
        endpoint_type=endpoint_type,
        function_name=function_name,
    )

    try:
        invoke_payload = {
            "request_meta": {
                "source_method": method,
                "source_path": path,
                "endpoint_type": endpoint_type,
                "decision_source": decision_source,
            },
            "headers": headers,
            "body": body,
            "query_params": query_params,
        }
        result = _invoke_target(function_name, invoke_payload)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "routed_to": function_name,
                    "target": target,
                    "endpoint_type": endpoint_type,
                    "result": result["payload"],
                }
            ),
        }
    except (ClientError, BotoCoreError, ValueError) as exc:
        _json_log("ERROR", "Target lambda invocation failed", error=str(exc), function_name=function_name)
        return {
            "statusCode": 502,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to process routed request"}),
        }
