"""
FastAPI Main Application - Executive Analytics Assistant API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .routes import router
from .connections import router as connections_router
from .schemas import ErrorResponse
from ..utils.logging import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    console_output=True
)
logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("application_startup", version="0.1.0")
    yield
    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title="Executive Analytics Assistant API",
    description="Multi-agent system for conversational SQL analytics with LangGraph",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration (integrated, no separate middleware file)
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("cors_configured", allowed_origins=allowed_origins)

# Include routers
app.include_router(router)
app.include_router(connections_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        ).model_dump()
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Executive Analytics Assistant API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        client_host=request.client.host if request.client else "unknown"
    )
    
    response = await call_next(request)
    
    logger.info(
        "http_response",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info("starting_server", host=host, port=port)
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
