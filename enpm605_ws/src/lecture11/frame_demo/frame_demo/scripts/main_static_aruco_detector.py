"""Entry point for the static_aruco_detector executable."""

import rclpy
from frame_demo.static_aruco_detector import StaticArucoDetector


def main(args=None):
    rclpy.init(args=args)
    node = StaticArucoDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
