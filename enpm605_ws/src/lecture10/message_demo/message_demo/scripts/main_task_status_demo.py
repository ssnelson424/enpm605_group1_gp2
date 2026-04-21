"""Entry point for the task_status_demo executable."""

import rclpy
from lecture10_demo.message_demo.message_demo.task_status_demo import TaskStatusDemo


def main(args=None):
    rclpy.init(args=args)
    node = TaskStatusDemo("task_status_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
