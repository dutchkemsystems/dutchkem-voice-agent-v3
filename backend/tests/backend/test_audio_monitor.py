import pytest
import numpy as np
import asyncio
import queue
from unittest.mock import patch, MagicMock, AsyncMock


# --- AudioMonitor Initialization Tests ---

def test_audio_monitor_init_defaults():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    assert monitor.sample_rate == 16000
    assert monitor.channels == 1
    assert monitor.is_running is False
    assert monitor.on_speech_detected is None
    assert monitor.on_silence_detected is None


def test_audio_monitor_init_custom_rate():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor(sample_rate=44100, channels=2)
    assert monitor.sample_rate == 44100
    assert monitor.channels == 2


def test_audio_monitor_init_vad():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    assert monitor.vad is not None


def test_audio_monitor_init_queue():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    assert isinstance(monitor._audio_queue, queue.Queue)


# --- AudioMonitor VAD Tests ---

def test_audio_monitor_vad_detects_speech():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    # Create synthetic speech-like signal (sine wave)
    t = np.linspace(0, 0.3, 4800)  # 0.3s at 16kHz
    audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    audio_bytes = audio.tobytes()
    is_speech = monitor.vad.is_speech(audio_bytes, 16000)
    assert isinstance(is_speech, bool)


def test_audio_monitor_vad_detects_silence():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    # Create silence
    audio = np.zeros(4800, dtype=np.int16)
    audio_bytes = audio.tobytes()
    is_speech = monitor.vad.is_speech(audio_bytes, 16000)
    assert isinstance(is_speech, bool)


# --- AudioMonitor Callback Tests ---

def test_audio_callback_processes_audio():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    # Create mock audio input
    frames = 480  # 30ms at 16kHz
    indata = np.random.rand(frames, 1).astype(np.float32)
    time_info = MagicMock()
    status = MagicMock()

    monitor.audio_callback(indata, frames, time_info, status)
    assert not monitor._audio_queue.empty()


def test_audio_callback_converts_int16():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    frames = 480
    indata = np.zeros((frames, 1), dtype=np.float32)
    time_info = MagicMock()
    status = MagicMock()

    monitor.audio_callback(indata, frames, time_info, status)
    audio_data, is_speech = monitor._audio_queue.get_nowait()
    assert audio_data.dtype == np.int16


# --- AudioMonitor Queue Processing Tests ---

@pytest.mark.asyncio
async def test_process_queue_speech_callback():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    callback_called = []

    async def on_speech(audio_data):
        callback_called.append(audio_data)

    monitor.on_speech_detected = on_speech
    monitor.is_running = True

    # Put speech audio in queue
    audio = np.zeros(4800, dtype=np.int16)
    monitor._audio_queue.put((audio, True))

    task = asyncio.create_task(monitor._process_queue())
    await asyncio.sleep(0.1)
    monitor.is_running = False
    await asyncio.sleep(0.1)

    assert len(callback_called) == 1


@pytest.mark.asyncio
async def test_process_queue_silence_callback():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    callback_called = []

    async def on_silence():
        callback_called.append(True)

    monitor.on_silence_detected = on_silence
    monitor.is_running = True

    # Put silence in queue
    audio = np.zeros(4800, dtype=np.int16)
    monitor._audio_queue.put((audio, False))

    task = asyncio.create_task(monitor._process_queue())
    await asyncio.sleep(0.1)
    monitor.is_running = False
    await asyncio.sleep(0.1)

    assert len(callback_called) == 1


@pytest.mark.asyncio
async def test_process_queue_empty():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    monitor.is_running = True

    # Empty queue - should not crash
    task = asyncio.create_task(monitor._process_queue())
    await asyncio.sleep(0.1)
    monitor.is_running = False
    await asyncio.sleep(0.1)
    # No exception = pass


# --- AudioMonitor Start/Stop Tests ---

@pytest.mark.asyncio
async def test_audio_monitor_start_sets_running():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()

    with patch("apps.background.audio_monitor.sd") as mock_sd:
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_sd.InputStream.return_value = mock_stream

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)
        assert monitor.is_running is True
        monitor.stop()
        await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_audio_monitor_stop_sets_running_false():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()

    with patch("apps.background.audio_monitor.sd") as mock_sd:
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_sd.InputStream.return_value = mock_stream

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)
        assert monitor.is_running is True
        monitor.stop()
        await asyncio.sleep(0.1)
        assert monitor.is_running is False


# --- NoiseFilter Tests ---

def test_noise_filter_init():
    from apps.background.noise_filter import NoiseFilter
    nf = NoiseFilter()
    assert nf.sample_rate == 16000


def test_noise_filter_init_custom_rate():
    from apps.background.noise_filter import NoiseFilter
    nf = NoiseFilter(sample_rate=44100)
    assert nf.sample_rate == 44100


