from rclpy.node import Node
from std_msgs.msg import Int64


class SubscriberDemo(Node):
    def __init__(self, node_name: str):
        super().__init__(node_name)
        self._subscriber = self.create_subscription(
            Int64, "counter", self._subscriber_callback, 10
        )
        self.get_logger().info("Subscriber initialized.")

    def _subscriber_callback(self, msg: Int64):
        self.get_logger().info(f"Received: {msg.data}")
