"""Pipeline tests for bounded queue behavior."""
import unittest

from app.services.monitor_pipeline import FrameQueue


class PipelineTests(unittest.TestCase):
    """Validate ring buffer bounds and drops."""

    def test_frame_queue_drop(self):
        """FrameQueue drops oldest frames when full."""
        queue = FrameQueue(maxlen=2)
        queue.put("a")
        queue.put("b")
        queue.put("c")
        self.assertEqual(queue.dropped, 1)
        self.assertEqual(queue.get(), "b")
        self.assertEqual(queue.get(), "c")
        self.assertIsNone(queue.get(timeout=0.01))


    def test_peek_latest_does_not_drain(self):
        """peek_latest returns newest item without removing queue contents."""
        queue = FrameQueue(maxlen=3)
        queue.put("x")
        queue.put("y")
        self.assertEqual(queue.peek_latest(), "y")
        self.assertEqual(queue.size(), 2)
        self.assertEqual(queue.get(), "x")
        self.assertEqual(queue.get(), "y")
