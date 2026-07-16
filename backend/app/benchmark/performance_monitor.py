"""Performance monitoring utilities for benchmarking."""

import time
import psutil
from typing import Optional, List
from threading import Thread, Event
from dataclasses import dataclass
from loguru import logger


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    elapsed_time_ms: float
    peak_memory_mb: float
    average_cpu_percent: float
    memory_samples: List[float]
    cpu_samples: List[float]


class PerformanceMonitor:
    """
    Monitor CPU and memory usage during code execution.
    
    Uses psutil to track system resources in real-time.
    """

    def __init__(self, sampling_interval_ms: float = 50):
        """
        Initialize performance monitor.
        
        Args:
            sampling_interval_ms: Interval between samples in milliseconds
        """
        self.sampling_interval = sampling_interval_ms / 1000.0  # Convert to seconds
        self._monitoring = False
        self._monitor_thread: Optional[Thread] = None
        self._stop_event = Event()
        
        # Metrics storage
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Process reference
        self.process = psutil.Process()

    def start(self) -> None:
        """Start monitoring CPU and memory usage."""
        if self._monitoring:
            logger.warning("Performance monitor already running")
            return
        
        # Reset metrics
        self.memory_samples = []
        self.cpu_samples = []
        self.start_time = time.time()
        self.end_time = None
        self._stop_event.clear()
        
        # Start monitoring thread
        self._monitoring = True
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.debug("Performance monitoring started")

    def stop(self) -> PerformanceMetrics:
        """
        Stop monitoring and return collected metrics.
        
        Returns:
            PerformanceMetrics with collected data
        """
        if not self._monitoring:
            logger.warning("Performance monitor not running")
            return PerformanceMetrics(
                elapsed_time_ms=0.0,
                peak_memory_mb=0.0,
                average_cpu_percent=0.0,
                memory_samples=[],
                cpu_samples=[],
            )
        
        # Stop monitoring
        self.end_time = time.time()
        self._monitoring = False
        self._stop_event.set()
        
        # Wait for monitoring thread to finish
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        
        # Calculate metrics
        elapsed_time_ms = (self.end_time - self.start_time) * 1000.0
        peak_memory_mb = max(self.memory_samples) if self.memory_samples else 0.0
        average_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
        
        logger.debug(
            f"Performance monitoring stopped: "
            f"time={elapsed_time_ms:.2f}ms, "
            f"peak_mem={peak_memory_mb:.2f}MB, "
            f"avg_cpu={average_cpu:.2f}%"
        )
        
        return PerformanceMetrics(
            elapsed_time_ms=elapsed_time_ms,
            peak_memory_mb=peak_memory_mb,
            average_cpu_percent=average_cpu,
            memory_samples=self.memory_samples.copy(),
            cpu_samples=self.cpu_samples.copy(),
        )

    def _monitor_loop(self) -> None:
        """Internal monitoring loop running in separate thread."""
        while self._monitoring and not self._stop_event.is_set():
            try:
                # Get memory usage in MB
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                self.memory_samples.append(memory_mb)
                
                # Get CPU usage percentage
                # cpu_percent() needs a small interval to calculate
                cpu_percent = self.process.cpu_percent(interval=None)
                self.cpu_samples.append(cpu_percent)
                
                # Wait for next sample
                self._stop_event.wait(timeout=self.sampling_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                break

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
