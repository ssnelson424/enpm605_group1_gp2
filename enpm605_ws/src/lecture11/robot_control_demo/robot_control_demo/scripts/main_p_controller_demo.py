"""Entry point for the p_controller executable.

Creates and spins a ProportionalController node that drives the robot
toward a configurable goal using a proportional control law.
"""

import rclpy
from robot_control_demo.p_controller_demo import ProportionalController


def main(args=None):
    """Initialize ROS 2, spin the ProportionalController node, and handle shutdown.

    Args:
        args (list, optional): Command-line arguments passed to rclpy.init().
    """
    rclpy.init(args=args)
    node = ProportionalController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        node.get_logger().info(f"Exception: {type(e).__name__}")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
