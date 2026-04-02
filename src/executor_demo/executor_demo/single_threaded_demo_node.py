import time

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup


class SingleThreadedDemoNode(Node):
    def __init__(self):
        super().__init__("single_threaded_demo")

        self.create_timer(0.5, self._cb1)
        self.create_timer(0.5, self._cb2)
        self.create_timer(0.25, self._cb3)

    def _cb1(self):
        self.get_logger().info("cb1 START")
        time.sleep(0.030)
        self.get_logger().info("cb1 DONE")

    def _cb2(self):
        self.get_logger().info("cb2 START")
        time.sleep(0.020)
        self.get_logger().info("cb2 DONE")

    def _cb3(self):
        self.get_logger().info("cb3 START")
        time.sleep(0.010)
        self.get_logger().info("cb3 DONE")
