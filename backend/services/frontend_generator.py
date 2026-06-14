import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from models.architecture import ParsedArchitecture


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


def _sections(architecture: ParsedArchitecture) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    for service in architecture.services:
        if service.type == "frontend" and service.components:
            for index, component in enumerate(service.components, start=1):
                sections.append(
                    {
                        "id": str(component.get("id") or f"{service.id}-{index}"),
                        "type": str(component.get("type") or "component"),
                        "label": str(component.get("label") or component.get("name") or f"Component {index}"),
                        "description": str(component.get("description") or "Generated from the parsed UI sketch."),
                    }
                )
        elif service.type == "frontend":
            sections.append(
                {
                    "id": service.id,
                    "type": "frontend",
                    "label": service.label,
                    "description": service.raw_description if hasattr(service, "raw_description") else "Generated frontend shell.",
                }
            )

    if not sections:
        sections.append(
            {
                "id": "app-shell",
                "type": "application",
                "label": "Application Shell",
                "description": architecture.raw_description or "Generated from the parsed architecture.",
            }
        )
    return sections


def generate_frontend_files(architecture: ParsedArchitecture) -> dict[str, str]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    sections = _sections(architecture)
    package_name = "architectx-generated-frontend"
    return {
        "package.json": env.get_template("frontend/package.json.j2").render(package_name=package_name),
        "src/App.jsx": env.get_template("frontend/App.jsx.j2").render(
            sections_json=json.dumps(sections, indent=2)
        ),
        "src/components/GeneratedComponent.jsx": env.get_template("frontend/component.jsx.j2").render(),
    }
