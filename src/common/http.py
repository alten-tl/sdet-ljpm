"""HTTP response, request-body, and input-validation helpers."""

import json
from datetime import datetime
from uuid import UUID


def response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,OPTIONS",
        },
        "body": json.dumps(payload, default=str),
    }


def read_json_body(event):
    body = event.get("body")
    if body is None or body == "":
        return {}
    if isinstance(body, dict):
        return body
    try:
        return json.loads(body)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("Request body must contain valid JSON.") from exc


def is_valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def is_valid_time(value):
    if not isinstance(value, str):
        return False
    for time_format in ("%H:%M", "%H:%M:%S"):
        try:
            datetime.strptime(value, time_format)
            return True
        except ValueError:
            continue
    return False


def is_valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def database_error_response(exc):
    """Translate the active-slot unique index into an HTTP 409 response."""
    print(f"Database operation failed: {exc}")
    if "uq_appointments_active_slot" in str(exc):
        return response(409, {
            "message": "The selected date and time are already reserved."
        })
    return response(500, {"message": "An internal database error occurred."})
