from app.routing.router import SelfRouter

router = SelfRouter()

queries = [
    "What is RAG?",
    "Compare RAG and fine tuning step by step",
    "Explain this image",
    "Why does RAG improve factual accuracy?"
]

for q in queries:
    route = router.route(q)
    print("\nQuery:", q)
    print("Router decision:", route)