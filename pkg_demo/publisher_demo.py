from std_msgs.msg import Int64
from rclpy.node import Node


class PublisherDemo(Node):
    def __init__(self, node_name: str):
        super().__init__(node_name)
        self._counter = 0
        self._message = Int64()
        self._publisher = self.create_publisher(Int64, "counter", 10)
        self._timer = self.create_timer(2.0, self._timer_callback)

    def _timer_callback(self):
        self._message.data = self._counter  # populate field
        self._publisher.publish(self._message)  # send
        self.get_logger().info(f"Publishing: {self._counter}")
        self._counter += 1
