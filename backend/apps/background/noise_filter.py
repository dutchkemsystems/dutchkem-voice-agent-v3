import numpy as np
from typing import Optional


class NoiseFilter:
    """Background noise filtering using noisereduce library."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def reduce(self, audio: np.ndarray) -> np.ndarray:
        """Reduce background noise from audio signal."""
        if len(audio) == 0:
            return audio

        try:
            import noisereduce as nr
            result = nr.reduce_noise(
                y=audio.astype(np.float32),
                sr=self.sample_rate,
            )
            return result.astype(np.int16)
        except ImportError:
            return audio
