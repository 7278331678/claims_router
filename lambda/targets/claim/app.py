import json
import os


def handler(event, _context):
    endpoint_type = os.getenv("ENDPOINT_TYPE", "public")
    env = os.getenv("ENV", "dev")
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "api": "claim",
                "endpoint_type": endpoint_type,
                "env": env,
                "query_params": event.get("query_params", {}),
                "echo": event,
            }
        ),
    }
