"""Entry point for the lidar_demo executable.

Creates and spins a LidarDemo node that publishes simulated lidar
scan data at a configurable rate.
"""

import rclpy
from lecture10_demo.parameters_demo.parameters_demo.lidar_demo import LidarDemo


def main(args=None):
    """Initialize ROS 2, spin the LidarDemo node, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = LidarDemo("lidar_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
