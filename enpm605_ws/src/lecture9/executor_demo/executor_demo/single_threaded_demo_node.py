import time

from rclpy.node import Node


class SingleThreadedDemoNode(Node):
    # ANSI colors for callbacks
    _CB_COLORS = {1: "\033[91m", 2: "\033[92m", 3: "\033[94m"}
    # Two alternating colors for the timestamp (white / yellow)
    _TIME_COLORS = ["\033[97m", "\033[93m"]
    _RESET = "\033[0m"

    def __init__(self):
        super().__init__("single_threaded_demo")
        self._last_second = None
        self._time_color_idx = 0

        self.create_timer(0.5, self._cb1)
        self.create_timer(0.5, self._cb2)
        self.create_timer(0.25, self._cb3)

    def _log(self, cb_id, msg):
        now = self.get_clock().now()
        sec, nsec = now.seconds_nanoseconds()
        if sec != self._last_second:
            self._last_second = sec
            self._time_color_idx = 1 - self._time_color_idx
        tc = self._TIME_COLORS[self._time_color_idx]
        cc = self._CB_COLORS[cb_id]
        self.get_logger().info(
            f"{tc}[{sec}.{nsec:09d}]{self._RESET} {cc}cb{cb_id} {msg}{self._RESET}"
        )

    def _cb1(self):
        self._log(1, "START")
        time.sleep(0.030)
        self._log(1, "DONE")

    def _cb2(self):
        self._log(2, "START")
        time.sleep(0.020)
        self._log(2, "DONE")

    def _cb3(self):
        self._log(3, "START")
        time.sleep(0.010)
        self._log(3, "DONE")
