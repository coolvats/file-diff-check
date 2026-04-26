"""
File Duplicate Checker API
Main application entry point using FastAPI
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import os

from app.routes import file_routes, health_routes
from app.utils.logger import setup_logger
from app.config import settings

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="File Duplicate Checker API",
    description="API for checking if files are duplicates using content hashing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_routes.router)
app.include_router(file_routes.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"File Duplicate Checker API starting up at {datetime.now()}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"File Duplicate Checker API shutting down at {datetime.now()}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "File Duplicate Checker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
