import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import endpoints as api_endpoints
from app.containers import ApplicationContainer
from app.exceptions import ResourceNotFound


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(container: ApplicationContainer) -> FastAPI:
    container.wire(packages=[api_endpoints])
    settings = container.settings()
    
    app = FastAPI(
        title="Story Tailer",
        description="API for generating stories from images and converting them to audio",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.container = container  # type: ignore
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_endpoints.router)

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Resource not found",
                "details": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception handler caught: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "details": str(exc) if settings.debug else None,
            },
        )
    
    return app


if __name__ == "__main__":
    container = ApplicationContainer()
    settings = container.settings()
    app = create_app(container)
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
    )
