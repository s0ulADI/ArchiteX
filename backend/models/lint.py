from pydantic import BaseModel, Field


class ArchWarning(BaseModel):
    severity: str
    message: str
    affected_services: list[str] = Field(default_factory=list)
    fix: str


class ArchLintResult(BaseModel):
    score: int
    warnings: list[ArchWarning] = Field(default_factory=list)
    passed_checks: list[str] = Field(default_factory=list)
