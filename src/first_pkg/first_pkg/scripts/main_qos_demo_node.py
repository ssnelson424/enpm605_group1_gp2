"""Entry point for the qos_demo_node executable.

Creates and spins a QoSDemoNode that demonstrates QoS compatibility,
incompatibility, and transient local durability across three pub/sub pairs.
"""

import rclpy
from first_pkg.qos_demo_node import QoSDemoNode


def main(args=None):
    """Initialize ROS 2, spin the QoSDemoNode, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = QoSDemoNode("qos_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
