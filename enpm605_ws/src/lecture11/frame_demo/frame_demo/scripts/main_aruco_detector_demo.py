"""Entry point for the aruco_detector executable.

Creates and spins an ArucoDetectorDemo node that detects ArUco markers
in a camera image stream and broadcasts each marker pose as a TF frame.
"""

import rclpy
from frame_demo.dynamic_detector_demo import ArucoDetectorDemo


def main(args=None):
    """Initialize ROS 2, spin the ArucoDetectorDemo node, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = ArucoDetectorDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
