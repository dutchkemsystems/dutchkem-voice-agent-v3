import asyncio
from typing import Optional, AsyncIterator

from apps.voice.stt_vosk import VoskEngine

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None


class STTService:
    """Speech-to-Text service with automatic engine selection.

    Uses faster-whisper (GPU) when available, falls back to Vosk (CPU).
    All transcription runs in threads to avoid blocking the event loop.
    """

    def __init__(self):
        self._whisper_model = None
        self._vosk_engine: Optional[VoskEngine] = None
        self.engine_type = "whisper" if self._has_gpu() else "vosk"

    @staticmethod
    def _has_gpu() -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    @property
    def _vosk(self) -> VoskEngine:
        if self._vosk_engine is None:
            self._vosk_engine = VoskEngine()
        return self._vosk_engine

    def _transcribe_whisper(self, audio_path: str, language: Optional[str] = None) -> str:
        if WhisperModel is None:
            raise ImportError("faster-whisper package is not installed")
        if self._whisper_model is None:
            self._whisper_model = WhisperModel("large-v3", device="cuda", compute_type="int8")
        segments, _info = self._whisper_model.transcribe(
            audio_path,
            beam_size=5,
            language=language,
        )
        return " ".join(seg.text for seg in segments)

    def _transcribe_vosk(self, audio_path: str, language: Optional[str] = None) -> str:
        return self._vosk.transcribe(audio_path, language)

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcribe audio file to text. Tries whisper first, falls back to vosk."""
        try:
            return self._transcribe_whisper(audio_path, language)
        except Exception:
            return self._transcribe_vosk(audio_path, language)

    async def transcribe_async(self, audio_path: str, language: Optional[str] = None) -> str:
        """Non-blocking transcription. Runs the sync transcribe in a thread."""
        return await asyncio.to_thread(self.transcribe, audio_path, language)

    async def stream_transcribe(self, audio_path: str, language: Optional[str] = None) -> AsyncIterator[str]:
        """Yield transcription segments as they become available.

        For file-based engines this returns the full result split into chunks.
        For streaming engines this would yield partial results in real-time.
        """
        text = await self.transcribe_async(audio_path, language)
        # Split into sentence-like segments on common delimiters
        segments = []
        current = []
        for char in text:
            current.append(char)
            if char in ".!?\n" and current:
                segments.append("".join(current).strip())
                current = []
        if current:
            segments.append("".join(current).strip())

        for segment in segments:
            if segment:
                yield segment
