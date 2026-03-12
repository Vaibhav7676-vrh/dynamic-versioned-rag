from pydantic import BaseModel
from typing import List
from typing import Optional


class QueryRequest(BaseModel):
    question: str
    k: int = 3
    image:Optional[str] = None


class Source(BaseModel):
    source: str
    chunk_id: int
    start: int
    end: int


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]


class IngestRequest(BaseModel):
    path: str
