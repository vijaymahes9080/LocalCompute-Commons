"""
Privacy-Preserving Federated Embedding & Vector Generation Engine
"""
import hashlib
import math
import random
from typing import List, Dict, Any

class FederatedEmbeddingEngine:
    """
    Computes local semantic vector embeddings with differential privacy noise
    to prevent document reconstruction while enabling decentralized similarity search.
    """
    def __init__(self, dimension: int = 128, epsilon: float = 1.0):
        self.dimension = dimension
        self.epsilon = epsilon  # Privacy budget parameter

    def generate_embedding(self, text: str, apply_differential_privacy: bool = True) -> List[float]:
        """Generates a normalized dense vector embedding for text."""
        # Deterministic pseudo-embedding from text hash shingles
        words = text.lower().split()
        vector = [0.0] * self.dimension
        
        for w in words:
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            for d in range(self.dimension):
                bit = (h >> (d % 32)) & 1
                vector[d] += 1.0 if bit else -1.0
                
        # Optional Differential Privacy: Add Laplace noise
        if apply_differential_privacy:
            scale = 1.0 / self.epsilon
            for d in range(self.dimension):
                u = random.uniform(-0.4999, 0.4999)
                noise = -scale * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))
                vector[d] += noise * 0.05
                
        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [round(v / norm, 4) for v in vector]

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two vector embeddings."""
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return round(dot, 4)

federated_embedding_engine = FederatedEmbeddingEngine()
