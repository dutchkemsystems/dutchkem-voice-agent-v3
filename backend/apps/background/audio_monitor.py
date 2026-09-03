import asyncio
import numpy as np
import queue
from typing import Callable, Optional

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import webrtcvad
    _HAS_WEBRTCVAD = True
except ImportError:
    webrtcvad = None
    _HAS_WEBRTCVAD = False

from apps.background.noise_filter import NoiseFilter
from apps.background.voice_biometrics import VoiceBiometrics


class _FallbackVAD:
    """Energy-based VAD fallback when webrtcvad is unavailable."""

    def __init__(self, aggressiveness: int = 2, threshold: float = 500.0):
        self.aggressiveness = aggressiveness
        self.threshold = threshold

    def is_speech(self, audio_bytes: bytes, sample_rate: int) -> bool:
        audio = np.frombuffer(audio_bytes, dtype=np.int16)
        energy = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        return energy > self.threshold


class AudioMonitor:
    """Continuous audio monitoring with VAD, noise filtering, and speaker verification."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        vad_aggressiveness: int = 2,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_running = False
        self.on_speech_detected: Optional[Callable] = None
        self.on_silence_detected: Optional[Callable] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # VAD
        if _HAS_WEBRTCVAD:
            self.vad = webrtcvad.Vad(vad_aggressiveness)
        else:
            self.vad = _FallbackVAD(aggressiveness=vad_aggressiveness)

        # Noise filter
        self.noise_filter = NoiseFilter(sample_rate=sample_rate)

        # Voice biometrics
        self.voice_biometrics = VoiceBiometrics()

        # Adaptive sampling / battery optimization
        self.adaptive_sampling = True
        self.battery_level: float = 1.0
        self.cpu_threshold: float = 0.8

    def set_battery_level(self, level: float) -> None:
        """Set current battery level (0.0 to 1.0)."""
        self.battery_level = max(0.0, min(1.0, level))

    def set_cpu_threshold(self, threshold: float) -> None:
        """Set CPU usage threshold for adaptive sampling."""
        self.cpu_threshold = max(0.0, min(1.0, threshold))

    def get_optimal_sample_rate(self) -> int:
        """Return optimal sample rate based on battery and adaptive settings."""
        if not self.adaptive_sampling:
            return self.sample_rate

        if self.battery_level < 0.2:
            return min(8000, self.sample_rate)
        elif self.battery_level < 0.5:
            return min(11025, self.sample_rate)
        return self.sample_rate

    def audio_callback(self, indata, frames, time_info, status):
        """Process audio frames in real-time (sync callback, queue for async)."""
        # Convert to int16
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)

        # Noise reduction
        audio_clean = self.noise_filter.reduce(audio_int16)

        # VAD
        audio_bytes = audio_clean.tobytes()
        try:
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
        except Exception:
            is_speech = False

        # Queue for async processing
        self._audio_queue.put((audio_clean, is_speech))

    async def _process_queue(self):
        """Process queued audio in async context."""
        while self.is_running:
            try:
                audio_data, is_speech = self._audio_queue.get_nowait()
                if is_speech and self.on_speech_detected:
                    await self.on_speech_detected(audio_data)
                elif not is_speech and self.on_silence_detected:
                    await self.on_silence_detected()
            except queue.Empty:
                await asyncio.sleep(0.01)

    async def start(self):
        """Start continuous audio monitoring."""
        if sd is None:
            raise RuntimeError("sounddevice is required for audio capture")

        self.is_running = True
        self._loop = asyncio.get_event_loop()

        sample_rate = self.get_optimal_sample_rate()

        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=self.channels,
            callback=self.audio_callback,
        )

        with stream:
            await self._process_queue()

    def stop(self):
        """Stop audio monitoring."""
        self.is_running = False
