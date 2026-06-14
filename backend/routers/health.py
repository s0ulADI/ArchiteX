from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def root() -> dict[str, object]:
    return {
        "name": "ArchiteX API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
