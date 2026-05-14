from datetime import datetime, timezone
from typing import Any


def build_response(status: bool, message: str, data: Any = None) -> dict:
    return {
        "status": status,
        "message": message,
        "data": data,
        "time_stamp": datetime.now(timezone.utc).isoformat(),
    }
