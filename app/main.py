from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.certificates import router as certificate_router
from app.api.jobs import router as job_router
from app.core.config import APP_NAME, APP_VERSION, DATABASE_URL
from app.database.database import create_database_engine, create_session_factory
from app.database import models


def create_app(database_url: str = DATABASE_URL) -> FastAPI:
    engine = create_database_engine(database_url)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        from app.database.database import Base

        Base.metadata.create_all(bind=engine)
        yield
        engine.dispose()

    application = FastAPI(
        title=APP_NAME,
        description="Create, track, and retrieve bulk-generated certificates.",
        version=APP_VERSION,
        lifespan=lifespan,
    )
    application.state.session_factory = session_factory
    application.include_router(job_router)
    application.include_router(certificate_router)

    @application.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return application


app = create_app()