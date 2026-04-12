"""Entry point for the random_mover executable.

Creates and spins a RandomMoverDemo node that publishes random
velocities and subscribes to odometry for demonstration purposes.
"""

import rclpy
from robot_control_demo.random_mover_demo import RandomMoverDemo


def main(args=None):
    """Initialize ROS 2, spin the RandomMoverDemo node, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = RandomMoverDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
