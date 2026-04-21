"""Entry point for the trajectory_client_sync executable.

Creates and spins a TrajectoryClientSync node that sends a
synchronous request to the compute_trajectory service.
"""

import rclpy
from rclpy.executors import MultiThreadedExecutor
from lecture10_demo.service_demo.service_demo.trajectory_client_sync import TrajectoryClientSync


def main(args=None):
    """Initialize ROS 2, spin the TrajectoryClientSync, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = TrajectoryClientSync("trajectory_client_sync")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
