from fastapi import APIRouter, File, Form, UploadFile

from config import settings
from models.architecture import ParsedArchitecture
from services.arch_linter import lint_architecture
from services.vision_parser import VisionAPIError, parse_architecture_from_image
from utils.errors import api_error
from utils.image_utils import read_image_bytes
from utils.port_registry import assign_ports


router = APIRouter()


def _preview(parsed: ParsedArchitecture) -> dict[str, object]:
    return {
        "detected_services": [service.label for service in parsed.services],
        "connections": [
            f"{connection.from_id} -> {connection.to_id}" for connection in parsed.connections
        ],
        "confidence": parsed.confidence,
    }


@router.post("/parse")
async def parse_diagram(
    image: UploadFile = File(...),
    mode: str = Form(default="backend"),
) -> dict[str, object]:
    if mode not in {"backend", "frontend", "url"}:
        raise api_error(422, "Invalid mode", "mode must be one of backend, frontend, or url")

    try:
        image_bytes, mime_type = await read_image_bytes(image)
    except ValueError as exc:
        raise api_error(422, "Invalid image", str(exc)) from exc

    try:
        parsed = await parse_architecture_from_image(image_bytes, mime_type, mode=mode)
    except VisionAPIError as exc:
        raise api_error(502, "Vision API unavailable", str(exc)) from exc

    if parsed.confidence < 0.4:
        raise api_error(
            422,
            "Could not parse diagram - please upload a clearer image",
            f"Vision confidence was {parsed.confidence}",
        )

    if len(parsed.services) > settings.max_services:
        raise api_error(
            422,
            "Too many services detected",
            f"Detected {len(parsed.services)} services; MAX_SERVICES is {settings.max_services}",
        )

    parsed = parsed.model_copy(update={"services": assign_ports(parsed.services)})
    lint = lint_architecture(parsed)

    return {
        "parsed": parsed.model_dump(),
        "lint": lint.model_dump(),
        "understanding_preview": _preview(parsed),
    }
