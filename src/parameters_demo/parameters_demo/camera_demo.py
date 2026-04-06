"""Camera demo node with dynamic parameters.

This module demonstrates how to declare, retrieve, and dynamically
update ROS 2 parameters using ParameterDescriptor and parameter
callbacks.
"""

from sensor_msgs.msg import Image
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
            node_name: Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)

        # -- Declare parameters (matching the sensor parameter table) --
        # Freely writable parameters
        self.declare_parameter(
            "camera_name", "front_cam",
            ParameterDescriptor(description="Name of the camera"),
        )
        self.declare_parameter(
            "camera_frame_id", "cam_link",
            ParameterDescriptor(description="TF frame ID for the camera"),
        )
        self.declare_parameter(
            "exposure_auto", True,
            ParameterDescriptor(description="Enable auto exposure"),
        )
        self.declare_parameter(
            "exposure_time_us", 10000,
            ParameterDescriptor(description="Manual exposure time in microseconds"),
        )
        self.declare_parameter(
            "brightness", 128,
            ParameterDescriptor(
                description="Image brightness",
                integer_range=[IntegerRange(from_value=0, to_value=255, step=1)],
            ),
        )

        # Timer rebuild required
        self.declare_parameter(
            "fps", 30,
            ParameterDescriptor(
                description="Camera frame rate in Hz",
                integer_range=[IntegerRange(from_value=1, to_value=60, step=1)],
            ),
        )

        # Node restart required
        self.declare_parameter(
            "image_width", 1920,
            ParameterDescriptor(description="Image width in pixels (requires restart)"),
        )
        self.declare_parameter(
            "image_height", 1080,
            ParameterDescriptor(description="Image height in pixels (requires restart)"),
        )
        self.declare_parameter(
            "encoding", "bgr8",
            ParameterDescriptor(description="Image encoding format (requires restart)"),
        )
        self.declare_parameter(
            "camera_info_url", "",
            ParameterDescriptor(description="Path to camera calibration file (requires restart)"),
        )

        # -- Retrieve parameters --
        self._camera_name: str = (
            self.get_parameter("camera_name").get_parameter_value().string_value
        )
        self._camera_frame_id: str = (
            self.get_parameter("camera_frame_id").get_parameter_value().string_value
        )
        self._fps: int = (
            self.get_parameter("fps").get_parameter_value().integer_value
        )
        self._exposure_auto: bool = (
            self.get_parameter("exposure_auto").get_parameter_value().bool_value
        )
        self._exposure_time_us: int = (
            self.get_parameter("exposure_time_us").get_parameter_value().integer_value
        )
        self._brightness: int = (
            self.get_parameter("brightness").get_parameter_value().integer_value
        )
        self._image_width: int = (
            self.get_parameter("image_width").get_parameter_value().integer_value
        )
        self._image_height: int = (
            self.get_parameter("image_height").get_parameter_value().integer_value
        )
        self._encoding: str = (
            self.get_parameter("encoding").get_parameter_value().string_value
        )

        self.get_logger().info(f"camera_name: {self._camera_name}")
        self.get_logger().info(f"camera_frame_id: {self._camera_frame_id}")
        self.get_logger().info(f"fps: {self._fps}")

        # -- Publisher --
        self._publisher = self.create_publisher(
            Image, "/camera/image_color", 10
        )

        # -- Timer --
        self._image_timer = self.create_timer(
            1.0 / self._fps, self._image_pub_callback
        )

        # -- Parameter callback --
        self.add_on_set_parameters_callback(self._parameter_update_cb)

    def _image_pub_callback(self) -> None:
        """Publish a simulated camera Image message using current parameters."""
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._camera_frame_id
        msg.height = self._image_height
        msg.width = self._image_width
        msg.encoding = self._encoding
        msg.is_bigendian = 0
        msg.step = self._image_width * 3  # assume 3 bytes per pixel (bgr8)
        msg.data = bytes(msg.step * msg.height)  # zero-filled placeholder

        self._publisher.publish(msg)

        exposure = (
            "auto" if self._exposure_auto else f"{self._exposure_time_us} us"
        )
        self.get_logger().info(
            f"[{self._camera_name}] {msg.width}x{msg.height} "
            f"{msg.encoding}, fps={self._fps}, exposure={exposure}, "
            f"brightness={self._brightness}"
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

            elif param.name == "camera_frame_id":
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason="camera_frame_id must be a string",
                    )
                self._camera_frame_id = param.value

            elif param.name == "exposure_auto":
                if param.type_ != Parameter.Type.BOOL:
                    return SetParametersResult(
                        successful=False,
                        reason="exposure_auto must be a bool",
                    )
                self._exposure_auto = param.value

            elif param.name == "exposure_time_us":
                if param.type_ != Parameter.Type.INTEGER:
                    return SetParametersResult(
                        successful=False,
                        reason="exposure_time_us must be an integer",
                    )
                self._exposure_time_us = param.value

            elif param.name == "brightness":
                if param.type_ != Parameter.Type.INTEGER:
                    return SetParametersResult(
                        successful=False,
                        reason="brightness must be an integer",
                    )
                self._brightness = param.value

            elif param.name == "fps":
                if param.type_ != Parameter.Type.INTEGER:
                    return SetParametersResult(
                        successful=False,
                        reason="fps must be an integer",
                    )
                self._fps = param.value
                self.get_logger().info(f"fps updated to: {self._fps}")
                # Cancel the existing timer and recreate it
                self._image_timer.cancel()
                self._image_timer = self.create_timer(
                    1.0 / self._fps, self._image_pub_callback
                )

        return SetParametersResult(successful=True)
