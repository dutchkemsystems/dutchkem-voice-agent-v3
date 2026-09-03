import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock


# --- ProcessMonitor Initialization Tests ---

def test_process_monitor_init_defaults():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    assert monitor.cpu_threshold == 80.0
    assert monitor.memory_threshold == 85.0
    assert monitor.battery_low_threshold == 20.0
    assert monitor.sampling_interval_normal == 1.0
    assert monitor.sampling_interval_low_power == 5.0
    assert monitor.sampling_interval_idle == 10.0
    assert monitor.current_mode == "balanced"


def test_process_monitor_init_custom_thresholds():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor(
        cpu_threshold=70.0,
        memory_threshold=80.0,
        battery_low_threshold=30.0,
    )
    assert monitor.cpu_threshold == 70.0
    assert monitor.memory_threshold == 80.0
    assert monitor.battery_low_threshold == 30.0


# --- ProcessMonitor System Stats Tests ---

def test_process_monitor_get_cpu_percent():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 45.2
        result = monitor.get_cpu_percent()
        assert result == 45.2
        mock_psutil.cpu_percent.assert_called_once()


def test_process_monitor_get_memory_info():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_mem = MagicMock()
        mock_mem.percent = 62.5
        mock_mem.available = 8 * 1024 * 1024 * 1024
        mock_mem.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_mem
        result = monitor.get_memory_info()
        assert result["percent"] == 62.5
        assert "available" in result
        assert "total" in result


def test_process_monitor_get_battery_info_no_battery():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.sensors_battery.return_value = None
        result = monitor.get_battery_info()
        assert result is None


def test_process_monitor_get_battery_info_with_battery():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_battery = MagicMock()
        mock_battery.percent = 75.0
        mock_battery.power_plugged = True
        mock_battery.secsleft = 7200
        mock_psutil.sensors_battery.return_value = mock_battery
        result = monitor.get_battery_info()
        assert result["percent"] == 75.0
        assert result["power_plugged"] is True
        assert result["secsleft"] == 7200


def test_process_monitor_get_system_stats():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 35.0
        mock_mem = MagicMock()
        mock_mem.percent = 55.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_psutil.sensors_battery.return_value = None

        result = monitor.get_system_stats()
        assert "cpu_percent" in result
        assert "memory_percent" in result
        assert "battery" in result
        assert result["cpu_percent"] == 35.0
        assert result["memory_percent"] == 55.0
        assert result["battery"] is None


# --- ProcessMonitor Performance Mode Tests ---

def test_process_monitor_mode_low_power_high_cpu():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 90.0
        mock_mem = MagicMock()
        mock_mem.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_psutil.sensors_battery.return_value = None

        mode = monitor.determine_performance_mode()
        assert mode == "low_power"


def test_process_monitor_mode_low_power_low_battery():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 30.0
        mock_mem = MagicMock()
        mock_mem.percent = 40.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_battery = MagicMock()
        mock_battery.percent = 15.0
        mock_battery.power_plugged = False
        mock_psutil.sensors_battery.return_value = mock_battery

        mode = monitor.determine_performance_mode()
        assert mode == "low_power"


def test_process_monitor_mode_low_power_high_memory():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 40.0
        mock_mem = MagicMock()
        mock_mem.percent = 92.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_psutil.sensors_battery.return_value = None

        mode = monitor.determine_performance_mode()
        assert mode == "low_power"


def test_process_monitor_mode_high_performance():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 15.0
        mock_mem = MagicMock()
        mock_mem.percent = 30.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_battery = MagicMock()
        mock_battery.percent = 90.0
        mock_battery.power_plugged = True
        mock_psutil.sensors_battery.return_value = mock_battery

        mode = monitor.determine_performance_mode()
        assert mode == "high_performance"


def test_process_monitor_mode_balanced():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 50.0
        mock_mem = MagicMock()
        mock_mem.percent = 60.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_battery = MagicMock()
        mock_battery.percent = 60.0
        mock_battery.power_plugged = True
        mock_psutil.sensors_battery.return_value = mock_battery

        mode = monitor.determine_performance_mode()
        assert mode == "balanced"


