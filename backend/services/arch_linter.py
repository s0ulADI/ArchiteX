from collections import defaultdict

from models.architecture import ParsedArchitecture
from models.lint import ArchLintResult, ArchWarning


SERVICE_TYPES = {"rest_api", "frontend", "worker"}


def _build_warning(severity: str, message: str, affected_services: list[str], fix: str) -> ArchWarning:
    return ArchWarning(
        severity=severity,
        message=message,
        affected_services=affected_services,
        fix=fix,
    )


def _find_cycles(architecture: ParsedArchitecture) -> list[list[str]]:
    services = {service.id: service for service in architecture.services if service.type in SERVICE_TYPES}
    graph: dict[str, list[str]] = defaultdict(list)
    for connection in architecture.connections:
        if connection.from_id in services and connection.to_id in services:
            graph[connection.from_id].append(connection.to_id)

    cycles: list[list[str]] = []
    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        visited.add(node)
        active.add(node)
        stack.append(node)
        for target in graph.get(node, []):
            if target not in visited:
                visit(target)
            elif target in active:
                start = stack.index(target)
                cycles.append(stack[start:] + [target])
        stack.pop()
        active.remove(node)

    for service_id in services:
        if service_id not in visited:
            visit(service_id)

    return cycles


def lint_architecture(architecture: ParsedArchitecture) -> ArchLintResult:
    warnings: list[ArchWarning] = []
    passed_checks: list[str] = []
    services = {service.id: service for service in architecture.services}

    direct_db_errors = []
    db_targets: dict[str, list[str]] = defaultdict(list)
    connected_ids: set[str] = set()

    for connection in architecture.connections:
        source = services.get(connection.from_id)
        target = services.get(connection.to_id)
        if source:
            connected_ids.add(source.id)
        if target:
            connected_ids.add(target.id)
        if source and target and target.type == "database":
            db_targets[target.id].append(source.id)
            if source.type not in {"rest_api", "worker"}:
                direct_db_errors.append((source.id, target.id))

    if direct_db_errors:
        for source_id, target_id in direct_db_errors:
            warnings.append(
                _build_warning(
                    "error",
                    f"{source_id} connects directly to database {target_id}.",
                    [source_id, target_id],
                    "Route database access through an API or worker service.",
                )
            )
    else:
        passed_checks.append("No direct database connections from non-service nodes")

    cycles = _find_cycles(architecture)
    if cycles:
        for cycle in cycles:
            warnings.append(
                _build_warning(
                    "warning",
                    "Circular dependency detected: " + " -> ".join(cycle),
                    cycle,
                    "Break the cycle with an async queue, event bus, or one-way API contract.",
                )
            )
    else:
        passed_checks.append("No circular dependencies detected")

    isolated = [service.id for service in architecture.services if service.id not in connected_ids]
    if isolated:
        warnings.append(
            _build_warning(
                "warning",
                "One or more services have no inbound or outbound connections.",
                isolated,
                "Connect isolated services or remove them from the generated architecture.",
            )
        )
    else:
        passed_checks.append("All services participate in at least one connection")

    multi_db = {db_id: sources for db_id, sources in db_targets.items() if len(set(sources)) > 1}
    if multi_db:
        for db_id, sources in multi_db.items():
            warnings.append(
                _build_warning(
                    "warning",
                    f"Multiple services connect directly to database {db_id}.",
                    [db_id, *sorted(set(sources))],
                    "Prefer a single owning service for each database boundary.",
                )
            )
    else:
        passed_checks.append("No database has multiple direct service owners")

    rest_without_health = [
        service.id
        for service in architecture.services
        if service.type == "rest_api" and "/health" not in service.endpoints
    ]
    if rest_without_health:
        warnings.append(
            _build_warning(
                "suggestion",
                "REST API services should expose a /health endpoint.",
                rest_without_health,
                "Add /health to each REST API service.",
            )
        )
    else:
        passed_checks.append("REST API services include health endpoints")

    no_env = [service.id for service in architecture.services if service.type in SERVICE_TYPES and not service.env_vars]
    if no_env:
        warnings.append(
            _build_warning(
                "suggestion",
                "Some services do not define environment variables.",
                no_env,
                "Confirm whether secrets, connection strings, or feature flags are required.",
            )
        )
    else:
        passed_checks.append("All runnable services define environment variables")

    penalty = 0
    for warning in warnings:
        if warning.severity == "error":
            penalty += 20
        elif warning.severity == "warning":
            penalty += 10
        elif warning.severity == "suggestion":
            penalty += 3

    return ArchLintResult(score=max(0, 100 - penalty), warnings=warnings, passed_checks=passed_checks)
