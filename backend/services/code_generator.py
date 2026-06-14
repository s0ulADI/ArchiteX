from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from models.architecture import ParsedArchitecture
from models.plan import FileTreePlan, ServicePlan


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _template_path(plan: ServicePlan, file_name: str) -> str:
    if plan.template_type == "postgres_connector":
        return "services/postgres_connector/init.sql.j2"
    if plan.template_type == "redis_connector":
        return "services/redis_connector/redis_config.j2"
    return f"services/{plan.template_type}/{file_name}.j2"


def _env_vars(architecture: ParsedArchitecture) -> list[str]:
    return sorted({env_var for service in architecture.services for env_var in service.env_vars})


def generate_files(plan: FileTreePlan, architecture: ParsedArchitecture) -> dict[str, str]:
    env = _environment()
    files: dict[str, str] = {}

    for service_plan in plan.services:
        for output_path in service_plan.files:
            file_name = output_path.split("/")[-1]
            template = env.get_template(_template_path(service_plan, file_name))
            files[output_path] = template.render(
                service=service_plan.service,
                connections=architecture.connections,
                all_services=architecture.services,
            )

    files["docker-compose.yml"] = env.get_template("docker-compose.yml.j2").render(
        all_services=architecture.services,
        connections=architecture.connections,
    )
    files[".env.example"] = env.get_template("env.example.j2").render(env_vars=_env_vars(architecture))
    return files
