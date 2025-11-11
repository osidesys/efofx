"""Main FastAPI application for EFOFX Estimate Service."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.chat import router as chat_router
from app.core.config import settings
from app.observability.logging import setup_logging
from app.observability.metrics import setup_metrics

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging."""

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        start_time = asyncio.get_event_loop().time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling."""

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                "Unhandled exception",
                method=request.method,
                url=str(request.url),
                error=str(exc),
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "trace_id": getattr(request.state, "trace_id", "unknown"),
                },
            )


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Application lifespan manager."""
    logger.info("Starting EFOFX Estimate Service")
    
    # Setup metrics
    setup_metrics()
    
    yield
    
    logger.info("Shutting down EFOFX Estimate Service")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="EFOFX Estimate Service",
        description="Monolithic FastAPI service that powers chat-driven estimates",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routes
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
    
    # Add Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": "efofx-estimate"}
    
    return app


# Create the application instance
app = create_app()


def main() -> None:
    """Main entry point for running the application."""
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
