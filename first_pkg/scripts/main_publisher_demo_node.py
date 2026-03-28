"""Entry point for the publisher_demo_node executable.

Creates and spins a PublisherDemoNode that publishes an incrementing
counter on the "counter" topic every 2 seconds.
"""

import rclpy
from first_pkg.publisher_demo_node import PublisherDemoNode


def main(args=None):
    """Initialize ROS 2, spin the PublisherDemoNode, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = PublisherDemoNode("publisher_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()