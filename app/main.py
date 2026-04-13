from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ingest import router as ingest_router
from app.api.query import router as query_router

# ----------------------------
# App Initialization
# ----------------------------
app = FastAPI(title="Versioned RAG API")

# ----------------------------
# CORS Configuration
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://dynamic-versioned-rag.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Routers
# ----------------------------
app.include_router(ingest_router)
app.include_router(query_router)

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def root():
    return {"message": "RAG system running"}