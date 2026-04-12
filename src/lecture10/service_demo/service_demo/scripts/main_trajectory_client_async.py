"""Entry point for the trajectory_client_async executable.

Creates and spins a TrajectoryClientAsync node that sends an
asynchronous request to the compute_trajectory service.
"""

import rclpy
from lecture10_demo.service_demo.service_demo.trajectory_client_async import TrajectoryClientAsync


def main(args=None):
    """Initialize ROS 2, spin the TrajectoryClientAsync, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = TrajectoryClientAsync("trajectory_client_async")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
