from app.retrieval.retriever import Retriever
from app.rag.generator import Generator


if __name__ == "__main__":
    retriever = Retriever()
    generator = Generator()

    query = "What is RAG?"

    results = retriever.search(query)

    contexts = [r["metadata"]["source"] for r in results]

    answer = generator.generate(query, contexts)

    print("\nFINAL ANSWER:\n")
    print(answer)
