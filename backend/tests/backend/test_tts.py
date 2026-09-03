import pytest
from unittest.mock import patch, MagicMock
import io


# --- KokoroEngine Tests ---


class TestKokoroEngine:
    def test_init_creates_empty_pipelines(self):
        from apps.voice.kokoro_engine import KokoroEngine

        engine = KokoroEngine()
        assert engine.pipelines == {}

    @patch("apps.voice.kokoro_engine.KPipeline", create=True)
    def test_get_pipeline_creates_and_caches(self, mock_pipeline_cls):
        from apps.voice.kokoro_engine import KokoroEngine

        mock_pipeline_cls.return_value = MagicMock()
        engine = KokoroEngine()
        pipeline = engine.get_pipeline("a")
        assert "a" in engine.pipelines
        assert pipeline is engine.pipelines["a"]

    @patch("apps.voice.kokoro_engine.KPipeline", create=True)
    def test_get_pipeline_reuses_cached(self, mock_pipeline_cls):
        from apps.voice.kokoro_engine import KokoroEngine

        mock_pipeline_cls.return_value = MagicMock()
        engine = KokoroEngine()
        p1 = engine.get_pipeline("a")
        p2 = engine.get_pipeline("a")
        assert p1 is p2
        assert mock_pipeline_cls.call_count == 1

    @patch("apps.voice.kokoro_engine.sf")
    @patch("apps.voice.kokoro_engine.KPipeline", create=True)
    def test_synthesize_returns_wav_bytes(self, mock_pipeline_cls, mock_sf):
        from apps.voice.kokoro_engine import KokoroEngine

        import numpy as np

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [("g", "p", np.zeros(100, dtype=np.float32))]
        mock_pipeline_cls.return_value = mock_pipeline

        def fake_write(buffer, data, samplerate, format=None):
            buffer.write(b"RIFF" + b"\x00" * 40)

        mock_sf.write.side_effect = fake_write

        engine = KokoroEngine()
        result = engine.synthesize("Hello world")
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch("apps.voice.kokoro_engine.sf")
    @patch("apps.voice.kokoro_engine.KPipeline", create=True)
    def test_synthesize_empty_text_returns_bytes(self, mock_pipeline_cls, mock_sf):
        from apps.voice.kokoro_engine import KokoroEngine

        import numpy as np

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = []
        mock_pipeline_cls.return_value = mock_pipeline

        def fake_write(buffer, data, samplerate, format=None):
            buffer.write(b"")

        mock_sf.write.side_effect = fake_write

        engine = KokoroEngine()
        result = engine.synthesize("")
        assert isinstance(result, bytes)

    @patch("apps.voice.kokoro_engine.sf")
    @patch("apps.voice.kokoro_engine.KPipeline", create=True)
    def test_synthesize_concatenates_chunks(self, mock_pipeline_cls, mock_sf):
        from apps.voice.kokoro_engine import KokoroEngine

        import numpy as np

        chunk1 = np.ones(100, dtype=np.float32)
        chunk2 = np.ones(200, dtype=np.float32) * 2

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [
            ("g1", "p1", chunk1),
            ("g2", "p2", chunk2),
        ]
        mock_pipeline_cls.return_value = mock_pipeline

        written_data = {}

        def fake_write(buffer, data, samplerate, format=None):
            written_data["data"] = data
            written_data["samplerate"] = samplerate
            buffer.write(b"RIFF" + b"\x00" * 40)

        mock_sf.write.side_effect = fake_write

        engine = KokoroEngine()
        engine.synthesize("Hello world")

        import numpy as np

        assert written_data["samplerate"] == 24000
        assert len(written_data["data"]) == 300

    @patch("apps.voice.kokoro_engine.sf")
    @patch("apps.voice.kokoro_engine.KPipeline", create=True)
    def test_synthesize_default_voice_and_lang(self, mock_pipeline_cls, mock_sf):
        from apps.voice.kokoro_engine import KokoroEngine

        import numpy as np

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [("g", "p", np.zeros(10, dtype=np.float32))]
        mock_pipeline_cls.return_value = mock_pipeline

        def fake_write(buffer, data, samplerate, format=None):
            buffer.write(b"RIFF" + b"\x00" * 40)

        mock_sf.write.side_effect = fake_write

        engine = KokoroEngine()
        engine.synthesize("test")
        mock_pipeline.assert_called_once_with("test", voice="af_heart")


# --- TTSService Tests ---


