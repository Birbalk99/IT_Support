"""
IT Help Desk Backend - Main Application
FastAPI application with multi-level security for banking sector
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from core.security.middleware import SecurityMiddleware
from core.logging.logger import app_logger, cleanup_old_logs
from api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    app_logger.info("Application starting up...", method="startup")
    cleanup_old_logs()
    yield
    # Shutdown
    app_logger.info("Application shutting down...", method="shutdown")


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="IT Help Desk With AI",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS Middleware - Configure allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Custom Security Middleware
app.add_middleware(SecurityMiddleware)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions"""
    app_logger.error(
        f"Unhandled exception: {str(exc)}", 
        method=request.method,
        extra_info={"path": request.url.path}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "IT Help Desk Backend"}


# Include API routes - /api prefix yaha set hai
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
