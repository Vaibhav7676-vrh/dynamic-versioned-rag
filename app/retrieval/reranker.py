from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):

        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query, results, top_k=5):

        texts = [r["metadata"]["text"] for r in results]

        pairs = [(query, t) for t in texts]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )

        reranked_results = [r[0] for r in ranked[:top_k]]

        return reranked_results