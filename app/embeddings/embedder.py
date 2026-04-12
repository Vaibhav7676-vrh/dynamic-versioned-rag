from typing import List
import numpy as np


class Embedder:
    def __init__(self):
        pass

    def embed_texts(self, texts: List[str]):
        # Dummy embeddings (for deployment)
        return np.random.rand(len(texts), 384).astype("float32")