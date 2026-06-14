from models.architecture import ServiceNode


STANDARD_PORTS = {
    "postgres": 5432,
    "postgresql": 5432,
    "redis": 6379,
    "mysql": 3306,
}


def _standard_port_for(service: ServiceNode) -> int | None:
    haystack = f"{service.id} {service.label} {service.type}".lower()
    for marker, port in STANDARD_PORTS.items():
        if marker in haystack:
            return port
    return None


def assign_ports(services: list[ServiceNode], start: int = 8001) -> list[ServiceNode]:
    next_port = start
    assigned: list[ServiceNode] = []

    for service in services:
        update: dict[str, int] = {}
        standard_port = _standard_port_for(service)
        if standard_port is not None:
            update["port"] = standard_port
        elif service.port is None:
            update["port"] = next_port
            next_port += 1
        else:
            next_port = max(next_port, service.port + 1)

        assigned.append(service.model_copy(update=update))

    return assigned
