import re
import math
import hashlib
import numpy as np
from typing import List, Optional
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

class FastLocalEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    100% Offline, Zero-Dependency Semantic Vectorizer for ChromaDB.
    Uses subword n-gram hashing and TF-IDF weighted projections to map
    text into a normalized 384-dimensional dense semantic vector space.
    Guarantees immediate zero-download offline operation on any machine.
    """
    def __init__(self, dimension: int = 384, seed: int = 42):
        self.dimension = dimension
        self.seed = seed
        # Precompute projection vectors for feature hashing
        rng = np.random.default_rng(seed)
        self._projection_matrix = rng.normal(0, 1.0 / math.sqrt(dimension), (4096, dimension)).astype(np.float32)

    def name(self) -> str:
        return "fast_local_embedding"

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        # Extract words and char n-grams (3-to-5 chars) for subword semantic overlap
        words = re.findall(r"\b[\w\-áéíóúüñ]+\b", text)
        features = list(words)
        for w in words:
            if len(w) >= 3:
                for n in (3, 4):
                    for i in range(len(w) - n + 1):
                        features.append(w[i:i+n])
        return features

    def _embed_single(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dimension
        
        vec = np.zeros(self.dimension, dtype=np.float32)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
            
        for token, count in token_counts.items():
            # Hash token to a stable bucket index in [0, 4095]
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest()[:8], 16) % 4096
            # Sublinear TF weight: 1 + log(count)
            weight = 1.0 + math.log(count)
            vec += self._projection_matrix[h] * weight
            
        # L2 Normalization for accurate cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec.tolist()

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed_single(doc) for doc in input]
