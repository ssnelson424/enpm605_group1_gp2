"""Navigate action server node.

This module demonstrates how to create a ROS 2 action server using
a custom action interface (Navigate). This is a text-based demo -- no
robot or simulator is needed. Navigation is simulated with a countdown
loop using time.sleep() and log messages.
"""

import time

from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node

from custom_interfaces.action import Navigate


class NavigateServer(Node):
    """An action server node that simulates robot navigation."""

    def __init__(self, node_name: str) -> None:
        """Initialize the Navigate action server.

        Args:
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self._action_server = ActionServer(
            self,
            Navigate,
            "navigate",
            execute_callback=self._execute_callback,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback,
        )
        self.get_logger().info("Navigate action server ready.")

    def _goal_callback(self, goal_request) -> GoalResponse:
        """Accept or reject an incoming goal request.

        Rejects the goal if max_speed is less than or equal to zero.

        Args:
            goal_request: The incoming goal request.

        Returns:
            GoalResponse.ACCEPT or GoalResponse.REJECT.
        """
        self.get_logger().info("Received goal request.")
        if goal_request.max_speed <= 0:
            self.get_logger().warn(
                f"Rejecting goal: max_speed ({goal_request.max_speed}) <= 0"
            )
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle) -> CancelResponse:
        """Accept all cancel requests.

        Args:
            goal_handle: The goal handle for the cancel request.

        Returns:
            CancelResponse.ACCEPT.
        """
        self.get_logger().info("Received cancel request. Accepting.")
        return CancelResponse.ACCEPT

    def _execute_callback(self, goal_handle) -> Navigate.Result:
        """Execute the navigation goal.

        Simulates navigation in 10 iterations (1 second each), publishing
        feedback with distance_remaining and percent_complete. Checks for
        cancellation each iteration.

        Args:
            goal_handle: The goal handle for the current goal.

        Returns:
            The Navigate result with success, total_distance, and elapsed_time.
        """
        self.get_logger().info("Executing goal...")
        feedback_msg = Navigate.Feedback()
        total_iterations = 10
        total_distance = 10.0

        for i in range(1, total_iterations + 1):
            # Check for cancellation
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info("Goal canceled.")
                result = Navigate.Result()
                result.success = False
                result.total_distance = (i - 1) * (total_distance / total_iterations)
                result.elapsed_time = float(i - 1)
                return result

            # Simulate work
            time.sleep(1.0)

            # Publish feedback
            feedback_msg.distance_remaining = total_distance - (
                i * (total_distance / total_iterations)
            )
            feedback_msg.percent_complete = (i / total_iterations) * 100.0
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(
                f"Feedback: {feedback_msg.percent_complete:.0f}% complete, "
                f"{feedback_msg.distance_remaining:.1f} remaining"
            )

        # Mark goal as succeeded
        goal_handle.succeed()
        self.get_logger().info("Goal succeeded.")

        result = Navigate.Result()
        result.success = True
        result.total_distance = total_distance
        result.elapsed_time = float(total_iterations)
        return result
