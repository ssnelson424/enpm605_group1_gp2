"""Subscriber demo node that listens for counter messages.

This module demonstrates how to create a subscription that
receives Int64 messages on the "counter" topic.
"""

from rclpy.node import Node
from std_msgs.msg import Int64


class SubscriberDemoNode(Node):
    """A node that subscribes to the "counter" topic and logs received values."""

    def __init__(self, node_name: str):
        """Initialize the subscription on the "counter" topic.

        Args:
            node_name (str): Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        # Subscribe to "counter" topic with a queue depth of 10
        self._subscriber = self.create_subscription(
            Int64, "counter", self._subscriber_callback, 10
        )
        self.get_logger().info("Subscriber initialized.")

    def _subscriber_callback(self, msg: Int64):
        """Log the received message data.

        Args:
            msg (Int64): The incoming Int64 message.
        """
        self.get_logger().info(f"Received: {msg.data}")
