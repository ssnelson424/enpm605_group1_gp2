"""Entry point for the navigate_client executable.

Creates a NavigateClient node, sends a goal to (5.0, 3.0),
and spins until completion.
"""

import rclpy
from action_demo.navigate_client import NavigateClient


def main(args=None):
    """Initialize ROS 2, send a navigation goal, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = NavigateClient("navigate_client")
    node.send_goal(5.0, 3.0)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
