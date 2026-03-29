import rclpy
from executor_demo.single_threaded_demo_node import SingleThreadedDemoNode


def main(args=None):
    rclpy.init(args=args)
    node = SingleThreadedDemoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
