
from fastapi import FastAPI

from app.database import Base, engine
from app.models import User, Document, Permission, AuditLog
from app.routes import auth, documents, permissions, audit

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TrustVault API",
    description="Secure document sharing and access management platform",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(permissions.router)
app.include_router(audit.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to TrustVault",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
