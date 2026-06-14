import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from config import settings


@dataclass
class StoredRepository:
    files: dict[str, str]
    created_at: float
    metadata: dict[str, Any]


_repositories: dict[str, StoredRepository] = {}


def put_repository(files: dict[str, str], metadata: dict[str, Any] | None = None) -> str:
    token = str(uuid4())
    _repositories[token] = StoredRepository(files=files, created_at=time.time(), metadata=metadata or {})
    return token


def get_repository(download_token: str) -> StoredRepository | None:
    record = _repositories.get(download_token)
    if record is None:
        return None
    if time.time() - record.created_at > settings.repo_ttl_seconds:
        _repositories.pop(download_token, None)
        return None
    return record


def purge_expired() -> None:
    now = time.time()
    expired = [
        token
        for token, record in _repositories.items()
        if now - record.created_at > settings.repo_ttl_seconds
    ]
    for token in expired:
        _repositories.pop(token, None)
