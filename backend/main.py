from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from database.config import init_db
from backend.main import general_exception_handler, validation_exception_handler, http_exception_handler, startup_event, shutdown_event
from backend.routes.sessions import router as sessions_router
from backend.routes.files import router as files_router
from backend.routes.messages import router as messages_router

# Initialize FastAPI app
app = FastAPI(
    title="Aakaar Project",
    description="Backend API for Aakaar Project",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow localhost:3000 for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(sessions_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(messages_router, prefix="/api")

# Global exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    return await validation_exception_handler(request, exc)

@app.exception_handler(Exception)
async def custom_general_exception_handler(request: Request, exc: Exception):
    return await general_exception_handler(request, exc)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Lifespan context manager
@app.on_event("startup")
async def on_startup():
    await startup_event()
    init_db()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown_event()

# AI_ROUTER_INJECTION_POINT — do not remove this line