"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.config import settings
from app.api.routes import prediction, dataset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ML-powered delay prediction service",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
# Allow all origins in development, specific origins in production
cors_origins = settings.allowed_origins_list
if settings.DEBUG:
    # In debug mode, allow all origins for easier development
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if "*" not in cors_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for visualizations
from fastapi.staticfiles import StaticFiles
from pathlib import Path

viz_dir = Path(__file__).parent.parent / "ml_pipeline" / "outputs" / "visualizations"
if viz_dir.exists():
    app.mount("/api/v1/visualizations", StaticFiles(directory=str(viz_dir)), name="visualizations")

# Register routes
app.include_router(
    prediction.router,
    prefix=settings.API_V1_PREFIX,
    tags=["predictions"]
)

app.include_router(
    dataset.router,
    prefix=settings.API_V1_PREFIX,
    tags=["dataset"]
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Transport Delay Prediction API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Health check endpoint (outside API prefix for easier access)
@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")
    
    # Try to load model
    try:
        from app.models.ml_model import MLModelWrapper
        model = MLModelWrapper()
        if model.is_loaded():
            logger.info("ML model loaded successfully")
        else:
            logger.warning("ML model not found - running in mock mode")
    except Exception as e:
        logger.warning(f"Could not load ML model: {str(e)} - running in mock mode")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

