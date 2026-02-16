# Bug and Logical Inconsistency Notes

This file highlights issues found while adding function-level comments/docstrings.

## 1) Race condition when draining FFmpeg logs (fixed)
- **File:** `app/services/monitor_service.py`
- **Issue:** The previous implementation used `while not queue.empty(): get_nowait()`. This is a known race: another thread can drain the queue between the two calls, causing `queue.Empty` unexpectedly.
- **Fix applied:** Switched to `while True` + `get_nowait()` + `except queue.Empty: break`.

## 2) Multiple broad `except Exception: pass` blocks can hide operational faults
- **Files:**
  - `app/services/monitor_service.py`
  - `app/services/ffmpeg_capture_supervisor.py`
  - `core/profiles.py`
- **Risk:** Silent exception swallowing can mask real failures (state transitions, logging transport issues, cleanup failures), making incidents difficult to diagnose.
- **Recommendation:** Capture and log at least debug-level details where suppressing errors is intentional.

## 3) State transition errors are intentionally suppressed in stop/failure flows
- **File:** `app/services/monitor_service.py`
- **Risk:** `InvalidTransition` is swallowed in several places, which may leave state recovery paths harder to reason about when transitions are out-of-order.
- **Recommendation:** Add instrumentation counters or debug logs so this behavior is observable in production diagnostics.
