from typing import Any

from pydantic import BaseModel, Field


class ServiceNode(BaseModel):
    id: str
    label: str
    type: str
    language: str | None = None
    port: int | None = None
    env_vars: list[str] = Field(default_factory=list)
    endpoints: list[str] = Field(default_factory=list)
    components: list[dict[str, Any]] = Field(default_factory=list)


class Connection(BaseModel):
    from_id: str
    to_id: str
    protocol: str | None = "http"


class ParsedArchitecture(BaseModel):
    services: list[ServiceNode]
    connections: list[Connection]
    raw_description: str
    confidence: float
