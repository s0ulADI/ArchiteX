import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.architecture import ParsedArchitecture
from services.frontend_generator import generate_frontend_files
from services.repository_store import put_repository
from utils.sse import sse_event


router = APIRouter()


async def _frontend_stream(architecture: ParsedArchitecture):
    try:
        yield sse_event("reading_diagram", "Reading UI structure...", done=False)
        await asyncio.sleep(0)

        frontend_services = [service for service in architecture.services if service.type == "frontend"]
        yield sse_event(
            "detected_services",
            f"Detected {len(frontend_services)} frontend services...",
            done=False,
        )
        await asyncio.sleep(0)

        yield sse_event("creating_contracts", "Creating component contracts...", done=False)
        await asyncio.sleep(0)

        for service in frontend_services or architecture.services:
            yield sse_event(
                "generating_code",
                f"Generating {service.id}...",
                service=service.id,
                done=False,
            )
            await asyncio.sleep(0)

        yield sse_event("generating_dockerfiles", "Generating frontend package files...", done=False)
        files = generate_frontend_files(architecture)
        await asyncio.sleep(0)

        yield sse_event("generating_compose", "Skipping docker-compose for frontend bundle...", done=False)
        await asyncio.sleep(0)

        yield sse_event("generating_readme", "Generating frontend README...", done=False)
        files["README.md"] = (
            "# ArchiteX Generated Frontend\n\n"
            "Generated from parsed UI JSON. Run with `npm install` and `npm run dev`.\n"
        )
        await asyncio.sleep(0)

        yield sse_event("verifying", "Validating frontend file paths...", done=False)
        if any("\\" in path for path in files):
            yield sse_event("error", "Generated frontend paths must use forward slashes", done=True)
            return

        token = put_repository(files, metadata={"kind": "frontend"})
        yield sse_event("complete", "Repository ready", done=True, download_token=token)
    except Exception as exc:
        yield sse_event("error", str(exc), done=True)


@router.post("/generate")
async def generate_frontend(architecture: ParsedArchitecture) -> StreamingResponse:
    return StreamingResponse(_frontend_stream(architecture), media_type="text/event-stream")
