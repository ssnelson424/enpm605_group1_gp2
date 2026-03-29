import rclpy
from rclpy.executors import MultiThreadedExecutor
from executor_demo.slow_cb_demo_node import SlowCbDemoNode


def main(args=None):
    rclpy.init(args=args)
    node = SlowCbDemoNode()
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
