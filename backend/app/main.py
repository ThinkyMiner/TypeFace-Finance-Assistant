from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import health, categories, transactions, stats, receipts, imports, ai_assistant
from app.db import Base, engine
from app.models import user, category, transaction  # ensure models are imported before create_all
from app.api.v1 import auth
# create tables on first run (for SQLite demo). In prod use Alembic only.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Finance API (Base)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health.router, prefix="/api/v1", tags=["meta"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(receipts.router, prefix="/api/v1/receipts", tags=["receipts"])
app.include_router(imports.router, prefix="/api/v1/imports", tags=["imports"])
app.include_router(ai_assistant.router, prefix="/api/v1/ai", tags=["ai-assistant"])