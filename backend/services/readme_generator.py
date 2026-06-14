from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from models.architecture import ParsedArchitecture


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


def _env_table(architecture: ParsedArchitecture) -> dict[str, list[str]]:
    table: dict[str, list[str]] = {}
    for service in architecture.services:
        for env_var in service.env_vars:
            table.setdefault(env_var, []).append(service.id)
    return dict(sorted(table.items()))


def _assumptions(architecture: ParsedArchitecture) -> list[str]:
    assumptions = [
        "Service internals are scaffolded from templates and should be completed with domain logic.",
        "Any endpoints not written on the diagram were inferred from service names and common conventions.",
        "Database credentials in docker-compose are local development defaults.",
    ]
    if architecture.confidence < 0.8:
        assumptions.append("The diagram confidence was below 0.8, so generated boundaries should be reviewed carefully.")
    return assumptions


def generate_readme(architecture: ParsedArchitecture, files: dict[str, str]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("README.md.j2")
    return template.render(
        project_name="ArchiteX Generated Repository",
        services=architecture.services,
        connections=architecture.connections,
        env_table=_env_table(architecture),
        assumptions=_assumptions(architecture),
        files=files,
    )