# --- ProcessMonitor Sampling Interval Tests ---

def test_process_monitor_get_sampling_interval_normal():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    interval = monitor.get_sampling_interval("balanced")
    assert interval == 1.0


def test_process_monitor_get_sampling_interval_low_power():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    interval = monitor.get_sampling_interval("low_power")
    assert interval == 5.0


def test_process_monitor_get_sampling_interval_idle():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    interval = monitor.get_sampling_interval("idle")
    assert interval == 10.0


def test_process_monitor_adapt_sampling_updates_mode():
    from apps.background.process_monitor import ProcessMonitor
    monitor = ProcessMonitor()
    with patch("apps.background.process_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 90.0
        mock_mem = MagicMock()
        mock_mem.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_psutil.sensors_battery.return_value = None

        monitor.adapt_sampling_rate()
        assert monitor.current_mode == "low_power"


# --- BackgroundServiceManager Initialization Tests ---

def test_service_manager_init_defaults():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    assert mgr.is_running is False
    assert mgr.performance_mode == "balanced"
    assert mgr.audio_monitor is not None
    assert mgr.video_monitor is not None
    assert mgr.trigger_detector is not None
    assert mgr.interview_engine is None


def test_service_manager_init_custom_audio_monitor():
    from apps.background.service_manager import BackgroundServiceManager
    from apps.background.audio_monitor import AudioMonitor
    custom = AudioMonitor(sample_rate=44100)
    mgr = BackgroundServiceManager(audio_monitor=custom)
    assert mgr.audio_monitor is custom
    assert mgr.audio_monitor.sample_rate == 44100


def test_service_manager_init_custom_video_monitor():
    from apps.background.service_manager import BackgroundServiceManager
    from apps.background.video_monitor import VideoMonitor
    custom = VideoMonitor(camera_index=2)
    mgr = BackgroundServiceManager(video_monitor=custom)
    assert mgr.video_monitor is custom
    assert mgr.video_monitor.camera_index == 2


# --- BackgroundServiceManager Start/Stop Tests ---

@pytest.mark.asyncio
async def test_service_manager_start_sets_running():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.audio_monitor, "start", new_callable=AsyncMock) as mock_a_start, \
         patch.object(mgr.video_monitor, "start", new_callable=AsyncMock) as mock_v_start:
        task = asyncio.create_task(mgr.start())
        await asyncio.sleep(0.05)
        assert mgr.is_running is True
        mgr.stop()
        await asyncio.sleep(0.05)
        mock_a_start.assert_called_once()
        mock_v_start.assert_called_once()


@pytest.mark.asyncio
async def test_service_manager_stop_sets_running_false():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.audio_monitor, "start", new_callable=AsyncMock), \
         patch.object(mgr.video_monitor, "start", new_callable=AsyncMock):
        task = asyncio.create_task(mgr.start())
        await asyncio.sleep(0.05)
        assert mgr.is_running is True

        mgr.stop()
        await asyncio.sleep(0.05)
        assert mgr.is_running is False


@pytest.mark.asyncio
async def test_service_manager_stop_stops_monitors():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.audio_monitor, "start", new_callable=AsyncMock), \
         patch.object(mgr.video_monitor, "start", new_callable=AsyncMock), \
         patch.object(mgr.audio_monitor, "stop") as mock_a_stop, \
         patch.object(mgr.video_monitor, "stop") as mock_v_stop:
        task = asyncio.create_task(mgr.start())
        await asyncio.sleep(0.05)

        mgr.stop()
        await asyncio.sleep(0.05)
        mock_a_stop.assert_called_once()
        mock_v_stop.assert_called_once()


