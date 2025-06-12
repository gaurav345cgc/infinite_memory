from datetime import datetime

def current_utc_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"
