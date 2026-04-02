import rclpy
from rclpy.executors import SingleThreadedExecutor
from executor_demo.single_threaded_demo_node import SingleThreadedDemoNode


def main(args=None):
    rclpy.init(args=args)
    node = SingleThreadedDemoNode()
    
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
