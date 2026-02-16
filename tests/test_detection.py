"""Detection tests for deterministic template matching."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from core import profiles
from core import storage


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


@unittest.skipUnless(CV2_AVAILABLE, "cv2 unavailable in test environment")
class DetectionTests(unittest.TestCase):
    """Validate deterministic detection behavior."""

    def setUp(self):
        """Execute setUp.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
        os.environ["APP_DB_PATH"] = str(Path(self.temp_dir.name) / "Data" / "app.db")

    def tearDown(self):
        """Execute tearDown.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        os.chdir(self.original_cwd)
        os.environ.pop("APP_DB_PATH", None)

    def test_deterministic_output(self):
        """Same input yields same confidence and match result."""
        import cv2
        from core import detector
        profiles.create_profile("Delta")
        profiles.update_profile_detection_threshold("Delta", 0.5)
        dirs = profiles.get_profile_dirs("Delta")

        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        frame[16:32, 16:32] = 255
        frame_path = Path(dirs["frames"]) / "frame.png"
        cv2.imwrite(str(frame_path), frame)
        storage.add_frame("Delta", frame_path.name, str(frame_path))

        ref = frame[16:32, 16:32].copy()
        ref_path = Path(dirs["references"]) / "ref_1.png"
        cv2.imwrite(str(ref_path), ref)
        storage.add_reference("Delta", ref_path.name, str(ref_path), "frame.png")

        state = detector.new_detector_state()
        result1 = detector.evaluate_frame("Delta", frame, state, selected_reference="ref_1.png")
        result2 = detector.evaluate_frame("Delta", frame, state, selected_reference="ref_1.png")
        self.assertEqual(result1.matched, result2.matched)
        self.assertAlmostEqual(result1.confidence, result2.confidence, places=6)

    def test_debug_frame_saved_periodically_while_event_active(self):
        """Debug image should be emitted at interval while persistent match remains active."""
        import cv2
        from core import detector

        profiles.create_profile("Delta")
        profiles.update_profile_detection_threshold("Delta", 0.5)
        dirs = profiles.get_profile_dirs("Delta")

        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        frame[16:32, 16:32] = 255
        frame_path = Path(dirs["frames"]) / "frame.png"
        cv2.imwrite(str(frame_path), frame)
        storage.add_frame("Delta", frame_path.name, str(frame_path))

        ref = frame[16:32, 16:32].copy()
        ref_path = Path(dirs["references"]) / "ref_1.png"
        cv2.imwrite(str(ref_path), ref)
        storage.add_reference("Delta", ref_path.name, str(ref_path), "frame.png")

        state = detector.new_detector_state()
        fake_times = iter([100.0, 100.4, 101.2])

        with (
            mock.patch.object(detector, "get_debug_dir", return_value=dirs["debug"]),
            mock.patch.object(detector, "_save_debug_image_if_allowed") as save_mock,
            mock.patch.object(detector.time, "time", side_effect=lambda: next(fake_times)),
        ):
            result1 = detector.evaluate_frame("Delta", frame, state, selected_reference="ref_1.png")
            result2 = detector.evaluate_frame("Delta", frame, state, selected_reference="ref_1.png")
            result3 = detector.evaluate_frame("Delta", frame, state, selected_reference="ref_1.png")

        self.assertTrue(result1.event_start)
        self.assertIsNotNone(result1.debug_frame)
        self.assertFalse(result2.event_start)
        self.assertIsNone(result2.debug_frame)
        self.assertFalse(result3.event_start)
        self.assertIsNotNone(result3.debug_frame)
        self.assertEqual(save_mock.call_count, 2)
