"""Frame consumer interfaces for preview, detection, snapshot, and metrics."""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod

from app.services.frame_bus import FramePacket, FrameQueue


class FrameConsumer(ABC):
    @abstractmethod
    def consume(self, packet: FramePacket) -> None:
        """Execute consume.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        raise NotImplementedError


class SnapshotConsumer:
    """Fetch immutable copy of latest frame without pausing capture/detection."""

    def __init__(self, frame_queue: FrameQueue):
        """Execute   init  .
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self._queue = frame_queue

    def capture_snapshot(self) -> FramePacket | None:
        """Execute capture snapshot.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        packet = self._queue.peek_latest()
        if not packet:
            return None
        return FramePacket(timestamp=packet.timestamp, payload=bytes(packet.payload), stale=packet.stale)


class DetectionConsumer:
    def __init__(self):
        """Execute   init  .
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self._paused = threading.Event()
        self._paused.clear()

    def pause(self) -> None:
        """Execute pause.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self._paused.set()

    def resume(self) -> None:
        """Execute resume.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self._paused.clear()

    def is_paused(self) -> bool:
        """Execute is paused.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        return self._paused.is_set()


class MetricsConsumer:
    def __init__(self):
        """Execute   init  .
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self.capture_fps = 0.0
        self.last_ts = time.time()
        self.frames = 0

    def on_frame(self):
        """Execute on frame.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self.frames += 1
        now = time.time()
        delta = now - self.last_ts
        if delta >= 1.0:
            self.capture_fps = self.frames / delta
            self.frames = 0
            self.last_ts = now
