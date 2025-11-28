"""
FASTAPI APPLICATION - Enterprise API Server
Cyberzilla Enterprise Intelligence Platform v2.1.0
"""

"""
FASTAPI APPLICATION - Enterprise API Server
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from core.config import get_settings
from core.enterprise_trust import trust_manager
from database.db import init_db

from .routes import router as api_router


# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("🚀 Starting Cyberzilla Enterprise API")
    trust_manager.establish_enterprise_presence()
    init_db()
    yield
    # Shutdown
    logging.info("🛑 Shutting down Cyberzilla Enterprise API")


# Create FastAPI app
app = FastAPI(
    title="Cyberzilla Enterprise Intelligence Platform",
    description="Enterprise-grade social intelligence and digital footprint analysis",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cyberzilla.systems"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["cyberzilla.systems", "api.cyberzilla.systems"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/")
async def root():
    return {
        "message": "Cyberzilla Enterprise Intelligence Platform",
        "version": "2.1.0",
        "docs": "/docs",
    }


import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import generate_latest

from core.ai_hierarchy import AIHierarchyManager
from core.resource_orchestrator import resource_orchestrator
from database.db import db_manager
from security.rate_limiter import RateLimiter
from monitoring.health_checks import HealthMonitor
from monitoring.metrics import TASKS_PROCESSED, TASK_DURATION
from core.exceptions import (
    CyberzillaException,
    SecurityViolation,
    AuthenticationError,
    ConfigurationError,
    ValidationError,
    AgentError,
    ProxyError,
    RateLimitExceeded,
    DatabaseError,
    NetworkError,
)

from .routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/api.log"), logging.StreamHandler()],
)

logger = logging.getLogger("cyberzilla_api")

# Global instances
settings = get_settings()
rate_limiter = RateLimiter()
ai_hierarchy = AIHierarchyManager()
health_monitor = HealthMonitor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for startup and shutdown events
    """
    # Startup
    startup_time = datetime.now()
    logger.info("🚀 Starting Cyberzilla Enterprise API Server")

    try:
        # Establish enterprise trust presence
        trust_manager.establish_enterprise_presence()
        logger.info("✅ Enterprise trust established")

        # Initialize database
        init_db()
        logger.info("✅ Database initialized")

        # Initialize AI hierarchy
        await ai_hierarchy.initialize_default_agents()
        logger.info("✅ AI hierarchy initialized")

        # Assess system resources
        resources = await resource_orchestrator.assess_system_resources()
        strategy = resource_orchestrator.determine_resource_strategy(resources)
        logger.info(f"✅ Resource strategy: {strategy.level.value}")

        startup_duration = (datetime.now() - startup_time).total_seconds()
        logger.info(f"🎯 Startup completed in {startup_duration:.2f}s")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield  # Application runs here

    # Shutdown
    logger.info("🛑 Shutting down Cyberzilla Enterprise API")
    try:
        # Cleanup operations
        await ai_hierarchy.cleanup()
        logger.info("✅ Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Shutdown cleanup failed: {e}")


# Custom OpenAPI configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Customize OpenAPI schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://cyberzilla.systems/logo.png",
        "backgroundColor": "#FFFFFF",
    }

    openapi_schema["servers"] = [
        {
            "url": "https://api.cyberzilla.systems",
            "description": "Production API server",
        },
        {"url": "http://localhost:8000", "description": "Development server"},
    ]

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://cyberzilla.systems/favicon.ico",
    )


