import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChatterboxEngine:
    """Wrapper around Chatterbox TTS for voice cloning and synthesis.

    Lazy-loads the model on first use to avoid import-time GPU allocation.
    """

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model = None

    def load_model(self):
        if self.model is None:
            try:
                import torch
                from chatterbox.tts import ChatterboxTTS

                self.device = self.device if torch.cuda.is_available() else "cpu"
                self.model = ChatterboxTTS.from_pretrained(device=self.device)
                logger.info("Chatterbox model loaded on %s", self.device)
            except ImportError:
                logger.warning("chatterbox-tts not installed, using mock engine")
                self.model = "mock"

    def clone_and_synthesize(
        self,
        text: str,
        reference_audio_path: str,
        exaggeration: float = 0.5,
    ) -> bytes:
        self.load_model()

        if self.model == "mock":
            return self._mock_synthesize(text)

        import torch
        import torchaudio

        wav = self.model.generate(
            text=text,
            audio_prompt_path=reference_audio_path,
            exaggeration=exaggeration,
        )
        buffer = io.BytesIO()
        torchaudio.save(buffer, wav, self.model.sr, format="wav")
        return buffer.getvalue()

    def _mock_synthesize(self, text: str) -> bytes:
        """Generate minimal valid WAV for testing when chatterbox is unavailable."""
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
