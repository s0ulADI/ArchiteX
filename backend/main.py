from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import delivery, frontend_gen, generate, health, parse, url_scrape

app = FastAPI(title="ArchiteX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and {"error", "detail"} <= set(exc.detail):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": "Request failed", "detail": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "Validation error", "detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})


app.include_router(health.router)
app.include_router(parse.router)
app.include_router(generate.router)
app.include_router(frontend_gen.router, prefix="/frontend")
app.include_router(url_scrape.router, prefix="/url")
app.include_router(delivery.router, prefix="/deliver")
