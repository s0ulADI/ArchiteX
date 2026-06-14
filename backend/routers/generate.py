import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from config import settings
from models.architecture import ParsedArchitecture
from services.code_generator import generate_files
from services.planner import create_file_tree_plan
from services.readme_generator import generate_readme
from services.repository_store import put_repository
from services.verifier import verify_generated_files
from utils.port_registry import assign_ports
from utils.sse import sse_event


router = APIRouter()


async def _repo_stream(architecture: ParsedArchitecture):
    try:
        if len(architecture.services) > settings.max_services:
            yield sse_event(
                "error",
                f"Detected {len(architecture.services)} services; MAX_SERVICES is {settings.max_services}",
                done=True,
            )
            return

        architecture = architecture.model_copy(update={"services": assign_ports(architecture.services)})

        yield sse_event("reading_diagram", "Reading diagram...", done=False)
        await asyncio.sleep(0)

        yield sse_event(
            "detected_services",
            f"Detected {len(architecture.services)} services...",
            done=False,
        )
        await asyncio.sleep(0)

        yield sse_event("creating_contracts", "Creating API contracts...", done=False)
        plan = create_file_tree_plan(architecture)
        await asyncio.sleep(0)

        for service in architecture.services:
            yield sse_event(
                "generating_code",
                f"Generating {service.id}...",
                done=False,
                service=service.id,
            )
            await asyncio.sleep(0)

        files = generate_files(plan, architecture)

        yield sse_event("generating_dockerfiles", "Generating Dockerfiles...", done=False)
        await asyncio.sleep(0)

        yield sse_event("generating_compose", "Building docker-compose.yml...", done=False)
        await asyncio.sleep(0)

        yield sse_event("generating_readme", "Generating README...", done=False)
        files["README.md"] = generate_readme(architecture, files)
        await asyncio.sleep(0)

        yield sse_event("verifying", "Validating service ports...", done=False)
        verification = verify_generated_files(files, architecture)
        if verification.failed:
            yield sse_event(
                "error",
                "Generated repository failed verification: " + "; ".join(verification.failed),
                done=True,
            )
            return

        token = put_repository(files, metadata={"kind": "backend", "verification": verification.model_dump()})
        yield sse_event("complete", "Repository ready", done=True, download_token=token)
    except Exception as exc:
        yield sse_event("error", str(exc), done=True)


@router.post("/generate")
async def generate_repository(architecture: ParsedArchitecture) -> StreamingResponse:
    return StreamingResponse(_repo_stream(architecture), media_type="text/event-stream")
