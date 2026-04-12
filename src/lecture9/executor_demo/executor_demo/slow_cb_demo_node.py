import time

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup


class SlowCbDemoNode(Node):
    """Single slow callback -- cb takes 2 s but fires every 500 ms."""

    # Cycling colors for each invocation
    _CB_COLORS = ["\033[91m", "\033[92m", "\033[94m", "\033[93m", "\033[95m", "\033[96m"]
    # Two alternating colors for the timestamp (white / yellow)
    _TIME_COLORS = ["\033[97m", "\033[93m"]
    _RESET = "\033[0m"

    def __init__(self):
        super().__init__("slow_cb_demo")
        self._group = ReentrantCallbackGroup()
        self._last_second = None
        self._time_color_idx = 0
        self._invocation = 0
        self.create_timer(0.5, self._cb, callback_group=self._group)

    def _log(self, inv, msg):
        now = self.get_clock().now()
        sec, nsec = now.seconds_nanoseconds()
        if sec != self._last_second:
            self._last_second = sec
            self._time_color_idx = 1 - self._time_color_idx
        tc = self._TIME_COLORS[self._time_color_idx]
        cc = self._CB_COLORS[(inv - 1) % len(self._CB_COLORS)]
        self.get_logger().info(
            f"{tc}[{sec}.{nsec:09d}]{self._RESET} {cc}cb [#{inv}] {msg}{self._RESET}"
        )

    def _cb(self):
        self._invocation += 1
        inv = self._invocation
        self._log(inv, "START -- sleeping 2 s")
        time.sleep(2)
        self._log(inv, "DONE")
