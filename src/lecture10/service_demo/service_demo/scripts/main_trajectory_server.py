"""Entry point for the trajectory_server executable.

Creates and spins a TrajectoryServer node that provides the
compute_trajectory service.
"""

import rclpy
from lecture10_demo.service_demo.service_demo.trajectory_server import TrajectoryServer


def main(args=None):
    """Initialize ROS 2, spin the TrajectoryServer, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = TrajectoryServer("trajectory_server")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
