
# ENPM605 - RO01
# Group Project 2 - Group 1 
# Stephen Snelson 12254074
# Navigate to Goal Client Main Function
import rclpy
from group1_gp2.navigate_to_goal_client import NavigationClient


def main(args=None):
    """Send a navigation goal, and handle shutdown."""
    
    rclpy.init(args=args)
    node = NavigationClient("navigate_to_goal_client")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f"Keyboard Interrupt Received.")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()