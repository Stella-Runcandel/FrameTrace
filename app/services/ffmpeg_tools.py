"""FFmpeg discovery and command helpers for Windows capture."""
import os
import platform
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


class FfmpegNotFoundError(RuntimeError):
    """Raised when FFmpeg cannot be located."""
    pass


@dataclass(frozen=True)
class CaptureConfig:
    width: int
    height: int
    fps: int


_ENUM_CACHE: list[str] | None = None


def resolve_ffmpeg_path() -> str:
    """Return bundled FFmpeg path or fallback to PATH."""
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    root = Path(__file__).resolve().parents[2]
    bundled = root / "bin" / "ffmpeg.exe"
    if bundled.exists():
        return str(bundled)

    return "ffmpeg"


def _run_ffmpeg_command(args, timeout=10, text=True):
    """Run FFmpeg command and return CompletedProcess."""
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            text=text,
        )
    except FileNotFoundError as exc:
        raise FfmpegNotFoundError("ffmpeg executable not found") from exc
    return result


def list_dshow_video_devices():
    """Return DirectShow video device names using FFmpeg enumeration."""
    return list_video_devices(force_refresh=True)


def _probe_opencv_indices(max_devices=12, max_consecutive_failures=3) -> list[str]:
    """Probe camera indexes with OpenCV as Windows fallback enumeration only."""
    try:
        import cv2
    except Exception:
        return []

    devices = []
    failures = 0
    for idx in range(max_devices):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        ok = bool(cap and cap.isOpened())
        if ok:
            devices.append(f"Camera {idx}")
            failures = 0
        else:
            failures += 1
        if cap:
            cap.release()
        if failures >= max_consecutive_failures:
            break
    return devices


def list_video_devices(force_refresh: bool = False) -> list[str]:
    """
    Return a list of video capture device names discovered via FFmpeg (Windows).
    Must be safe, fail gracefully, and return [] on error.
    """
    global _ENUM_CACHE
    if _ENUM_CACHE is not None and not force_refresh:
        return list(_ENUM_CACHE)

    ffmpeg_path = resolve_ffmpeg_path()
    args = [
        ffmpeg_path,
        "-hide_banner",
        "-list_devices",
        "true",
        "-f",
        "dshow",
        "-i",
        "dummy",
    ]

    devices = []
    try:
        # FFmpeg writes DirectShow device listings to stderr for this command.
        result = _run_ffmpeg_command(args, timeout=10, text=True)
        output = result.stderr or ""
        devices = _parse_dshow_video_devices(output)
    except Exception:
        devices = []

    if not devices and platform.system() == "Windows":
        devices = _probe_opencv_indices()

    _ENUM_CACHE = list(devices)
    return list(_ENUM_CACHE)


def _parse_dshow_video_devices(output: str):
    """Parse FFmpeg stderr output into a list of device names."""
    devices = []
    in_video = False
    for line in output.splitlines():
        if "DirectShow video devices" in line:
            in_video = True
            continue
        if "DirectShow audio devices" in line:
            in_video = False
        if not in_video:
            continue
        match = re.search(r"\"([^\"]+)\"", line)
        if match:
            devices.append(match.group(1))
    return devices


def build_ffmpeg_capture_command(device_name: str, config: CaptureConfig):
    """Build FFmpeg command for raw BGR24 capture."""
    return [
        resolve_ffmpeg_path(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "dshow",
        "-rtbufsize",
        "512M",
        "-video_size",
        f"{config.width}x{config.height}",
        "-framerate",
        str(config.fps),
        "-i",
        f"video={device_name}",
        "-pix_fmt",
        "bgr24",
        "-f",
        "rawvideo",
        "pipe:1",
    ]


def capture_single_frame(device_name: str, width: int, height: int, fps: int):
    """Capture a single raw frame from FFmpeg for legacy callers."""
    config = CaptureConfig(width=width, height=height, fps=fps)
    args = [
        resolve_ffmpeg_path(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "dshow",
        "-video_size",
        f"{config.width}x{config.height}",
        "-framerate",
        str(config.fps),
        "-i",
        f"video={device_name}",
        "-frames:v",
        "1",
        "-pix_fmt",
        "bgr24",
        "-f",
        "rawvideo",
        "pipe:1",
    ]
    result = _run_ffmpeg_command(args, timeout=10, text=False)
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="ignore") if result.stderr else ""
        raise RuntimeError(stderr.strip() or "FFmpeg snapshot failed")
    return result.stdout
