# ENPM605 - RO01
# Group Project 2 - Group 1
# Kyle DeGuzman: 120452062
# Stephen Snelson: 12254074
# main_navigate_to_goal_server.py - Navigate to goal server main function.

import rclpy
from rclpy.executors import MultiThreadedExecutor

from group1_gp2.navigate_to_goal_server import NavigateToGoalServer


def main(args=None):
    """Entry point function for the NavigateToGoal server."""
    # Initialize the ROS 2 client for Python.
    rclpy.init(args=args)
    # Create an instance of the navigate_to_goal node.
    node = NavigateToGoalServer("navigate_to_goal")
    # Use a MultiThreadedExecutor with this node.
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    # Spin the node until Ctrl+C is pressed, then
    # destroy the node and clean up.
    try:
        executor.spin()
    except KeyboardInterrupt as e:
        print(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
