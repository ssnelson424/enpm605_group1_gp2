"""Entry point for the navigate_server executable.

Creates and spins a NavigateServer node that provides the
navigate action.
"""

import rclpy
from action_demo.navigate_server import NavigateServer


def main(args=None):
    """Initialize ROS 2, spin the NavigateServer, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = NavigateServer("navigate_server")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
