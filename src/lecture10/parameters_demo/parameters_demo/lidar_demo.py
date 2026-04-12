"""Lidar demo node with dynamic parameters.

This module demonstrates how to declare, retrieve, and dynamically
update ROS 2 parameters for a simulated lidar sensor.
"""

import math

from sensor_msgs.msg import LaserScan
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import (
    ParameterDescriptor,
    FloatingPointRange,
    IntegerRange,
    SetParametersResult,
)


class LidarDemo(Node):
    """A node that publishes simulated lidar scan data at a configurable rate."""

    def __init__(self, node_name: str):
        """Initialize the node, declare parameters, and start the timer.

        Args:
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)

        # -- Declare parameters (matching the sensor parameter table) --
        # Freely writable parameters
        self.declare_parameter(
            "lidar_name", "top_lidar",
            ParameterDescriptor(description="Name of the lidar sensor"),
        )
        self.declare_parameter(
            "lidar_frame_id", "lidar_link",
            ParameterDescriptor(description="TF frame ID for the lidar"),
        )
        self.declare_parameter(
            "min_range", 0.1,
            ParameterDescriptor(
                description="Minimum detection range in meters",
                floating_point_range=[
                    FloatingPointRange(from_value=0.0, to_value=10.0, step=0.0)
                ],
            ),
        )
        self.declare_parameter(
            "max_range", 100.0,
            ParameterDescriptor(
                description="Maximum detection range in meters",
                floating_point_range=[
                    FloatingPointRange(from_value=1.0, to_value=300.0, step=0.0)
                ],
            ),
        )
        self.declare_parameter(
            "min_angle", -3.14159,
            ParameterDescriptor(description="Minimum scan angle in radians"),
        )
        self.declare_parameter(
            "max_angle", 3.14159,
            ParameterDescriptor(description="Maximum scan angle in radians"),
        )
        self.declare_parameter(
            "intensity_threshold", 0.0,
            ParameterDescriptor(description="Minimum intensity to report a return"),
        )

        # Timer rebuild required
        self.declare_parameter(
            "scan_frequency", 10,
            ParameterDescriptor(
                description="Scan frequency in Hz",
                integer_range=[IntegerRange(from_value=1, to_value=30, step=1)],
            ),
        )

        # Node restart required
        self.declare_parameter(
            "port", "/dev/lidar0",
            ParameterDescriptor(description="Serial port for the lidar (requires restart)"),
        )
        self.declare_parameter(
            "return_mode", "strongest",
            ParameterDescriptor(description="Return mode: strongest, last, dual (requires restart)"),
        )

        # Extra parameter for launch file argument demo
        self.declare_parameter(
            "lidar_model", "default_lidar",
            ParameterDescriptor(description="Model of the lidar sensor"),
        )

        # -- Retrieve parameters --
        self._lidar_name: str = (
            self.get_parameter("lidar_name").get_parameter_value().string_value
        )
        self._lidar_frame_id: str = (
            self.get_parameter("lidar_frame_id").get_parameter_value().string_value
        )
        self._min_range: float = (
            self.get_parameter("min_range").get_parameter_value().double_value
        )
        self._max_range: float = (
            self.get_parameter("max_range").get_parameter_value().double_value
        )
        self._min_angle: float = (
            self.get_parameter("min_angle").get_parameter_value().double_value
        )
        self._max_angle: float = (
            self.get_parameter("max_angle").get_parameter_value().double_value
        )
        self._intensity_threshold: float = (
            self.get_parameter("intensity_threshold").get_parameter_value().double_value
        )
        self._scan_frequency: int = (
            self.get_parameter("scan_frequency").get_parameter_value().integer_value
        )
        self._lidar_model: str = (
            self.get_parameter("lidar_model").get_parameter_value().string_value
        )

        self.get_logger().info(f"lidar_name: {self._lidar_name}")
        self.get_logger().info(f"lidar_frame_id: {self._lidar_frame_id}")
        self.get_logger().info(f"scan_frequency: {self._scan_frequency}")
        self.get_logger().info(f"lidar_model: {self._lidar_model}")

        # -- Publisher --
        self._publisher = self.create_publisher(
            LaserScan, "/lidar/scan_data", 10
        )

        # -- Timer --
        self._scan_timer = self.create_timer(
            1.0 / self._scan_frequency, self._scan_pub_callback
        )

        # -- Parameter callback --
        self.add_on_set_parameters_callback(self._parameter_update_cb)

    def _scan_pub_callback(self) -> None:
        """Publish a simulated LaserScan message using current parameters."""
        num_readings = 360
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._lidar_frame_id
        msg.angle_min = self._min_angle
        msg.angle_max = self._max_angle
        msg.angle_increment = (
            (self._max_angle - self._min_angle) / num_readings
        )
        msg.time_increment = 0.0
        msg.scan_time = 1.0 / self._scan_frequency
        msg.range_min = self._min_range
        msg.range_max = self._max_range
        # Placeholder ranges/intensities (all at max_range)
        msg.ranges = [self._max_range] * num_readings
        msg.intensities = [self._intensity_threshold] * num_readings

        self._publisher.publish(msg)

        self.get_logger().info(
            f"[{self._lidar_name}] model={self._lidar_model}, "
            f"freq={self._scan_frequency} Hz, "
            f"range=[{self._min_range:.2f}, {self._max_range:.2f}] m, "
            f"angle=[{math.degrees(self._min_angle):.0f}, "
            f"{math.degrees(self._max_angle):.0f}] deg"
        )

    def _parameter_update_cb(
        self, params: list[Parameter]
    ) -> SetParametersResult:
        """Validate and apply parameter changes at runtime.

        Args:
            params: List of parameters being changed.

        Returns:
            Whether the parameter change was accepted.
        """
        for param in params:
            if param.name == "lidar_name":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="lidar_name must be a string",
                    )
                self._lidar_name = param.value

            elif param.name == "lidar_frame_id":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="lidar_frame_id must be a string",
                    )
                self._lidar_frame_id = param.value

            elif param.name == "min_range":
                if param.type_ != Parameter.Type.DOUBLE:
                    return SetParametersResult(
                        successful=False,
                        reason="min_range must be a double",
                    )
                self._min_range = param.value

            elif param.name == "max_range":
                if param.type_ != Parameter.Type.DOUBLE:
                    return SetParametersResult(
                        successful=False,
                        reason="max_range must be a double",
                    )
                self._max_range = param.value

            elif param.name == "min_angle":
                if param.type_ != Parameter.Type.DOUBLE:
                    return SetParametersResult(
                        successful=False,
                        reason="min_angle must be a double",
                    )
                self._min_angle = param.value

            elif param.name == "max_angle":
                if param.type_ != Parameter.Type.DOUBLE:
                    return SetParametersResult(
                        successful=False,
                        reason="max_angle must be a double",
                    )
                self._max_angle = param.value

            elif param.name == "intensity_threshold":
                if param.type_ != Parameter.Type.DOUBLE:
                    return SetParametersResult(
                        successful=False,
                        reason="intensity_threshold must be a double",
                    )
                self._intensity_threshold = param.value

            elif param.name == "scan_frequency":
                if param.type_ != Parameter.Type.INTEGER:
                    return SetParametersResult(
                        successful=False,
                        reason="scan_frequency must be an integer",
                    )
                self._scan_frequency = param.value
                self.get_logger().info(
                    f"scan_frequency updated to: {self._scan_frequency}"
                )
                # Cancel the existing timer and recreate it
                self._scan_timer.cancel()
                self._scan_timer = self.create_timer(
                    1.0 / self._scan_frequency, self._scan_pub_callback
                )

            elif param.name == "lidar_model":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="lidar_model must be a string",
                    )
                self._lidar_model = param.value

        return SetParametersResult(successful=True)
