import numpy as np
from typing import Optional


class VoiceBiometrics:
    """Speaker verification via voice embeddings and cosine similarity."""

    def __init__(self, embedding_dim: int = 256, similarity_threshold: float = 0.75):
        self.embedding_dim = embedding_dim
        self.similarity_threshold = similarity_threshold
        self.registered_voices: dict[str, np.ndarray] = {}

    def register_voice(self, user_id: str, embedding: np.ndarray) -> None:
        """Register a voice embedding for a user."""
        self.registered_voices[user_id] = embedding

    def extract_embedding(self, audio: np.ndarray) -> Optional[np.ndarray]:
        """Extract a voice embedding from audio samples.

        Uses a simple spectral feature approach when heavy ML
        libraries are unavailable.
        """
        if len(audio) == 0:
            return None

        float_audio = audio.astype(np.float64)

        # Compute spectral centroid-like features via FFT
        fft = np.fft.rfft(float_audio)
        magnitudes = np.abs(fft)

        # Split into bands and compute energy per band
        n_bands = self.embedding_dim
        band_size = max(1, len(magnitudes) // n_bands)
        embedding = np.zeros(n_bands, dtype=np.float64)

        for i in range(n_bands):
            start = i * band_size
            end = min(start + band_size, len(magnitudes))
            if start < len(magnitudes):
                embedding[i] = np.mean(magnitudes[start:end])

        # L2-normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def verify_voice(self, audio_embedding: np.ndarray) -> tuple[Optional[str], float]:
        """Verify a voice embedding against registered voices.

        Returns (user_id, confidence) or (None, 0.0) if no match.
        """
        if not self.registered_voices:
            return None, 0.0

        best_user = None
        best_score = 0.0

        for user_id, known_emb in self.registered_voices.items():
            score = self._compute_similarity(audio_embedding, known_emb)
            if score > best_score:
                best_score = score
                best_user = user_id

        if best_score >= self.similarity_threshold:
            return best_user, best_score
        return None, best_score

    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Cosine similarity between two embeddings."""
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return float(np.dot(emb1, emb2) / (norm1 * norm2))
