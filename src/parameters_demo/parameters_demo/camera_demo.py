"""Camera demo node with dynamic parameters.

This module demonstrates how to declare, retrieve, and dynamically
update ROS 2 parameters using ParameterDescriptor and parameter
callbacks.
"""

from std_msgs.msg import String
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import (
    ParameterDescriptor,
    IntegerRange,
    SetParametersResult,
)


class CameraDemo(Node):
    """A node that publishes simulated camera images at a configurable rate."""

    def __init__(self, node_name: str):
        """Initialize the node, declare parameters, and start the timer.

        Args:
            node_name (str): Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)

        # -- Declare parameters --
        self.declare_parameter(
            "camera_name",
            "camera",
            ParameterDescriptor(description="Name of the camera"),
        )

        camera_rate_descriptor = ParameterDescriptor(
            description="Publishing rate for the camera (Hz)",
            integer_range=[
                IntegerRange(from_value=10, to_value=80, step=10)
            ],
        )
        self.declare_parameter("camera_rate", 60, camera_rate_descriptor)

        # -- Retrieve parameters --
        self._camera_name: str = (
            self.get_parameter("camera_name").get_parameter_value().string_value
        )
        self._camera_rate: int = (
            self.get_parameter("camera_rate")
            .get_parameter_value()
            .integer_value
        )

        self.get_logger().info(f"camera_name: {self._camera_name}")
        self.get_logger().info(f"camera_rate: {self._camera_rate}")

        # -- Publisher --
        self._publisher = self.create_publisher(
            String, "/camera/image_color", 10
        )

        # -- Timer --
        self._timer = self.create_timer(
            1.0 / self._camera_rate, self._timer_callback
        )

        # -- Parameter callback --
        self.add_on_set_parameters_callback(self._on_parameter_change)

    def _timer_callback(self) -> None:
        """Publish a simulated camera image message."""
        msg = String()
        msg.data = (
            f"Published random camera image from: {self._camera_name}"
        )
        self._publisher.publish(msg)
        self.get_logger().info(msg.data)

    def _on_parameter_change(
        self, params: list[Parameter]
    ) -> SetParametersResult:
        """Validate and apply parameter changes at runtime.

        Args:
            params (list[Parameter]): List of parameters being changed.

        Returns:
            SetParametersResult: Whether the parameter change was accepted.
        """
        for param in params:
            if param.name == "camera_name":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="camera_name must be a string",
                    )
                self._camera_name = param.value
                self.get_logger().info(
                    f"camera_name updated to: {self._camera_name}"
                )

            elif param.name == "camera_rate":
                if param.type_ != Parameter.Type.INTEGER:
                    return SetParametersResult(
                        successful=False,
                        reason="camera_rate must be an integer",
                    )
                self._camera_rate = param.value
                self.get_logger().info(
                    f"camera_rate updated to: {self._camera_rate}"
                )
                # Cancel the existing timer and recreate it
                self._timer.cancel()
                self._timer = self.create_timer(
                    1.0 / self._camera_rate, self._timer_callback
                )

        return SetParametersResult(successful=True)
