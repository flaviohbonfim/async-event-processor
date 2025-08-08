from threading import Lock
from typing import Dict, Optional

notification_storage: Dict[str, Dict[str, any]] = {}
lock = Lock()

def set_notification(trace_id: str, data: Dict[str, any]):
    with lock:
        notification_storage[trace_id] = data

def get_notification(trace_id: str) -> Optional[Dict[str, any]]:
    with lock:
        return notification_storage.get(trace_id)

def clear_storage():
    with lock:
        notification_storage.clear()

def set_status(trace_id: str, status: str):
    with lock:
        if trace_id in notification_storage:
            notification_storage[trace_id]['status'] = status