"""Entry point for the kdl_chain_demo executable."""

import rclpy
from frame_demo.kdl_chain_demo import KdlChainDemo


def main(args=None):
    rclpy.init(args=args)
    node = KdlChainDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
