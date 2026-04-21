"""Advanced ROS 2 node with a timer-driven callback.

This module demonstrates how to subclass Node and use a timer
to execute a callback at a fixed interval (1 Hz).
"""

from rclpy.node import Node


class AdvancedNode(Node):
    """A node that logs a greeting on startup."""

    def __init__(self, node_name: str):
        """Initialize the node and log a greeting.

        Args:
            node_name (str): Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self.get_logger().info(f"Hello from {self.get_name()}")


# class AdvancedNode(Node):
#     """A node that increments and logs a counter every second."""

#     def __init__(self, node_name: str):
#         """Initialize the node with a counter and a 1-second timer.

#         Args:
#             node_name: Name to register this node with in the ROS 2 graph.
#         """
#         super().__init__(node_name)
#         self._counter = 0
#         # Fire _timer_callback every 1.0 second
#         self._timer = self.create_timer(1.0, self._timer_callback)

#     def _timer_callback(self):
#         """Log the current counter value and increment it."""
#         self.get_logger().info(f"Count: {self._counter}")
#         self._counter += 1
