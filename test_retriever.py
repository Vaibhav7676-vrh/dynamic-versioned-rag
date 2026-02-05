from app.retrieval.retriever import Retriever


if __name__ == "__main__":

    retriever = Retriever()

    results = retriever.search("What is RAG?")

    print(results)
