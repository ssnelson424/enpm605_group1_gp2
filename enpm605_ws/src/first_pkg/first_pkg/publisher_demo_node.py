"""Publisher demo node that publishes an incrementing counter.

This module demonstrates how to create a publisher with a timer
callback that periodically publishes Int64 messages on the "counter" topic.
"""

from std_msgs.msg import Int64
from rclpy.node import Node


class PublisherDemoNode(Node):
    """A node that publishes an incrementing integer every 2 seconds."""

    def __init__(self, node_name: str):
        """Initialize the publisher, message, and timer.

        Args:
            node_name (str): Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self._counter = 0
        self._message = Int64()
        # Create a publisher on the "counter" topic with a queue depth of 10
        self._publisher = self.create_publisher(Int64, "counter", 10)
        # Fire _timer_callback every 2.0 seconds
        self._timer = self.create_timer(2.0, self._timer_callback)

    def _timer_callback(self):
        """Publish the current counter value and increment it."""
        self._message.data = self._counter  # populate field
        self._publisher.publish(self._message)  # send
        self.get_logger().info(f"Publishing: {self._counter}")
        self._counter += 1
