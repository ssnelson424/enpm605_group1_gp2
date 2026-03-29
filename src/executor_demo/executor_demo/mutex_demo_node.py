import time

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup


class MutexDemoNode(Node):
    def __init__(self):
        super().__init__("mutex_demo")
        self._group = MutuallyExclusiveCallbackGroup()

        self.create_timer(1.0, self._cb1, callback_group=self._group)
        self.create_timer(0.5, self._cb2, callback_group=self._group)
        self.create_timer(0.25, self._cb3, callback_group=self._group)

    def _cb1(self):
        self.get_logger().info("cb1 START")
        time.sleep(0.200)
        self.get_logger().info("cb1 DONE")

    def _cb2(self):
        self.get_logger().info("cb2 START")
        time.sleep(0.080)
        self.get_logger().info("cb2 DONE")

    def _cb3(self):
        self.get_logger().info("cb3 START")
        time.sleep(0.040)
        self.get_logger().info("cb3 DONE")