# Create FastAPI app
app = FastAPI(
    title="Cyberzilla Enterprise Intelligence Platform",
    description="""
    🦖 Enterprise-grade social intelligence and digital footprint analysis platform.
    
    ## Features
    
    * 🔍 **Social Profile Lookup** - Cross-platform intelligence gathering
    * 🎯 **Advanced Correlation** - AI-powered identity correlation  
    * 🕵️ **Deception Detection** - Advanced manipulation detection
    * 📊 **Digital Footprint Analysis** - Comprehensive digital presence mapping
    * 🛡️ **Enterprise Security** - Military-grade security and compliance
    
    ## Authentication
    
    Most endpoints require JWT token authentication.
    Contact support@cyberzilla.systems for API access.
    """,
    version="2.1.0",
    terms_of_service="https://cyberzilla.systems/terms",
    contact={
        "name": "Cyberzilla Systems Support",
        "url": "https://cyberzilla.systems/support",
        "email": "support@cyberzilla.systems",
    },
    license_info={
        "name": "AGPL-3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
    docs_url=None,  # Disable default docs
    redoc_url="/documentation",
    lifespan=lifespan,
)

# Custom OpenAPI
app.openapi = custom_openapi
app.add_route("/docs", custom_swagger_ui_html)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cyberzilla.systems",
        "https://app.cyberzilla.systems",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "cyberzilla.systems",
        "api.cyberzilla.systems",
        "localhost",
        "127.0.0.1",
    ],
)

# Performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Custom middleware for logging and security
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    start_time = time.time()

    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Performance headers
    response.headers["X-Response-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
    response.headers["X-Powered-By"] = "Cyberzilla Enterprise v2.1.0"

    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    start_time = time.time()

    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    try:
        await rate_limiter.check_rate_limit(
            identifier=client_ip,
            limit=settings.rate_limits.api_requests_per_minute,
            window=60,
        )
    except HTTPException:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"},
        )

    # Process request
    response = await call_next(request)

    # Log request
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.2f}ms - "
        f"IP: {client_ip}"
    )

    # Prometheus metrics
    TASKS_PROCESSED.inc()
    TASK_DURATION.observe(process_time / 1000)  # Convert ms to seconds

    return response


# Include routers
app.include_router(api_router, prefix="/api/v1")

# Mount static files for docs
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Expose Prometheus metrics
    """
    return Response(generate_latest(), media_type="text/plain")


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Comprehensive system health check
    """
    return await health_monitor.run_all_checks()


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "🦖 Cyberzilla Enterprise Intelligence Platform",
        "version": "2.1.0",
        "description": "Enterprise-grade social intelligence and digital footprint analysis",
        "documentation": "/docs",
        "health_check": "/health",
        "support": "support@cyberzilla.systems",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/system/info", tags=["System"])
async def system_info():
    """
    Get detailed system information
    """
    trust_report = trust_manager.generate_legitimacy_report()
    resource_report = resource_orchestrator.get_performance_report()
    agent_report = ai_hierarchy.get_agent_performance_report()

    return {
        "software": trust_report["software_identity"],
        "system_integration": trust_report["system_integration"],
        "resource_strategy": resource_report["current_strategy"],
        "agent_performance": agent_report["performance_metrics"],
        "compliance": trust_report["compliance"],
        "timestamp": datetime.now().isoformat(),
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "documentation": "/docs",
            "support": "support@cyberzilla.systems",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "support": "support@cyberzilla.systems",
            "error_id": str(hash(str(exc))),  # For support tracking
        },
    )


@app.exception_handler(SecurityViolation)
async def security_violation_handler(request: Request, exc: SecurityViolation):
    logger.warning(f"Security violation: {exc.detail if hasattr(exc, 'detail') else exc}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Forbidden: Security Violation", "message": str(exc)},
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    logger.warning(f"Authentication error: {exc.detail if hasattr(exc, 'detail') else exc}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Unauthorized", "message": str(exc)},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded: {exc.detail if hasattr(exc, 'detail') else exc}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded", "message": str(exc)},
    )


@app.exception_handler(CyberzillaException)
async def cyberzilla_exception_handler(request: Request, exc: CyberzillaException):
    logger.error(f"Cyberzilla application error: {exc.detail if hasattr(exc, 'detail') else exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal application error occurred", "message": str(exc)},
    )


# Create necessary directories
Path("logs").mkdir(exist_ok=True)
Path("api/static").mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        log_level="info",
        access_log=True,
    )
