import base64
import json
from typing import Any


def get_jwt_payload(json_web_token: str) -> dict[str, Any]:
    jwt_header_part, jwt_payload_part, jwt_signature_part = json_web_token.split(".")
    # Add padding to the payload if needed
    jwt_payload_part += "=" * divmod(len(jwt_payload_part), 4)[1]
    payload_json: str = base64.urlsafe_b64decode(jwt_payload_part).decode()
    return json.loads(payload_json)
