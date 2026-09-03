import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class F5TTSEngine:
    """Backup TTS engine using F5-TTS.

    Lazy-loads the model on first use to avoid import-time GPU allocation.
    """

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model = None

    def load_model(self):
        if self.model is None:
            try:
                import torch
                from f5_tts.api import F5TTS

                self.device = self.device if torch.cuda.is_available() else "cpu"
                self.model = F5TTS(device=self.device)
                logger.info("F5-TTS model loaded on %s", self.device)
            except ImportError:
                logger.warning("f5-tts not installed, using mock engine")
                self.model = "mock"

    def synthesize(
        self,
        text: str,
        reference_audio_path: Optional[str] = None,
        reference_text: Optional[str] = None,
    ) -> bytes:
        self.load_model()

        if self.model == "mock":
            return self._mock_synthesize(text)

        import torchaudio

        wav, sr, _ = self.model.infer(
            text=text,
            ref_file=reference_audio_path,
            ref_text=reference_text or "",
        )
        buffer = io.BytesIO()
        torchaudio.save(buffer, wav, sr, format="wav")
        return buffer.getvalue()

    def _mock_synthesize(self, text: str) -> bytes:
        """Generate minimal valid WAV for testing when f5-tts is unavailable."""
        import struct

        sample_rate = 22050
        num_samples = len(text) * 100
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
