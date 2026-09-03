import asyncio
import logging
from typing import AsyncIterator, Optional

from apps.voice.kokoro_engine import KokoroEngine

logger = logging.getLogger(__name__)

# Maps user-friendly accent names to Kokoro (voice, lang_code) pairs.
# Kokoro voices: a=American, b=British, j=Japanese, etc.
ACCENT_VOICE_MAP: dict[str, dict] = {
    "nigerian": {"voice": "af_heart", "lang_code": "a"},
    "ghanaian": {"voice": "af_heart", "lang_code": "a"},
    "uk": {"voice": "bf_emma", "lang_code": "b"},
    "us": {"voice": "af_heart", "lang_code": "a"},
    "american": {"voice": "af_heart", "lang_code": "a"},
    "british": {"voice": "bf_emma", "lang_code": "b"},
    "japanese": {"voice": "jf_alpha", "lang_code": "j"},
    "default": {"voice": "af_heart", "lang_code": "a"},
}


class TTSService:
    """Text-to-Speech service with voice selection and accent/dialect support.

    Wraps KokoroEngine with:
    - Voice/accent mapping (Nigerian, Ghanaian, UK, US, Japanese, etc.)
    - Non-blocking async synthesis via asyncio.to_thread
    - Streaming audio output yielding chunks as they're produced
    """

    def __init__(self):
        self.engine = KokoroEngine()
        self.accent_voices = ACCENT_VOICE_MAP

    def _resolve_voice(self, voice: str) -> tuple[str, str]:
        """Resolve a voice name to (kokoro_voice, lang_code).

        If the voice matches an accent key, return the mapped values.
        Otherwise treat it as a raw Kokoro voice name with default lang_code.
        """
        key = voice.lower().strip()
        if key in self.accent_voices:
            entry = self.accent_voices[key]
            return entry["voice"], entry["lang_code"]
        return voice, "a"

    def synthesize(
        self,
        text: str,
        voice: str = "af_heart",
    ) -> bytes:
        """Synchronous text-to-speech synthesis."""
        kokoro_voice, lang_code = self._resolve_voice(voice)
        return self.engine.synthesize(text, voice=kokoro_voice, lang_code=lang_code)

    async def synthesize_async(
        self,
        text: str,
        voice: str = "af_heart",
    ) -> bytes:
        """Non-blocking text-to-speech synthesis."""
        return await asyncio.to_thread(self.synthesize, text, voice)

    async def stream_synthesize(
        self,
        text: str,
        voice: str = "af_heart",
    ) -> AsyncIterator[bytes]:
        """Yield audio byte chunks as they are synthesized."""
        kokoro_voice, lang_code = self._resolve_voice(voice)

        def _generate_chunks():
            return list(self.engine.synthesize_chunks(text, voice=kokoro_voice, lang_code=lang_code))

        chunks = await asyncio.to_thread(_generate_chunks)
        for chunk in chunks:
            yield chunk


tts_service = TTSService()
