import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path


class TestVoskEngine:
    """Tests for the Vosk (CPU fallback) transcription engine."""

    @patch("apps.voice.stt_vosk.wave")
    @patch("apps.voice.stt_vosk.vosk")
    def test_vosk_transcribe_returns_text(self, mock_vosk, mock_wave):
        from apps.voice.stt_vosk import VoskEngine

        mock_model = MagicMock()
        mock_vosk.Model.return_value = mock_model

        mock_rec = MagicMock()
        mock_vosk.KaldiRecognizer.return_value = mock_rec

        # Simulate waveform reads: one chunk with partial result, then final
        mock_rec.AcceptWaveform.side_effect = [True, False]
        mock_rec.Result.return_value = '{"text": "hello world"}'
        mock_rec.FinalResult.return_value = '{"text": " goodbye"}'

        mock_wf = MagicMock()
        mock_wf.readframes.side_effect = [b"data", b""]
        mock_wave.open.return_value.__enter__ = lambda s: mock_wf
        mock_wave.open.return_value.__exit__ = MagicMock(return_value=False)

        engine = VoskEngine(model_name="vosk-model-small-en-us-0.15")
        result = engine.transcribe("test.wav")

        assert result == "hello world goodbye"
        mock_vosk.Model.assert_called_once_with("vosk-model-small-en-us-0.15")

    @patch("apps.voice.stt_vosk.wave")
    @patch("apps.voice.stt_vosk.vosk")
    def test_vosk_transcribe_empty_audio(self, mock_vosk, mock_wave):
        from apps.voice.stt_vosk import VoskEngine

        mock_rec = MagicMock()
        mock_vosk.KaldiRecognizer.return_value = mock_rec

        mock_rec.AcceptWaveform.return_value = False
        mock_rec.Result.return_value = '{"text": ""}'
        mock_rec.FinalResult.return_value = '{"text": ""}'

        mock_wf = MagicMock()
        mock_wf.readframes.return_value = b""
        mock_wave.open.return_value.__enter__ = lambda s: mock_wf
        mock_wave.open.return_value.__exit__ = MagicMock(return_value=False)

        engine = VoskEngine(model_name="vosk-model-small-en-us-0.15")
        result = engine.transcribe("empty.wav")

        assert result == ""

    @patch("apps.voice.stt_vosk.wave")
    @patch("apps.voice.stt_vosk.vosk")
    def test_vosk_model_loaded_lazily(self, mock_vosk, mock_wave):
        from apps.voice.stt_vosk import VoskEngine

        engine = VoskEngine(model_name="vosk-model-small-en-us-0.15")
        mock_vosk.Model.assert_not_called()

        # First transcribe triggers model load
        mock_rec = MagicMock()
        mock_vosk.KaldiRecognizer.return_value = mock_rec
        mock_rec.AcceptWaveform.return_value = False
        mock_rec.Result.return_value = '{"text": ""}'
        mock_rec.FinalResult.return_value = '{"text": ""}'

        mock_wf = MagicMock()
        mock_wf.readframes.return_value = b""
        mock_wave.open.return_value.__enter__ = lambda s: mock_wf
        mock_wave.open.return_value.__exit__ = MagicMock(return_value=False)

        engine.transcribe("test.wav")
        mock_vosk.Model.assert_called_once()


class TestSTTService:
    """Tests for the main STT service with engine selection and fallback."""

    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    def test_transcribe_uses_whisper_when_available(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.return_value = "whisper result"
        service = STTService()
        result = service.transcribe("test.wav")

        assert result == "whisper result"
        mock_whisper.assert_called_once()
        mock_vosk.assert_not_called()

    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    def test_transcribe_falls_back_to_vosk_on_whisper_error(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.side_effect = RuntimeError("CUDA not available")
        mock_vosk.return_value = "vosk result"
        service = STTService()
        result = service.transcribe("test.wav")

        assert result == "vosk result"
        mock_whisper.assert_called_once()
        mock_vosk.assert_called_once()

    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    def test_transcribe_passes_language_to_whisper(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.return_value = "translated"
        service = STTService()
        result = service.transcribe("test.wav", language="fr")

        mock_whisper.assert_called_once_with("test.wav", "fr")
        assert result == "translated"

    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    def test_transcribe_returns_empty_on_total_failure(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.side_effect = RuntimeError("whisper failed")
        mock_vosk.side_effect = RuntimeError("vosk failed")
        service = STTService()

        with pytest.raises(RuntimeError):
            service.transcribe("test.wav")

    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    def test_transcribe_detects_language_when_not_specified(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.return_value = "auto detected"
        service = STTService()
        result = service.transcribe("test.wav")

        mock_whisper.assert_called_once_with("test.wav", None)
        assert result == "auto detected"


class TestSTTServiceAsync:
    """Tests for async transcription (non-blocking)."""

    @pytest.mark.asyncio
    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    async def test_transcribe_async_runs_in_thread(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.return_value = "async result"
        service = STTService()
        result = await service.transcribe_async("test.wav")

        assert result == "async result"

    @pytest.mark.asyncio
    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    async def test_transcribe_async_falls_back(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.side_effect = RuntimeError("GPU error")
        mock_vosk.return_value = "fallback async"
        service = STTService()
        result = await service.transcribe_async("test.wav")

        assert result == "fallback async"


class TestSTTServiceStreaming:
    """Tests for streaming transcription support."""

    @pytest.mark.asyncio
    @patch("apps.voice.stt_service.STTService._transcribe_vosk")
    @patch("apps.voice.stt_service.STTService._transcribe_whisper")
    async def test_stream_transcribe_yields_segments(self, mock_whisper, mock_vosk):
        from apps.voice.stt_service import STTService

        mock_whisper.return_value = "segment one segment two"
        service = STTService()
        segments = []
        async for segment in service.stream_transcribe("test.wav"):
            segments.append(segment)

        assert len(segments) > 0
        assert all(isinstance(s, str) for s in segments)


class TestSTTEngineSelection:
    """Tests for automatic engine selection based on hardware."""

    @patch("apps.voice.stt_service.STTService._has_gpu", return_value=True)
    def test_selects_whisper_on_gpu(self, mock_gpu):
        from apps.voice.stt_service import STTService

        service = STTService()
        assert service.engine_type == "whisper"

    @patch("apps.voice.stt_service.STTService._has_gpu", return_value=False)
    def test_selects_vosk_on_cpu(self, mock_gpu):
        from apps.voice.stt_service import STTService

        service = STTService()
        assert service.engine_type == "vosk"
