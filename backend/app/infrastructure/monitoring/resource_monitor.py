"""System resource monitoring using psutil."""

import psutil
from typing import Dict


class ResourceMonitor:
    """Monitor system resources like CPU, memory, and disk usage."""

    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get memory usage statistics."""
        memory = psutil.virtual_memory()
        return {
            "percent": memory.percent,
            "used_mb": memory.used / (1024 * 1024),
            "available_mb": memory.available / (1024 * 1024),
            "total_mb": memory.total / (1024 * 1024),
        }

    @staticmethod
    def get_disk_usage() -> Dict[str, float]:
        """Get disk usage statistics."""
        disk = psutil.disk_usage("/")
        return {
            "percent": disk.percent,
            "used_gb": disk.used / (1024 * 1024 * 1024),
            "free_gb": disk.free / (1024 * 1024 * 1024),
            "total_gb": disk.total / (1024 * 1024 * 1024),
        }

    @classmethod
    def get_all_stats(cls) -> Dict[str, any]:
        """Get all system statistics."""
        return {
            "cpu_percent": cls.get_cpu_usage(),
            "memory": cls.get_memory_usage(),
            "disk": cls.get_disk_usage(),
        }
