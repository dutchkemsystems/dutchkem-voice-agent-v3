import json
import wave
from typing import Optional

try:
    import vosk
except ImportError:
    vosk = None


class VoskEngine:
    """CPU-based transcription engine using Vosk (Kaldi)."""

    def __init__(self, model_name: str = "vosk-model-small-en-us-0.15"):
        self._model_name = model_name
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            if vosk is None:
                raise ImportError("vosk package is not installed")
            self._model = vosk.Model(self._model_name)

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        self._ensure_model()
        rec = vosk.KaldiRecognizer(self._model, 16000)
        results: list[str] = []

        with wave.open(audio_path, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        results.append(text)

            final = json.loads(rec.FinalResult())
            final_text = final.get("text", "").strip()
            if final_text:
                results.append(final_text)

        return " ".join(results)

    async def transcribe_async(self, audio_path: str, language: Optional[str] = None) -> str:
        import asyncio
        return await asyncio.to_thread(self.transcribe, audio_path, language)
