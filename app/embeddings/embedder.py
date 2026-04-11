from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self):
        self.model = None

    def get_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.model

    def embed_texts(self, texts):
        model = self.get_model()
        return model.encode(texts)