def test_noise_filter_reduce():
    from apps.background.noise_filter import NoiseFilter
    nf = NoiseFilter()
    audio = np.random.rand(4800).astype(np.int16)
    result = nf.reduce(audio)
    assert result.dtype == np.int16
    assert len(result) == len(audio)


def test_noise_filter_reduce_empty():
    from apps.background.noise_filter import NoiseFilter
    nf = NoiseFilter()
    audio = np.array([], dtype=np.int16)
    result = nf.reduce(audio)
    assert len(result) == 0


def test_noise_filter_reduce_preserves_shape():
    from apps.background.noise_filter import NoiseFilter
    nf = NoiseFilter()
    audio = np.random.rand(9600).astype(np.int16)
    result = nf.reduce(audio)
    assert result.shape == audio.shape


# --- VoiceBiometrics Tests ---

def test_voice_biometrics_init():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    assert vb.registered_voices == {}
    assert vb.similarity_threshold == 0.75


def test_voice_biometrics_init_custom_threshold():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics(similarity_threshold=0.85)
    assert vb.similarity_threshold == 0.85


def test_voice_biometrics_register_voice():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    embedding = np.random.rand(256)
    vb.register_voice("user-1", embedding)
    assert "user-1" in vb.registered_voices


def test_voice_biometrics_verify_match():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    embedding = np.random.rand(256)
    vb.register_voice("user-1", embedding)

    # Slightly perturbed embedding
    test_emb = embedding + np.random.normal(0, 0.001, 256)
    user_id, confidence = vb.verify_voice(test_emb)
    assert user_id == "user-1"
    assert confidence > 0.9


def test_voice_biometrics_verify_no_match():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    embedding = np.random.rand(256)
    vb.register_voice("user-1", embedding)

    random_embedding = np.random.rand(256)

    with patch.object(vb, "_compute_similarity") as mock_sim:
        mock_sim.return_value = 0.3
        user_id, confidence = vb.verify_voice(random_embedding)
        assert user_id is None
        assert confidence < 0.5


def test_voice_biometrics_verify_empty_registry():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    embedding = np.random.rand(256)
    user_id, confidence = vb.verify_voice(embedding)
    assert user_id is None
    assert confidence == 0.0


def test_voice_biometrics_extract_embedding():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    audio = np.random.rand(16000).astype(np.int16)  # 1s of audio
    embedding = vb.extract_embedding(audio)
    assert embedding is not None
    assert len(embedding) == 256


def test_voice_biometrics_compute_similarity_identical():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    emb = np.random.rand(256)
    sim = vb._compute_similarity(emb, emb)
    assert abs(sim - 1.0) < 0.001


def test_voice_biometrics_compute_similarity_orthogonal():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    emb1 = np.array([1.0] + [0.0] * 255)
    emb2 = np.array([0.0] * 255 + [1.0])
    sim = vb._compute_similarity(emb1, emb2)
    assert abs(sim) < 0.001


def test_voice_biometrics_compute_similarity_zero():
    from apps.background.voice_biometrics import VoiceBiometrics
    vb = VoiceBiometrics()
    emb1 = np.zeros(256)
    emb2 = np.random.rand(256)
    sim = vb._compute_similarity(emb1, emb2)
    assert sim == 0.0


# --- Adaptive Sampling Tests ---

def test_audio_monitor_adaptive_sampling_init():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    assert hasattr(monitor, 'adaptive_sampling')
    assert monitor.adaptive_sampling is True


def test_audio_monitor_battery_optimization():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    monitor.set_battery_level(0.5)
    assert monitor.battery_level == 0.5


def test_audio_monitor_cpu_optimization():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    monitor.set_cpu_threshold(0.8)
    assert monitor.cpu_threshold == 0.8


def test_audio_monitor_get_sampling_rate_low_battery():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    monitor.set_battery_level(0.1)
    rate = monitor.get_optimal_sample_rate()
    assert rate <= 16000


def test_audio_monitor_get_sampling_rate_high_battery():
    from apps.background.audio_monitor import AudioMonitor
    monitor = AudioMonitor()
    monitor.set_battery_level(1.0)
    rate = monitor.get_optimal_sample_rate()
    assert rate >= 16000


# --- Async Pipeline Tests ---

@pytest.mark.asyncio
async def test_audio_monitor_pipeline_integration():
    from apps.background.audio_monitor import AudioMonitor
    from apps.background.noise_filter import NoiseFilter
    from apps.background.voice_biometrics import VoiceBiometrics

    monitor = AudioMonitor()
    nf = NoiseFilter()
    vb = VoiceBiometrics()

    # Verify components can work together
    audio = np.random.rand(4800).astype(np.int16)
    filtered = nf.reduce(audio)
    assert filtered is not None
    assert len(filtered) == len(audio)
