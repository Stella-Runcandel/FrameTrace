"""Guardrails for FFmpeg-only camera enumeration stack."""

from pathlib import Path
import unittest


class CameraStackGuardrailsTests(unittest.TestCase):
    def test_no_forbidden_camera_stack_tokens_in_app_services(self):
        """Execute test no forbidden camera stack tokens in app services.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        services_dir = Path("app/services")
        forbidden = {
            "import ctypes",
            "from ctypes",
            "CoInitialize",
            "MFCreate",
            "IMF",
            "cv2.VideoCapture",
        }

        for file_path in services_dir.glob("*.py"):
            text = file_path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"Forbidden token {token!r} in {file_path}")

    def test_no_media_foundation_compat_module(self):
        """Execute test no media foundation compat module.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self.assertFalse(Path("app/services/mf_enumerator.py").exists())
