"""FastAPI application factory and main setup."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.services.proxy import proxy_service
from app.routers import auth, providers, projects, sessions, proxy as proxy_router

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("app_startup", message="Starting Unified AI Agents Platform")
    yield
    # Shutdown
    await proxy_service.close()
    logger.info("app_shutdown", message="Shutting down Unified AI Agents Platform")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Unified platform for AI coding agents with multi-provider proxy layer",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
    app.include_router(providers.router, prefix=f"{settings.API_V1_PREFIX}/providers", tags=["Providers"])
    app.include_router(projects.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["Projects"])
    app.include_router(sessions.router, prefix=f"{settings.API_V1_PREFIX}/sessions", tags=["Sessions"])
    app.include_router(proxy_router.router, prefix=f"{settings.API_V1_PREFIX}/proxy", tags=["Proxy"])
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}
    
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "docs": "/docs",
        }
    
    return app


# Create app instance
app = create_app()