@pytest.mark.asyncio
async def test_service_manager_restart():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.audio_monitor, "start", new_callable=AsyncMock) as mock_a_start, \
         patch.object(mgr.video_monitor, "start", new_callable=AsyncMock) as mock_v_start, \
         patch.object(mgr.audio_monitor, "stop") as mock_a_stop, \
         patch.object(mgr.video_monitor, "stop") as mock_v_stop:
        # Start first
        task = asyncio.create_task(mgr.start())
        await asyncio.sleep(0.05)
        assert mgr.is_running is True

        mgr.stop()
        await asyncio.sleep(0.05)
        assert mgr.is_running is False

        # Restart
        task2 = asyncio.create_task(mgr.start())
        await asyncio.sleep(0.05)
        assert mgr.is_running is True

        mgr.stop()
        await asyncio.sleep(0.05)

        # Start was called twice (once per start)
        assert mock_a_start.call_count == 2
        assert mock_v_start.call_count == 2
        # Stop was called twice (once per stop)
        assert mock_a_stop.call_count == 2
        assert mock_v_stop.call_count == 2


# --- BackgroundServiceManager Stats Tests ---

def test_service_manager_get_system_stats():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "get_system_stats") as mock_stats:
        mock_stats.return_value = {
            "cpu_percent": 45.0,
            "memory_percent": 60.0,
            "battery": {"percent": 80.0, "power_plugged": True},
        }
        result = mgr.get_system_stats()
        assert result["cpu_percent"] == 45.0
        assert result["memory_percent"] == 60.0
        mock_stats.assert_called_once()


# --- BackgroundServiceManager Performance Mode Tests ---

def test_service_manager_set_performance_mode():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    mgr.set_performance_mode("low_power")
    assert mgr.performance_mode == "low_power"

    mgr.set_performance_mode("high_performance")
    assert mgr.performance_mode == "high_performance"

    mgr.set_performance_mode("balanced")
    assert mgr.performance_mode == "balanced"


def test_service_manager_set_performance_mode_invalid():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    with pytest.raises(ValueError):
        mgr.set_performance_mode("turbo")


# --- BackgroundServiceManager Adaptive Sampling Tests ---

def test_service_manager_adapt_sampling_low_power():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "determine_performance_mode", return_value="low_power"):
        mgr.adapt_sampling_rate()
        assert mgr.performance_mode == "low_power"


def test_service_manager_adapt_sampling_high_performance():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "determine_performance_mode", return_value="high_performance"):
        mgr.adapt_sampling_rate()
        assert mgr.performance_mode == "high_performance"


def test_service_manager_adapt_sampling_balanced():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "determine_performance_mode", return_value="balanced"):
        mgr.adapt_sampling_rate()
        assert mgr.performance_mode == "balanced"


# --- BackgroundServiceManager Interview Engine Tests ---

def test_service_manager_set_interview_engine():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    mock_engine = MagicMock()
    mgr.set_interview_engine(mock_engine)
    assert mgr.interview_engine is mock_engine


# --- BackgroundServiceManager Trigger Integration Tests ---

def test_service_manager_analyze_transcript():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    result = mgr.analyze_transcript("Can you tell me about your experience with Python?")
    assert "phase" in result
    assert "score" in result
    assert "should_activate" in result


def test_service_manager_reset_trigger_detector():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    # Trigger some analysis first
    mgr.analyze_transcript("Tell me about your background")
    mgr.analyze_transcript("What experience do you have?")

    mgr.reset_trigger_detector()
    assert mgr.trigger_detector.phase.value == "idle"
    assert len(mgr.trigger_detector.conversation_history) == 0


# --- BackgroundServiceManager Audio Callback Integration ---

def test_service_manager_audio_callback():
    from apps.background.service_manager import BackgroundServiceManager
    import numpy as np
    mgr = BackgroundServiceManager()

    # Set up speech callback
    speech_events = []

    async def on_speech(data):
        speech_events.append(data)

    mgr.audio_monitor.on_speech_detected = on_speech

    # Simulate audio frame
    frames = 480
    indata = np.random.rand(frames, 1).astype(np.float32)
    from unittest.mock import MagicMock
    time_info = MagicMock()
    status = MagicMock()

    mgr.audio_monitor.audio_callback(indata, frames, time_info, status)
    assert not mgr.audio_monitor._audio_queue.empty()


