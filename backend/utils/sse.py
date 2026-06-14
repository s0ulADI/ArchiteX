import json
from typing import Any


def sse_event(step: str, message: str, done: bool = False, **kwargs: Any) -> str:
    payload = {"step": step, "message": message, "done": done, **kwargs}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
