"""Tests for global FFmpeg capture lifecycle behavior."""
import subprocess
import sys
import unittest
from unittest import mock

from app.services.ffmpeg_tools import CaptureConfig


def _module_importable(module: str) -> bool:
    """Return True when module can be imported in a subprocess."""
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


CV2_AVAILABLE = _module_importable("cv2")


class DummyProcess:
    def poll(self):
        return None


class DummyCapture:
    created = 0

    def __init__(self, input_token, config, frame_queue, allow_input_tuning=True, pipeline="monitoring"):
        self.device_name = input_token
        self.config = config
        self.queue = frame_queue
        self.allow_input_tuning = allow_input_tuning
        self.pipeline = pipeline
        self.process = DummyProcess()
        self.stop_calls = 0
        self.last_error = None
        DummyCapture.created += 1

    def start(self):
        return None

    def stop(self):
        self.stop_calls += 1

    def is_alive(self):
        return True


def _reset_globals(monitor_service):
    monitor_service._GLOBAL_CAPTURE = None
    monitor_service._GLOBAL_QUEUE = None
    monitor_service._GLOBAL_INPUT_TOKEN = None
    monitor_service._GLOBAL_CONFIG = None
    monitor_service._GLOBAL_USERS = 0
    monitor_service._PREVIEW_CAPTURE = None
    monitor_service._PREVIEW_QUEUE = None
    monitor_service._PREVIEW_INPUT_TOKEN = None
    monitor_service._PREVIEW_CONFIG = None
    monitor_service._PREVIEW_PAUSED_FOR_MONITORING = False
    monitor_service._PREVIEW_LAST_RESTART_AT = 0.0


@unittest.skipUnless(CV2_AVAILABLE, "OpenCV unavailable in test environment")
class MonitorCaptureTests(unittest.TestCase):
    """Validate reference counting and idempotent stop behavior."""

    def setUp(self):
        import app.services.monitor_service as monitor_service

        self.monitor_service = monitor_service
        _reset_globals(monitor_service)
        DummyCapture.created = 0

    def tearDown(self):
        _reset_globals(self.monitor_service)

    def test_global_capture_reference_counting(self):
        """Ensure global capture is stopped only after last release."""
        config = CaptureConfig(width=1280, height=720, fps=30)
        with mock.patch.object(self.monitor_service, "FfmpegCapture", DummyCapture):
            cap1, _ = self.monitor_service._ensure_global_capture("camera-1", config, allow_input_tuning=False)
            cap2, _ = self.monitor_service._ensure_global_capture("camera-1", config, allow_input_tuning=False)
            self.assertIs(cap1, cap2)
            self.assertEqual(self.monitor_service._GLOBAL_USERS, 2)

            self.monitor_service._release_global_capture()
            self.assertEqual(self.monitor_service._GLOBAL_USERS, 1)
            self.assertEqual(cap1.stop_calls, 0)

            self.monitor_service._release_global_capture()
            self.assertEqual(self.monitor_service._GLOBAL_USERS, 0)
            self.assertEqual(cap1.stop_calls, 1)

    def test_start_stop_start_creates_new_capture(self):
        """Ensure new capture starts after all users release."""
        config = CaptureConfig(width=1280, height=720, fps=30)
        with mock.patch.object(self.monitor_service, "FfmpegCapture", DummyCapture):
            cap1, _ = self.monitor_service._ensure_global_capture("camera-1", config, allow_input_tuning=False)
            self.monitor_service._release_global_capture()
            cap2, _ = self.monitor_service._ensure_global_capture("camera-1", config, allow_input_tuning=False)
            self.assertIsNot(cap1, cap2)
            self.assertEqual(DummyCapture.created, 2)

    def test_monitor_stop_is_idempotent(self):
        """Ensure stop can be called twice without double-release."""
        service = self.monitor_service.MonitorService()
        service._capture = DummyCapture("camera-1", CaptureConfig(1, 1, 1), None)
        service._capture_acquired = True

        with mock.patch.object(self.monitor_service, "_release_global_capture") as release_mock:
            service.stop()
            service.stop()
            release_mock.assert_called_once()

    def test_get_latest_global_frame_does_not_drain_queue(self):
        """Global preview accessor should read latest frame without removing queued frames."""
        queue = self.monitor_service.FrameQueue(maxlen=4)
        queue.put((1.0, b"a"))
        queue.put((2.0, b"b"))
        self.monitor_service._GLOBAL_QUEUE = queue
        latest = self.monitor_service.get_latest_global_frame()
        self.assertEqual(latest, (2.0, b"b"))
        self.assertEqual(queue.size(), 2)

    def test_preview_same_config_does_not_restart(self):
        config = CaptureConfig(width=1280, height=720, fps=30)
        with mock.patch.object(self.monitor_service, "FfmpegCapture", DummyCapture):
            ok1, _ = self.monitor_service._ensure_preview_capture("camera-1", config, allow_input_tuning=False)
            ok2, _ = self.monitor_service._ensure_preview_capture("camera-1", config, allow_input_tuning=False)
            self.assertTrue(ok1)
            self.assertTrue(ok2)
            self.assertEqual(DummyCapture.created, 1)

    def test_preview_restart_is_debounced(self):
        config1 = CaptureConfig(width=1280, height=720, fps=30)
        config2 = CaptureConfig(width=640, height=480, fps=30)
        with mock.patch.object(self.monitor_service, "FfmpegCapture", DummyCapture):
            ok1, _ = self.monitor_service._ensure_preview_capture("camera-1", config1, allow_input_tuning=False)
            ok2, reason = self.monitor_service._ensure_preview_capture("camera-1", config2, allow_input_tuning=False)
            self.assertTrue(ok1)
            self.assertFalse(ok2)
            self.assertEqual(reason, "Preview restart debounced")

    def test_preview_pause_blocks_restart(self):
        config = CaptureConfig(width=1280, height=720, fps=30)
        with mock.patch.object(self.monitor_service, "FfmpegCapture", DummyCapture):
            self.monitor_service.pause_preview_for_monitoring()
            ok, reason = self.monitor_service._ensure_preview_capture("camera-1", config, allow_input_tuning=False)
            self.assertFalse(ok)
            self.assertEqual(reason, "Preview paused while monitoring is active")
