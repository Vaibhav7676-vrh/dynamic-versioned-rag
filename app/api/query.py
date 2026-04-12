from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

from .schemas import QueryRequest

from app.retrieval.retriever import Retriever
from app.routing.router import SelfRouter

from app.models.text_llm import TextLLM
from app.models.reasoning_model import ReasoningModel
from app.models.vision_model import VisionModel

router = APIRouter()


@router.post("/query-stream")
async def query_stream(req: QueryRequest):

    try:
        # -----------------------------
        # Initialize components
        # -----------------------------
        retriever = Retriever()
        router_model = SelfRouter()

        text_model = TextLLM()
        reasoning_model = ReasoningModel()
        vision_model = VisionModel()

        # -----------------------------
        # Route the query
        # -----------------------------
        decision = router_model.route(req.question)
        print("Router decision:", decision)

        contexts = []

        # -----------------------------
        # Retrieval (SAFE)
        # -----------------------------
        if decision != "vlm":

            results = retriever.retrieve(req.question, k=req.k)

            if not results:
                print("No retrieval results → using fallback context")
                contexts = ["No context available"]
            else:
                contexts = [
                    r.get("metadata", {}).get("text", "")
                    for r in results
                ]

        # -----------------------------
        # Model selection
        # -----------------------------
        if decision == "reasoning":

            answer = reasoning_model.generate(
                req.question,
                contexts
            )

        elif decision == "vlm":

            if not req.image:
                print("No image provided → fallback to TextLLM")

                answer = text_model.generate(
                    req.question,
                    contexts
                )
            else:
                answer = vision_model.generate(
                    req.question,
                    req.image
                )

        else:

            answer = text_model.generate(
                req.question,
                contexts
            )

        # -----------------------------
        # Streaming response
        # -----------------------------
        async def stream():

            words = answer.split(" ")

            for word in words:
                yield word + " "
                await asyncio.sleep(0.02)

        return StreamingResponse(
            stream(),
            media_type="text/plain",
        )

    except Exception as e:
        print("ERROR in /query-stream:", e)

        async def error_stream():
            yield f"Error: {str(e)}"

        return StreamingResponse(
            error_stream(),
            media_type="text/plain",
        )