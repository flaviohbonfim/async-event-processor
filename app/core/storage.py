import redis
from typing import Dict, Optional
import json
from app.core.config import settings

# Conexão com Redis usando configurações do ambiente
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def set_notification(trace_id: str, data: Dict[str, any]):
    r.set(trace_id, json.dumps(data))

def get_notification(trace_id: str) -> Optional[Dict[str, any]]:
    stored = r.get(trace_id)
    if stored:
        return json.loads(stored)
    return None

def clear_storage():
    r.flushdb()

def set_status(trace_id: str, status: str):
    data = get_notification(trace_id)
    if data:
        data['status'] = status
        set_notification(trace_id, data)
