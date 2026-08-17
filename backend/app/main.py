import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.routes import auth_router, chat_router, intake_router, cases_router

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PharmaSentryBackend")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="PharmaSentry Secure Pharmacovigilance & Adverse Event Backend API"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(intake_router)
    app.include_router(cases_router)

    @app.get("/", tags=["Health"])
    async def root():
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
