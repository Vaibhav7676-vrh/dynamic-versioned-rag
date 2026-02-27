from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

from .schemas import QueryRequest, QueryResponse, Source
from app.retrieval.retriever import Retriever
from app.rag.generator import Generator

router = APIRouter()


# ------------------------
# Normal JSON endpoint (unchanged)
# ------------------------
@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    retriever = Retriever()
    results = retriever.search(req.question, k=req.k)

    contexts = [r["metadata"]["text"] for r in results]

    generator = Generator()
    answer = generator.generate(req.question, contexts)

    sources = []
    for r in results:
        m = r["metadata"]
        sources.append(
            Source(
                source=m["source"],
                chunk_id=m["chunk_id"],
                start=m.get("start", 0),
                end=m.get("end", 0),
            )
        )

    return QueryResponse(answer=answer, sources=sources)


# ------------------------
# New Streaming endpoint
# ------------------------
from fastapi.responses import StreamingResponse
import asyncio

@router.post("/query-stream")
async def query_stream(req: QueryRequest):
    retriever = Retriever()
    results = retriever.search(req.question, k=req.k)
    contexts = [r["metadata"]["text"] for r in results]

    generator = Generator()

    async def token_stream():
        for token in generator.stream_generate(req.question, contexts):
            yield token
            await asyncio.sleep(0)

    return StreamingResponse(
        token_stream(),
        media_type="text/plain",
    )