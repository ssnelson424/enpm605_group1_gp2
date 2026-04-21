import rclpy
from rclpy.executors import MultiThreadedExecutor
from lecture9_demo.executor_demo.executor_demo.reentrant_demo_node import ReentrantDemoNode


def main(args=None):
    rclpy.init(args=args)
    node = ReentrantDemoNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
