"""Minimal ROS 2 node that logs a single message and exits.

This module demonstrates the simplest possible ROS 2 node using
rclpy.create_node() without subclassing Node.
"""

import rclpy


def main(args=None):
    """Create a minimal node, log a message, and shut down.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    # Initialize the ROS 2 communication layer
    rclpy.init(args=args)
    # Create a node with the given name (visible in ros2 node list)
    node = rclpy.create_node("minimal_node")
    node.get_logger().info("Hello from ROS 2")
    # Shut down the ROS 2 runtime
    rclpy.shutdown()