"""Entry point for the aruco_marker_listener executable."""

import rclpy
from frame_demo.aruco_marker_listener import ArucoMarkerListener


def main(args=None):
    rclpy.init(args=args)
    node = ArucoMarkerListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
