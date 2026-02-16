import unittest
from unittest.mock import patch

from app.services import camera_enumerator


class CameraEnumeratorTests(unittest.TestCase):
    def test_parse_dshow_video_devices(self):
        """Execute test parse dshow video devices.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        sample = """
[dshow @ 0000000001] "Camera One" (video)
[dshow @ 0000000001] "Camera Two" (video)
[dshow @ 0000000001] "Microphone" (audio)
"""
        self.assertEqual(camera_enumerator._parse_dshow_video_devices(sample), ["Camera One", "Camera Two"])

    def test_parse_avfoundation_video_devices(self):
        """Execute test parse avfoundation video devices.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        sample = """
[AVFoundation indev @ 0x0] AVFoundation video devices:
[AVFoundation indev @ 0x0] [0] FaceTime HD Camera
[AVFoundation indev @ 0x0] [1] OBS Virtual Camera
[AVFoundation indev @ 0x0] AVFoundation audio devices:
[AVFoundation indev @ 0x0] [0] Built-in Microphone
"""
        self.assertEqual(
            camera_enumerator._parse_avfoundation_video_devices(sample),
            ["FaceTime HD Camera", "OBS Virtual Camera"],
        )

    def test_parse_dshow_skips_alternative_name_lines(self):
        """Execute test parse dshow skips alternative name lines.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        sample = """
[dshow @ 0000000001] "OBS Virtual Camera" (video)
[dshow @ 0000000001]   Alternative name "@device_pnp_\\?\\usb#vid"
"""
        self.assertEqual(camera_enumerator._parse_dshow_video_devices(sample), ["OBS Virtual Camera"])

    def test_parse_v4l2_sources(self):
        """Execute test parse v4l2 sources.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        sample = """
Auto-detected sources for v4l2:
  * video4linux2,v4l2 [/dev/video0]
  * video4linux2,v4l2 [/dev/video2]
"""
        self.assertEqual(camera_enumerator._parse_v4l2_sources(sample), ["/dev/video0", "/dev/video2"])

    def test_dedupe_case_insensitive_preserves_order(self):
        """Execute test dedupe case insensitive preserves order.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        devices = ["OBS Virtual Camera", "obs virtual camera", "USB Cam"]
        self.assertEqual(camera_enumerator._dedupe(devices), ["OBS Virtual Camera", "USB Cam"])

    @patch("app.services.camera_enumerator.platform.system", return_value="Windows")
    @patch("app.services.camera_enumerator._run_ffmpeg", side_effect=RuntimeError("boom"))
    def test_enumerate_video_devices_fails_safe_to_empty(self, _run_mock, _platform_mock):
        """Execute test enumerate video devices fails safe to empty.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self.assertEqual(camera_enumerator.enumerate_video_devices(), [])

    def test_reject_invalid_windows_names(self):
        """Execute test reject invalid windows names.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        items = ["OBS Virtual Camera", "Camera 0", "Camera1", "HD Webcam"]
        self.assertEqual(
            camera_enumerator._reject_invalid_windows_names(items),
            ["OBS Virtual Camera", "HD Webcam"],
        )

    @patch("app.services.camera_enumerator.platform.system", return_value="Windows")
    @patch("app.services.camera_enumerator._run_ffmpeg")
    def test_enumerate_video_devices_returns_structured_objects(self, run_mock, _platform_mock):
        """Execute test enumerate video devices returns structured objects.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        run_mock.return_value = type("R", (), {
            "stderr": '[dshow @ 1] "OBS Virtual Camera" (video)',
            "stdout": "",
            "returncode": 1,
        })()
        devices = camera_enumerator.enumerate_video_devices("ffmpeg")
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].display_name, "OBS Virtual Camera")
        self.assertEqual(devices[0].ffmpeg_token, "video=OBS Virtual Camera")
        self.assertEqual(devices[0].backend, "dshow")
        self.assertTrue(devices[0].is_virtual)
