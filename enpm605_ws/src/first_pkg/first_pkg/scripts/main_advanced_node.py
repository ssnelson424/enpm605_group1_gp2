"""Entry point for the advanced_node executable.

Creates and spins an AdvancedNode that logs an incrementing counter
every second.
"""

import rclpy
from first_pkg.advanced_node import AdvancedNode


def main(args=None):
    """Initialize ROS 2, spin the AdvancedNode, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = AdvancedNode("advanced_node")
    rclpy.shutdown()


# def main(args=None):
#     rclpy.init(args=args)
#     node = AdvancedNode("advanced_node")
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt as e:
#         print(f"Exception: {type(e).__name__}")
#     finally:
#         node.destroy_node()
#         if rclpy.ok():
#             rclpy.shutdown()
