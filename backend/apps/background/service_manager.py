import platform
import sys
from typing import Dict, List, Optional

from apps.background.audio_monitor import AudioMonitor
from apps.background.video_monitor import VideoMonitor
from apps.background.trigger_detector import InterviewTriggerDetector
from apps.background.process_monitor import ProcessMonitor


class BackgroundServiceManager:
    """Coordinate background audio/video monitoring and interview trigger detection."""

    VALID_MODES = ("low_power", "balanced", "high_performance")

    def __init__(
        self,
        audio_monitor: Optional[AudioMonitor] = None,
        video_monitor: Optional[VideoMonitor] = None,
        trigger_detector: Optional[InterviewTriggerDetector] = None,
        process_monitor: Optional[ProcessMonitor] = None,
    ):
        self.audio_monitor = audio_monitor or AudioMonitor()
        self.video_monitor = video_monitor or VideoMonitor()
        self.trigger_detector = trigger_detector or InterviewTriggerDetector()
        self.process_monitor = process_monitor or ProcessMonitor()
        self.interview_engine = None
        self.is_running = False
        self.performance_mode = "balanced"

    def set_interview_engine(self, engine) -> None:
        """Set the interview engine reference."""
        self.interview_engine = engine

    def set_performance_mode(self, mode: str) -> None:
        """Set performance mode explicitly."""
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {self.VALID_MODES}")
        self.performance_mode = mode

    async def start(self) -> None:
        """Start all background services."""
        if self.is_running:
            return
        self.is_running = True

        import asyncio
        await asyncio.gather(
            self.audio_monitor.start(),
            self.video_monitor.start(),
        )

    def stop(self) -> None:
        """Stop all background services."""
        self.is_running = False
        self.audio_monitor.stop()
        self.video_monitor.stop()

    def get_system_stats(self) -> Dict:
        """Get current system resource usage."""
        return self.process_monitor.get_system_stats()

    def adapt_sampling_rate(self) -> None:
        """Adapt monitoring rate based on system resources."""
        self.performance_mode = self.process_monitor.determine_performance_mode()

    def analyze_transcript(self, transcript: str) -> Dict:
        """Analyze a transcript segment for interview triggers."""
        return self.trigger_detector.analyze_transcript(transcript)

    def reset_trigger_detector(self) -> None:
        """Reset the trigger detector state."""
        self.trigger_detector.reset()

    def check_battery_warnings(self) -> List[str]:
        """Check battery status and return warning messages."""
        warnings = []
        battery = self.process_monitor.get_battery_info()
        if battery is None:
            return warnings
        if battery["percent"] < 20 and not battery["power_plugged"]:
            warnings.append(f"Low battery: {battery['percent']}%. Consider plugging in.")
        if battery["percent"] < 10 and not battery["power_plugged"]:
            warnings.append("Critical battery level! Services may be paused.")
        return warnings

    def get_stats(self) -> Dict:
        """Get current service manager stats."""
        return {
            "is_running": self.is_running,
            "performance_mode": self.performance_mode,
            "trigger_phase": self.trigger_detector.phase.value,
            "audio_running": self.audio_monitor.is_running,
            "video_running": self.video_monitor.is_running,
        }

    def get_systemd_config(self) -> str:
        """Generate a systemd unit file for this service."""
        python_path = sys.executable
        return (
            "[Unit]\n"
            "Description=DutchKem Voice Agent Background Service\n"
            "After=network.target\n\n"
            "[Service]\n"
            f"ExecStart={python_path} -m apps.background.service_manager\n"
            "Restart=always\n"
            "RestartSec=5\n"
            "User=dutchkem\n"
            "WorkingDirectory=/opt/dutchkem-voice-agent\n\n"
            "[Install]\n"
            "WantedBy=multi-user.target\n"
        )

    def get_launchd_config(self) -> str:
        """Generate a launchd plist for macOS."""
        python_path = sys.executable
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"'
            ' "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            '<plist version="1.0">\n'
            "<dict>\n"
            "    <key>Label</key>\n"
            "    <string>com.dutchkem.voice-agent</string>\n"
            "    <key>ProgramArguments</key>\n"
            "    <array>\n"
            f"        <string>{python_path}</string>\n"
            "        <string>-m</string>\n"
            "        <string>apps.background.service_manager</string>\n"
            "    </array>\n"
            "    <key>RunAtLoad</key>\n"
            "    <true/>\n"
            "    <key>KeepAlive</key>\n"
            "    <true/>\n"
            "</dict>\n"
            "</plist>\n"
        )

    def get_windows_service_config(self) -> Dict:
        """Return Windows service configuration."""
        return {
            "name": "DutchKemVoiceAgent",
            "display_name": "DutchKem Voice Agent Background Service",
            "description": "Monitors audio/video and detects interview triggers in background.",
            "start_type": "auto",
            "python_path": sys.executable,
        }