class TestTTSService:
    def test_init_has_kokoro_engine(self):
        from apps.voice.tts_service import TTSService

        service = TTSService()
        assert hasattr(service, "engine")

    @patch("apps.voice.tts_service.KokoroEngine")
    def test_synthesize_calls_engine(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        result = service.synthesize("Hello")
        assert result == b"wav-data"
        mock_engine.synthesize.assert_called_once()

    @patch("apps.voice.tts_service.KokoroEngine")
    def test_synthesize_with_voice(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        service.synthesize("Hello", voice="uk")
        mock_engine.synthesize.assert_called_once_with(
            "Hello", voice="bf_emma", lang_code="b"
        )

    @patch("apps.voice.tts_service.KokoroEngine")
    def test_synthesize_nigerian_accent(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        service.synthesize("Hello", voice="nigerian")
        call_kwargs = mock_engine.synthesize.call_args
        assert call_kwargs[1]["lang_code"] == "a"

    @patch("apps.voice.tts_service.KokoroEngine")
    def test_synthesize_ghanaian_accent(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        service.synthesize("Hello", voice="ghanaian")
        call_kwargs = mock_engine.synthesize.call_args
        assert call_kwargs[1]["lang_code"] == "a"

    @patch("apps.voice.tts_service.KokoroEngine")
    def test_synthesize_uk_accent(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        service.synthesize("Hello", voice="uk")
        call_kwargs = mock_engine.synthesize.call_args
        assert call_kwargs[1]["lang_code"] == "b"

    @patch("apps.voice.tts_service.KokoroEngine")
    def test_synthesize_us_accent(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        service.synthesize("Hello", voice="us")
        call_kwargs = mock_engine.synthesize.call_args
        assert call_kwargs[1]["lang_code"] == "a"

    @pytest.mark.asyncio
    @patch("apps.voice.tts_service.KokoroEngine")
    async def test_synthesize_async(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        mock_engine = MagicMock()
        mock_engine.synthesize.return_value = b"wav-data"
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        result = await service.synthesize_async("Hello")
        assert result == b"wav-data"

    @pytest.mark.asyncio
    @patch("apps.voice.tts_service.KokoroEngine")
    async def test_stream_synthesize_yields_chunks(self, mock_engine_cls):
        from apps.voice.tts_service import TTSService

        import numpy as np

        chunk1 = b"chunk1"
        chunk2 = b"chunk2"

        mock_engine = MagicMock()
        mock_engine.synthesize_chunks.return_value = [chunk1, chunk2]
        mock_engine_cls.return_value = mock_engine

        service = TTSService()
        chunks = []
        async for chunk in service.stream_synthesize("Hello"):
            chunks.append(chunk)
        assert len(chunks) == 2
        assert chunks[0] == chunk1
        assert chunks[1] == chunk2

    def test_accent_mapping_exists(self):
        from apps.voice.tts_service import TTSService

        service = TTSService()
        assert "nigerian" in service.accent_voices
        assert "ghanaian" in service.accent_voices
        assert "uk" in service.accent_voices
        assert "us" in service.accent_voices
        assert "japanese" in service.accent_voices


# --- Schema Tests ---


class TestTTSSchemas:
    def test_tts_request_valid(self):
        from apps.voice.schemas import TTSRequest

        req = TTSRequest(text="Hello world")
        assert req.text == "Hello world"
        assert req.voice == "af_heart"

    def test_tts_request_with_voice(self):
        from apps.voice.schemas import TTSRequest

        req = TTSRequest(text="Hello", voice="nigerian")
        assert req.voice == "nigerian"

    def test_tts_request_empty_text_raises(self):
        from apps.voice.schemas import TTSRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TTSRequest(text="")

    def test_tts_response_valid(self):
        from apps.voice.schemas import TTSResponse

        resp = TTSResponse(audio_base64="aGVsbG8=", duration_ms=1500)
        assert resp.audio_base64 == "aGVsbG8="
        assert resp.duration_ms == 1500

    def test_tts_stream_request_valid(self):
        from apps.voice.schemas import TTSStreamRequest

        req = TTSStreamRequest(text="Hello")
        assert req.text == "Hello"
        assert req.voice == "af_heart"


# --- API Endpoint Tests ---


class TestTTSEndpoints:
    @pytest.mark.asyncio
    @patch("apps.voice.router.tts_service.synthesize_async")
    async def test_tts_endpoint_returns_audio(self, mock_synthesize):
        from httpx import AsyncClient, ASGITransport
        from config.app import app

        mock_synthesize.return_value = b"wav-audio-data"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/voice/tts", json={"text": "Hello world"})
        assert resp.status_code == 200
        data = resp.json()
        assert "audio_base64" in data
        assert len(data["audio_base64"]) > 0

    @pytest.mark.asyncio
    @patch("apps.voice.router.tts_service.synthesize_async")
    async def test_tts_endpoint_with_voice(self, mock_synthesize):
        from httpx import AsyncClient, ASGITransport
        from config.app import app

        mock_synthesize.return_value = b"wav-data"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/voice/tts", json={"text": "Hello", "voice": "nigerian"})
        assert resp.status_code == 200
        mock_synthesize.assert_called_once_with(text="Hello", voice="nigerian")

    @pytest.mark.asyncio
    async def test_tts_endpoint_empty_text(self):
        from httpx import AsyncClient, ASGITransport
        from config.app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/voice/tts", json={"text": ""})
        assert resp.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @patch("apps.voice.router.tts_service.stream_synthesize")
    async def test_tts_stream_endpoint(self, mock_stream):
        from httpx import AsyncClient, ASGITransport
        from config.app import app

        async def fake_stream(text, voice):
            yield b"chunk1"
            yield b"chunk2"

        mock_stream.side_effect = fake_stream

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/voice/tts/stream", json={"text": "Hello"})
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "audio/wav"