# --- BackgroundServiceManager Stats Tracking ---

def test_service_manager_get_stats():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    stats = mgr.get_stats()
    assert "is_running" in stats
    assert "performance_mode" in stats
    assert "trigger_phase" in stats
    assert "audio_running" in stats
    assert "video_running" in stats
    assert stats["is_running"] is False
    assert stats["performance_mode"] == "balanced"
    assert stats["trigger_phase"] == "idle"


# --- BackgroundServiceManager Process Monitor Integration ---

def test_service_manager_has_process_monitor():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    assert mgr.process_monitor is not None


def test_service_manager_process_monitor_custom():
    from apps.background.service_manager import BackgroundServiceManager
    from apps.background.process_monitor import ProcessMonitor
    custom = ProcessMonitor(cpu_threshold=70.0)
    mgr = BackgroundServiceManager(process_monitor=custom)
    assert mgr.process_monitor is custom
    assert mgr.process_monitor.cpu_threshold == 70.0


# --- BackgroundServiceManager Battery Warning Tests ---

def test_service_manager_battery_warning_low_battery():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "get_battery_info") as mock_battery:
        mock_battery.return_value = {"percent": 15.0, "power_plugged": False}
        warnings = mgr.check_battery_warnings()
        assert len(warnings) > 0
        assert any("low" in w.lower() or "battery" in w.lower() for w in warnings)


def test_service_manager_battery_warning_ok():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "get_battery_info") as mock_battery:
        mock_battery.return_value = {"percent": 85.0, "power_plugged": True}
        warnings = mgr.check_battery_warnings()
        assert len(warnings) == 0


def test_service_manager_battery_warning_no_battery():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.process_monitor, "get_battery_info") as mock_battery:
        mock_battery.return_value = None
        warnings = mgr.check_battery_warnings()
        assert len(warnings) == 0


# --- System Service Integration Tests ---

def test_service_manager_get_systemd_config():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    config = mgr.get_systemd_config()
    assert "[Unit]" in config
    assert "[Service]" in config
    assert "[Install]" in config


def test_service_manager_get_launchd_config():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    config = mgr.get_launchd_config()
    assert "Label" in config
    assert "ProgramArguments" in config


def test_service_manager_get_windows_service_config():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()
    config = mgr.get_windows_service_config()
    assert "name" in config
    assert "display_name" in config
    assert "description" in config


# --- Integration: Full Service Lifecycle ---

@pytest.mark.asyncio
async def test_full_service_lifecycle():
    from apps.background.service_manager import BackgroundServiceManager
    mgr = BackgroundServiceManager()

    with patch.object(mgr.audio_monitor, "start", new_callable=AsyncMock), \
         patch.object(mgr.video_monitor, "start", new_callable=AsyncMock), \
         patch.object(mgr.audio_monitor, "stop"), \
         patch.object(mgr.video_monitor, "stop"), \
         patch.object(mgr.process_monitor, "get_system_stats", return_value={
             "cpu_percent": 50.0,
             "memory_percent": 60.0,
             "battery": None,
         }):

        # Start
        task = asyncio.create_task(mgr.start())
        await asyncio.sleep(0.05)
        assert mgr.is_running is True

        # Check stats while running
        stats = mgr.get_system_stats()
        assert stats["cpu_percent"] == 50.0

        # Adapt sampling
        with patch.object(mgr.process_monitor, "determine_performance_mode", return_value="balanced"):
            mgr.adapt_sampling_rate()
            assert mgr.performance_mode == "balanced"

        # Analyze transcript
        result = mgr.analyze_transcript("Tell me about your experience")
        assert "phase" in result

        # Stop
        mgr.stop()
        await asyncio.sleep(0.05)
        assert mgr.is_running is False
