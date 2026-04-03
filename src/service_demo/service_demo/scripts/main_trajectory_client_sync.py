"""Entry point for the trajectory_client_sync executable.

Creates and spins a TrajectoryClientSync node that sends a
synchronous request to the compute_trajectory service.
"""

import rclpy
from service_demo.trajectory_client_sync import TrajectoryClientSync


def main(args=None):
    """Initialize ROS 2, spin the TrajectoryClientSync, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = TrajectoryClientSync("trajectory_client_sync")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
