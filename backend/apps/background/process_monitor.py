import platform
from typing import Dict, Optional

try:
    import psutil
except ImportError:
    psutil = None


class ProcessMonitor:
    """Monitor system resources: CPU, memory, battery. Determines performance mode."""

    VALID_MODES = ("low_power", "balanced", "high_performance")

    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        battery_low_threshold: float = 20.0,
        sampling_interval_normal: float = 1.0,
        sampling_interval_low_power: float = 5.0,
        sampling_interval_idle: float = 10.0,
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.battery_low_threshold = battery_low_threshold
        self.sampling_interval_normal = sampling_interval_normal
        self.sampling_interval_low_power = sampling_interval_low_power
        self.sampling_interval_idle = sampling_interval_idle
        self.current_mode = "balanced"
        self._last_cpu_percent = 0.0

    def get_cpu_percent(self) -> float:
        """Return current CPU usage percentage."""
        if psutil is None:
            return 0.0
        return psutil.cpu_percent()

    def get_memory_info(self) -> Dict:
        """Return memory usage info."""
        if psutil is None:
            return {"percent": 0.0, "available": 0, "total": 0}
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "available": mem.available,
            "total": mem.total,
        }

    def get_battery_info(self) -> Optional[Dict]:
        """Return battery info, or None if no battery."""
        if psutil is None:
            return None
        battery = psutil.sensors_battery()
        if battery is None:
            return None
        return {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft,
        }

    def get_system_stats(self) -> Dict:
        """Aggregate system stats."""
        cpu = self.get_cpu_percent()
        mem = self.get_memory_info()
        battery = self.get_battery_info()
        self._last_cpu_percent = cpu
        return {
            "cpu_percent": cpu,
            "memory_percent": mem["percent"],
            "battery": battery,
        }

    def determine_performance_mode(self) -> str:
        """Decide performance mode based on current system resources."""
        stats = self.get_system_stats()

        cpu = stats["cpu_percent"]
        mem = stats["memory_percent"]
        battery = stats["battery"]

        if cpu > self.cpu_threshold:
            return "low_power"

        if mem > self.memory_threshold:
            return "low_power"

        if battery and not battery["power_plugged"] and battery["percent"] < self.battery_low_threshold:
            return "low_power"

        if cpu < 30.0 and mem < 50.0:
            if battery and battery["percent"] > 50.0:
                return "high_performance"
            elif not battery:
                return "high_performance"

        return "balanced"

    def get_sampling_interval(self, mode: str) -> float:
        """Return the sampling interval for a given mode."""
        if mode == "low_power":
            return self.sampling_interval_low_power
        elif mode == "idle":
            return self.sampling_interval_idle
        return self.sampling_interval_normal

    def adapt_sampling_rate(self) -> None:
        """Adapt sampling rate based on current system resources."""
        self.current_mode = self.determine_performance_mode()
