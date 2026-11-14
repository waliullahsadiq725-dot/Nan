from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core_config import settings
from db_session import Base, engine
import models_entities as entities
import auth_router as auth
import admin_router as admin
import resources_router as resources
import catalog_router as catalog
import notifications_router as notifications

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0",
              description="Backend API for Nangarhar University Digital Library")

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def initialize_development_database():
    # For initial local development only. Use Alembic migrations before production.
    Base.metadata.create_all(bind=engine)
    Path(settings.FILE_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

@app.get("/")
def home():
    return {"project": settings.PROJECT_NAME, "status": "online", "api_docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

for api_router in (auth.router, admin.router, resources.router, catalog.router, notifications.router):
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
