"""Entry point for the camera_demo executable.

Creates and spins a CameraDemo node that publishes simulated camera
images at a configurable rate.
"""

import rclpy
from lecture10_demo.parameters_demo.parameters_demo.camera_demo import CameraDemo


def main(args=None):
    """Initialize ROS 2, spin the CameraDemo node, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = CameraDemo("camera_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
