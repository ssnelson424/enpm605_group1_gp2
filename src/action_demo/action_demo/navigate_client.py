"""Navigate action client node.

This module demonstrates how to create a ROS 2 action client using
a custom action interface (Navigate). This is a text-based demo -- no
robot or simulator is needed. The client sends simulated navigation
goals and handles feedback and results via callbacks.
"""

from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node

from custom_interfaces.action import Navigate


class NavigateClient(Node):
    """An action client node that sends navigation goals."""

    def __init__(self, node_name: str) -> None:
        """Initialize the Navigate action client.

        Args:
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self._action_client = ActionClient(self, Navigate, "navigate")
        self._goal_handle = None

    def send_goal(self, x: float, y: float) -> None:
        """Send a navigation goal to the action server.

        Waits for the server to become available, then sends the goal
        with feedback and result callbacks.

        Args:
            x: Target x position.
            y: Target y position.
        """
        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()

        goal_msg = Navigate.Goal()
        goal_msg.target_pose.position.x = x
        goal_msg.target_pose.position.y = y
        goal_msg.max_speed = 1.0

        self.get_logger().info(f"Sending goal: ({x}, {y})")
        self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback
        ).add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        """Handle the goal response from the server.

        If the goal is accepted, requests the result asynchronously.

        Args:
            future: The future containing the goal handle.
        """
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected.")
            return

        self.get_logger().info("Goal accepted.")
        self._goal_handle = goal_handle
        goal_handle.get_result_async().add_done_callback(
            self._result_callback
        )

    def _feedback_callback(self, feedback_msg) -> None:
        """Handle feedback from the action server.

        Args:
            feedback_msg: The feedback message containing navigation progress.
        """
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"Feedback: {feedback.percent_complete:.0f}% complete, "
            f"{feedback.distance_remaining:.1f} remaining"
        )

    def _result_callback(self, future) -> None:
        """Handle the final result from the action server.

        Args:
            future: The future containing the action result.
        """
        result = future.result().result
        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f"Navigation succeeded! "
                f"Total distance: {result.total_distance:.1f}, "
                f"Elapsed time: {result.elapsed_time:.1f}s"
            )
        else:
            self.get_logger().warn(
                f"Navigation failed with status: {status}"
            )
