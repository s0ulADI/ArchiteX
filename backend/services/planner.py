from models.architecture import ParsedArchitecture, ServiceNode
from models.plan import FileTreePlan, ServicePlan


SERVICE_TEMPLATE_FILES = {
    "express_rest": ["index.js", "routes.js", "package.json", "Dockerfile"],
    "fastapi_service": ["main.py", "routes.py", "requirements.txt", "Dockerfile"],
    "postgres_connector": ["init.sql"],
    "redis_connector": ["redis.conf"],
}


def _template_type_for(service: ServiceNode) -> str:
    if service.type == "database":
        return "postgres_connector"
    if service.type == "cache":
        return "redis_connector"
    if service.language == "python":
        return "fastapi_service"
    return "express_rest"


def create_file_tree_plan(architecture: ParsedArchitecture) -> FileTreePlan:
    service_plans = []
    for service in architecture.services:
        template_type = _template_type_for(service)
        files = [f"{service.id}/{name}" for name in SERVICE_TEMPLATE_FILES[template_type]]
        service_plans.append(ServicePlan(service=service, template_type=template_type, files=files))

    return FileTreePlan(
        services=service_plans,
        top_level_files=["docker-compose.yml", "README.md", ".env.example"],
    )
