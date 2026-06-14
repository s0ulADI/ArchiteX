import re

from models.architecture import ParsedArchitecture
from models.plan import VerificationResult


SERVICE_BLOCK_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$", re.MULTILINE)


def _dockerfile_env_vars(content: str) -> set[str]:
    env_vars: set[str] = set()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("ENV "):
            parts = stripped.split(maxsplit=2)
            if len(parts) >= 2:
                env_vars.add(parts[1].split("=")[0])
    return env_vars


def verify_generated_files(files: dict[str, str], architecture: ParsedArchitecture) -> VerificationResult:
    passed: list[str] = []
    failed: list[str] = []
    compose = files.get("docker-compose.yml", "")
    env_example = files.get(".env.example", "")

    for service in architecture.services:
        if service.port is None:
            failed.append(f"{service.id} has no assigned port")
            continue
        if service.type == "database":
            expected = f'"{service.port}:5432"'
        elif service.type == "cache":
            expected = f'"{service.port}:6379"'
        else:
            expected = f'"{service.port}:{service.port}"'
        if expected in compose:
            passed.append(f"{service.id} port mapping matches {expected}")
        else:
            failed.append(f"{service.id} missing expected docker-compose port mapping {expected}")

    declared_env = {
        line.split("=", 1)[0].strip()
        for line in env_example.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    docker_env: set[str] = set()
    for path, content in files.items():
        if path.endswith("/Dockerfile"):
            docker_env.update(_dockerfile_env_vars(content))

    missing_env = sorted(var for var in docker_env if var not in declared_env)
    if missing_env:
        failed.append("Dockerfile ENV variables missing from .env.example: " + ", ".join(missing_env))
    else:
        passed.append("Dockerfile ENV variables are present in .env.example")

    service_blocks = set(SERVICE_BLOCK_RE.findall(compose))
    for connection in architecture.connections:
        if connection.to_id not in service_blocks:
            failed.append(f"{connection.from_id} depends on missing service block {connection.to_id}")
        else:
            passed.append(f"{connection.to_id} service block exists for connection from {connection.from_id}")

    for path in files:
        if "\\" in path:
            failed.append(f"{path} uses backslashes")
    if not any("\\" in path for path in files):
        passed.append("All generated file paths use forward slashes")

    return VerificationResult(passed=passed, failed=failed)
