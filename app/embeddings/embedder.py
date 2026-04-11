from typing import List

class Embedder:
    def __init__(self):
        pass

    def embed_texts(self, texts: List[str]):
        # Return dummy embeddings (dimension = 384)
        return [[0.0]*384 for _ in texts]