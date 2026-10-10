"""FastAPI Application factory with exception handling and CORS configuration."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.constants import API_V1_PREFIX
from app.core.crops import UnsupportedCropError
from app.routers import alerts, diagnosis, farms, health, irrigation, telemetry, yield_


def create_app() -> FastAPI:
    """Initialize and configure FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    application.include_router(health.router, prefix=API_V1_PREFIX)
    application.include_router(farms.router, prefix=API_V1_PREFIX)
    application.include_router(telemetry.router, prefix=API_V1_PREFIX)
    application.include_router(diagnosis.router, prefix=API_V1_PREFIX)
    application.include_router(irrigation.router, prefix=API_V1_PREFIX)
    application.include_router(yield_.router, prefix=API_V1_PREFIX)
    application.include_router(alerts.router, prefix=API_V1_PREFIX)

    register_exception_handlers(application)

    return application


def register_exception_handlers(application: FastAPI) -> None:
    """Attach structured error handlers to maintain standard envelope."""

    @application.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        code = "HTTP_ERROR"
        message = str(exc.detail)
        if isinstance(exc.detail, dict):
            code = exc.detail.get("code", code)
            message = exc.detail.get("message", message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "data": None, "error": {"code": code, "message": message}},
        )

    @application.exception_handler(UnsupportedCropError)
    async def unsupported_crop_handler(_: Request, exc: UnsupportedCropError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "data": None, "error": {"code": exc.code, "message": str(exc)}},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = {str(err["loc"][-1]): err["msg"] for err in exc.errors()}
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters or payload.",
                    "details": details,
                },
            },
        )


app = create_app()
