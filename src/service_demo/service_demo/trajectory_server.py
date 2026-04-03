"""Trajectory server node that provides the compute_trajectory service.

This module demonstrates how to create a ROS 2 service server using
a custom service interface (ComputeTrajectory). This is a text-based
demo -- no robot or simulator is needed. The server logs the request
and returns a success message without actually computing a path.
"""

from rclpy.node import Node

from custom_interfaces.srv import ComputeTrajectory


class TrajectoryServer(Node):
    """A service server node that simulates trajectory computation on request."""

    def __init__(self, node_name: str) -> None:
        """Initialize the trajectory service server.

        Args:
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)
        self._service = self.create_service(
            ComputeTrajectory, "compute_trajectory", self._service_callback
        )
        self.get_logger().info("Trajectory server ready.")

    def _service_callback(
        self,
        request: ComputeTrajectory.Request,
        response: ComputeTrajectory.Response,
    ) -> ComputeTrajectory.Response:
        """Handle an incoming ComputeTrajectory request.

        Logs the start pose, goal pose, and max velocity from the request,
        then returns a successful response.

        Args:
            request: The service request containing start_pose, goal_pose,
                and max_velocity.
            response: The service response to populate.

        Returns:
            The populated service response.
        """
        self.get_logger().info(
            f"Received request:\n"
            f"  Start pose: ({request.start_pose.position.x}, "
            f"{request.start_pose.position.y}, "
            f"{request.start_pose.position.z})\n"
            f"  Goal pose: ({request.goal_pose.position.x}, "
            f"{request.goal_pose.position.y}, "
            f"{request.goal_pose.position.z})\n"
            f"  Max velocity: {request.max_velocity}"
        )

        response.success = True
        response.message = "Trajectory computed successfully"
        return response
