# ENPM605 - RO01
# Group Project 2 - Group 1
# Kyle DeGuzman: 120452062
# Stephen Snelson: 12254074
# main_navigate_to_goal_client.py - Navigate to goal client main function.
import rclpy

from group1_gp2.navigate_to_goal_client import NavigationClient


def main(args=None):
    """Entry point function for the NavigationClient."""
    # Initialize the ROS 2 client for Python.
    rclpy.init(args=args)
    # Create an instance of the navigate_to_goal_client.
    node = NavigationClient("navigate_to_goal_client")
    # Spin the node until Ctrl+C is pressed, then
    # destroy the node and clean up.
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard Interrupt Received.")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
