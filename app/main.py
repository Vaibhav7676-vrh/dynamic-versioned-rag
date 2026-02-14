from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.query import router as query_router

app = FastAPI(title="Versioned RAG API")

app.include_router(ingest_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {"message": "RAG system running"}
