import io
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from kokoro import KPipeline
except ImportError:
    KPipeline = None

try:
    import soundfile as sf
except ImportError:
    sf = None


class KokoroEngine:
    """Kokoro TTS engine with lazy pipeline loading and graceful fallback.

    Uses Kokoro 82M (Apache 2.0) for fast, high-quality text-to-speech.
    Lazily loads pipelines per language code to minimize memory usage.
    Falls back to mock WAV generation when kokoro is not installed.
    """

    def __init__(self):
        self.pipelines: dict[str, object] = {}

    def get_pipeline(self, lang_code: str = "a"):
        if lang_code not in self.pipelines:
            if KPipeline is None:
                self.pipelines[lang_code] = "mock"
            else:
                self.pipelines[lang_code] = KPipeline(lang_code=lang_code)
        return self.pipelines[lang_code]

    def synthesize(
        self,
        text: str,
        voice: str = "af_heart",
        lang_code: str = "a",
    ) -> bytes:
        pipeline = self.get_pipeline(lang_code)

        if pipeline == "mock" or sf is None:
            return self._mock_synthesize(text)

        audio_chunks = []
        for gs, ps, audio in pipeline(text, voice=voice):
            audio_chunks.append(audio)

        if not audio_chunks:
            return self._mock_synthesize(text)

        full_audio = np.concatenate(audio_chunks)
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, 24000, format="wav")
        return buffer.getvalue()

    def synthesize_chunks(
        self,
        text: str,
        voice: str = "af_heart",
        lang_code: str = "a",
    ):
        """Yield WAV byte chunks as they are synthesized."""
        pipeline = self.get_pipeline(lang_code)

        if pipeline == "mock" or sf is None:
            yield self._mock_synthesize(text)
            return

        for gs, ps, audio in pipeline(text, voice=voice):
            buffer = io.BytesIO()
            sf.write(buffer, audio, 24000, format="wav")
            yield buffer.getvalue()

    def _mock_synthesize(self, text: str) -> bytes:
        """Generate minimal valid WAV for testing when kokoro is unavailable."""
        import struct

        sample_rate = 24000
        num_samples = max(len(text) * 100, 100)
        data_size = num_samples * 2
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + data_size,
            b"WAVE",
            b"fmt ",
            16,
            1,
            1,
            sample_rate,
            sample_rate * 2,
            2,
            16,
            b"data",
            data_size,
        )
        silence = b"\x00\x00" * num_samples
        return header + silence
