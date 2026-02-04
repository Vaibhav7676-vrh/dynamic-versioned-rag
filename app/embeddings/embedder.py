from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Loads a sentence-transformer model.
        """
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of texts into embeddings.

        Args:
            texts: List of chunk texts

        Returns:
            Numpy array of embeddings (num_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings
