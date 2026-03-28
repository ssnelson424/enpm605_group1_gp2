"""Entry point for the subscriber_demo_node executable.

Creates and spins a SubscriberDemoNode that listens for Int64
messages on the "counter" topic.
"""

import rclpy
from first_pkg.subscriber_demo_node import SubscriberDemoNode


def main(args=None):
    """Initialize ROS 2, spin the SubscriberDemoNode, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = SubscriberDemoNode("subscriber_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()