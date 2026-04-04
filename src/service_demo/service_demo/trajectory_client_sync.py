"""Synchronous trajectory client node.

This module demonstrates how to create a ROS 2 service client that
calls a service synchronously using client.call(). This is a text-based
demo -- no robot or simulator is needed.

Warning:
    Using synchronous service calls (client.call) with a
    single-threaded executor can cause deadlocks. The call blocks the
    executor thread while waiting for the response, preventing the
    executor from processing the response callback. Use a
    multi-threaded executor or prefer async calls in production code.
"""

import random

from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.node import Node

from custom_interfaces.srv import ComputeTrajectory


class TrajectoryClientSync(Node):
    """A service client node that sends synchronous trajectory requests.

    Warning:
        Synchronous service calls with a single-threaded executor will
        deadlock because the executor thread is blocked waiting for the
        response it cannot process. Use a MultiThreadedExecutor or
        prefer TrajectoryClientAsync for production code.
    """

    def __init__(self, node_name: str) -> None:
        """Initialize the synchronous trajectory client.

        Args:
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self._client_cb_group = MutuallyExclusiveCallbackGroup()
        self._client = self.create_client(
            ComputeTrajectory, "compute_trajectory",
            callback_group=self._client_cb_group
        )
        # Wait for the service to become available
        while not self._client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available, waiting...")

        # Use a repeating timer to send requests in a loop.
        self._timer = self.create_timer(2.0, self._timer_callback)

    def _timer_callback(self) -> None:
        """Send a synchronous request every timer tick."""
        self._send_request()
        
        for _ in range(1,20):
            self.get_logger().info("Executing after service call")

    def _send_request(self) -> None:
        """Build and send a synchronous ComputeTrajectory request."""
        request = ComputeTrajectory.Request()
        request.goal_pose.position.x = random.uniform(0.0, 10.0)
        request.max_velocity = 1.0

        self.get_logger().info("Sending synchronous request...")
        response = self._client.call(request)

        if response is None:
            self.get_logger().error("Service call returned None")
            return

        if response.success:
            self.get_logger().info(f"Service call succeeded: {response.message}")
            for i, waypoint in enumerate(response.waypoints):
                self.get_logger().info(
                    f"  Waypoint {i}: position=({waypoint.position.x}, "
                    f"{waypoint.position.y}, {waypoint.position.z})"
                )
        else:
            self.get_logger().warn(f"Service call failed: {response.message}")
