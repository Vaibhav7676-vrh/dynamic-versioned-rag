from app.models.text_llm import TextLLM
from app.models.reasoning_model import ReasoningModel

# fake retrieved context
contexts = [
    "Retrieval Augmented Generation (RAG) combines vector retrieval with language models.",
    "RAG improves factual accuracy by grounding responses in external documents."
]

print("\n--- Testing Text LLM ---\n")

text_model = TextLLM()
answer1 = text_model.generate(
    "What is RAG?",
    contexts
)

print(answer1)


print("\n--- Testing Reasoning Model ---\n")

reason_model = ReasoningModel()
answer2 = reason_model.generate(
    "Compare RAG and fine tuning step by step.",
    contexts
)

print(answer2)