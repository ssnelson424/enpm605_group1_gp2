"""Lidar demo node with dynamic parameters.

This module demonstrates how to declare, retrieve, and dynamically
update ROS 2 parameters for a simulated lidar sensor.
"""

from std_msgs.msg import String
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import (
    ParameterDescriptor,
    IntegerRange,
    SetParametersResult,
)


class LidarDemo(Node):
    """A node that publishes simulated lidar scan data at a configurable rate."""

    def __init__(self, node_name: str):
        """Initialize the node, declare parameters, and start the timer.

        Args:
            node_name (str): Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)

        # -- Declare parameters --
        self.declare_parameter(
            "lidar_name",
            "top_lidar",
            ParameterDescriptor(description="Name of the lidar sensor"),
        )

        lidar_rate_descriptor = ParameterDescriptor(
            description="Publishing rate for the lidar (Hz)",
            integer_range=[
                IntegerRange(from_value=1, to_value=30, step=1)
            ],
        )
        self.declare_parameter("lidar_rate", 10, lidar_rate_descriptor)

        self.declare_parameter(
            "lidar_model",
            "default_lidar",
            ParameterDescriptor(description="Model of the lidar sensor"),
        )

        # -- Retrieve parameters --
        self._lidar_name: str = (
            self.get_parameter("lidar_name").get_parameter_value().string_value
        )
        self._lidar_rate: int = (
            self.get_parameter("lidar_rate")
            .get_parameter_value()
            .integer_value
        )
        self._lidar_model: str = (
            self.get_parameter("lidar_model")
            .get_parameter_value()
            .string_value
        )

        self.get_logger().info(f"lidar_name: {self._lidar_name}")
        self.get_logger().info(f"lidar_rate: {self._lidar_rate}")
        self.get_logger().info(f"lidar_model: {self._lidar_model}")

        # -- Publisher --
        self._publisher = self.create_publisher(
            String, "/lidar/scan_data", 10
        )

        # -- Timer --
        self._timer = self.create_timer(
            1.0 / self._lidar_rate, self._timer_callback
        )

        # -- Parameter callback --
        self.add_on_set_parameters_callback(self._on_parameter_change)

    def _timer_callback(self) -> None:
        """Publish a simulated lidar scan message."""
        msg = String()
        msg.data = (
            f"Scan from: {self._lidar_name} (model: {self._lidar_model})"
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
            if param.name == "lidar_name":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="lidar_name must be a string",
                    )
                self._lidar_name = param.value
                self.get_logger().info(
                    f"lidar_name updated to: {self._lidar_name}"
                )

            elif param.name == "lidar_rate":
                if param.type_ != Parameter.Type.INTEGER:
                    return SetParametersResult(
                        successful=False,
                        reason="lidar_rate must be an integer",
                    )
                self._lidar_rate = param.value
                self.get_logger().info(
                    f"lidar_rate updated to: {self._lidar_rate}"
                )
                # Cancel the existing timer and recreate it
                self._timer.cancel()
                self._timer = self.create_timer(
                    1.0 / self._lidar_rate, self._timer_callback
                )

            elif param.name == "lidar_model":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="lidar_model must be a string",
                    )
                self._lidar_model = param.value
                self.get_logger().info(
                    f"lidar_model updated to: {self._lidar_model}"
                )

        return SetParametersResult(successful=True)
