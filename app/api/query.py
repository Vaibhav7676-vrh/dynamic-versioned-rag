from fastapi import APIRouter
from .schemas import QueryRequest, QueryResponse, Source

from app.retrieval.retriever import Retriever
from app.rag.generator import Generator

router = APIRouter()


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
