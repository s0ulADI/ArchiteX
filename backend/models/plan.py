from pydantic import BaseModel, Field

from models.architecture import ServiceNode


class ServicePlan(BaseModel):
    service: ServiceNode
    template_type: str
    files: list[str] = Field(default_factory=list)


class FileTreePlan(BaseModel):
    services: list[ServicePlan] = Field(default_factory=list)
    top_level_files: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    passed: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failed
