import time

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup


class SlowCbDemoNode(Node):
    """Single slow callback -- cb takes 2 s but fires every 500 ms."""

    def __init__(self):
        super().__init__("slow_cb_demo")
        self._group = ReentrantCallbackGroup()
        self.create_timer(0.5, self._cb, callback_group=self._group)

    def _cb(self):
        self.get_logger().info("cb START -- sleeping 2 s")
        time.sleep(2)
        self.get_logger().info("cb DONE")
