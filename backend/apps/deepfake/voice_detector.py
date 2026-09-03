import numpy as np
from typing import Dict


class VoiceDeepfakeDetector:
    """Detect synthetic voice artifacts via spectral, prosody, and breathing analysis."""

    def __init__(self, artifact_threshold: float = 0.3):
        self.artifact_threshold = artifact_threshold

    def detect(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict:
        """Detect synthetic voice artifacts."""
        spectral_features = self._extract_spectral_features(audio, sample_rate)
        prosody_features = self._extract_prosody_features(audio, sample_rate)
        breathing_features = self._extract_breathing_patterns(audio, sample_rate)

        is_fake = (
            spectral_features["anomaly_score"] > self.artifact_threshold
            or prosody_features["unnatural_score"] > self.artifact_threshold
            or breathing_features["absence_score"] > self.artifact_threshold
        )

        max_score = max(
            spectral_features["anomaly_score"],
            prosody_features["unnatural_score"],
            breathing_features["absence_score"],
        )

        return {
            "is_deepfake": is_fake,
            "confidence": 1.0 - max_score,
            "details": {
                "spectral": spectral_features,
                "prosody": prosody_features,
                "breathing": breathing_features,
            },
        }

    def _extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict:
        """Extract spectral features for artifact detection via FFT."""
        fft = np.fft.fft(audio)
        magnitudes = np.abs(fft)

        total_energy = np.sum(magnitudes)
        if total_energy == 0:
            return {"anomaly_score": 0.0, "high_freq_energy": 0.0}

        n = len(magnitudes)
        # Positive frequency bins: 0 to n//2
        # Map high-frequency range (above 4000 Hz) to bin indices
        nyquist_bin = n // 2
        high_freq_hz = 4000
        high_freq_bin = int(high_freq_hz * n / sr)
        high_freq_bin = min(high_freq_bin, nyquist_bin)

        high_freq_energy = float(np.sum(magnitudes[high_freq_bin:nyquist_bin]) / total_energy)
        anomaly_score = min(high_freq_energy * 10, 1.0)

        return {"anomaly_score": anomaly_score, "high_freq_energy": high_freq_energy}

    def _extract_prosody_features(self, audio: np.ndarray, sr: int) -> Dict:
        """Extract prosody features for unnatural speech pattern detection."""
        frame_length = int(sr * 0.025)
        hop_length = int(sr * 0.010)

        if len(audio) < frame_length:
            return {"unnatural_score": 0.0, "pitch_variance": 0.0}

        energies = []
        for start in range(0, len(audio) - frame_length, hop_length):
            frame = audio[start : start + frame_length]
            energies.append(float(np.sqrt(np.mean(frame**2))))

        if len(energies) < 2:
            return {"unnatural_score": 0.0, "pitch_variance": 0.0}

        energy_array = np.array(energies)
        pitch_variance = float(np.var(energy_array))
        mean_energy = float(np.mean(energy_array))

        if mean_energy == 0:
            unnatural_score = 0.0
        else:
            cv = np.sqrt(pitch_variance) / mean_energy
            unnatural_score = min(float(cv), 1.0)

        return {"unnatural_score": unnatural_score, "pitch_variance": pitch_variance}

    def _extract_breathing_patterns(self, audio: np.ndarray, sr: int) -> Dict:
        """Detect absence of natural breathing patterns.

        Only analyzes breathing for audio longer than 3 seconds, where natural
        speech would be expected to contain breathing pauses.
        """
        frame_length = int(sr * 0.05)
        hop_length = int(sr * 0.025)
        min_duration_for_breathing = 3.0  # seconds

        if len(audio) < frame_length or len(audio) < sr * min_duration_for_breathing:
            return {"absence_score": 0.0, "silence_ratio": 0.0}

        silence_threshold = 0.01
        silence_frames = 0
        total_frames = 0

        for start in range(0, len(audio) - frame_length, hop_length):
            frame = audio[start : start + frame_length]
            rms = float(np.sqrt(np.mean(frame**2)))
            total_frames += 1
            if rms < silence_threshold:
                silence_frames += 1

        if total_frames == 0:
            return {"absence_score": 0.0, "silence_ratio": 0.0}

        silence_ratio = silence_frames / total_frames

        natural_breathing_ratio = (0.05, 0.30)
        if silence_ratio < natural_breathing_ratio[0]:
            absence_score = (natural_breathing_ratio[0] - silence_ratio) / natural_breathing_ratio[0]
        elif silence_ratio > natural_breathing_ratio[1]:
            absence_score = min((silence_ratio - natural_breathing_ratio[1]) / 0.5, 1.0)
        else:
            absence_score = 0.0

        return {"absence_score": absence_score, "silence_ratio": silence_ratio}
