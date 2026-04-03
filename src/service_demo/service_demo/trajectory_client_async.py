"""Asynchronous trajectory client node.

This module demonstrates how to create a ROS 2 service client that
calls a service asynchronously using call_async with add_done_callback.
"""

from rclpy.node import Node

from custom_interfaces.srv import ComputeTrajectory


class TrajectoryClientAsync(Node):
    """A service client node that sends asynchronous trajectory requests."""

    def __init__(self, node_name: str) -> None:
        """Initialize the async trajectory client.

        Args:
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self._client = self.create_client(
            ComputeTrajectory, "compute_trajectory"
        )
        # Wait for the service to become available
        while not self._client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available, waiting...")

        self._send_request()

    def _send_request(self) -> None:
        """Build and send an asynchronous ComputeTrajectory request."""
        request = ComputeTrajectory.Request()
        request.goal_pose.position.x = 5.0
        request.max_velocity = 1.0

        self.get_logger().info("Sending async request...")
        future = self._client.call_async(request)
        future.add_done_callback(self._response_callback)

    def _response_callback(self, future) -> None:
        """Handle the service response.

        Args:
            future: The future object containing the service response.
        """
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(
                    f"Service call succeeded: {response.message}"
                )
            else:
                self.get_logger().warn(
                    f"Service call failed: {response.message}"
                )
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")
