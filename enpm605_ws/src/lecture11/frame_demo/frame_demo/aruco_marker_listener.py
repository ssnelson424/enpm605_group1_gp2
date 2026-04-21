"""Listen for ArUco marker TF frames and print each pose in a target frame.

Periodically inspects the TF buffer, picks out every frame whose name
starts with a configurable prefix (``aruco_marker_`` by default), and
looks up its transform in a target frame (``odom`` by default). Prints
the (x, y, z) translation for each marker. New markers are discovered
automatically as the detector publishes their frames.
"""

import rclpy
import yaml
from rclpy.duration import Duration
from rclpy.node import Node
from tf2_ros import Buffer, TransformException, TransformListener


class ArucoMarkerListener(Node):
    """Listens for `aruco_marker_*` frames and reports their pose in a target frame."""

    def __init__(self):
        super().__init__("aruco_marker_listener")

        self.declare_parameter("target_frame", "odom")
        self.declare_parameter("marker_prefix", "aruco_marker_")
        self.declare_parameter("period", 1.0)

        self._target_frame = self.get_parameter("target_frame").value
        self._marker_prefix = self.get_parameter("marker_prefix").value
        period = float(self.get_parameter("period").value)

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        self._timer = self.create_timer(period, self._timer_callback)

        self.get_logger().info(
            f"Listening for frames '{self._marker_prefix}*' "
            f"in target frame '{self._target_frame}' every {period:.1f} s."
        )

    def _timer_callback(self):
        marker_frames = self._discover_marker_frames()
        if not marker_frames:
            self.get_logger().info(
                "No marker frames in TF yet.",
                throttle_duration_sec=5.0,
            )
            return

        for frame in marker_frames:
            try:
                t = self._tf_buffer.lookup_transform(
                    self._target_frame,
                    frame,
                    rclpy.time.Time(),  # latest available
                    timeout=Duration(seconds=0.1),
                )
            except TransformException as e:
                self.get_logger().warn(
                    f"Could not transform {frame} -> {self._target_frame}: {e}",
                    throttle_duration_sec=2.0,
                )
                continue

            p = t.transform.translation
            self.get_logger().info(
                f"{frame} in {self._target_frame}: "
                f"x={p.x:.3f}, y={p.y:.3f}, z={p.z:.3f}"
            )

    def _discover_marker_frames(self):
        """Return sorted list of frames in the TF buffer matching the prefix."""
        try:
            frames = yaml.safe_load(self._tf_buffer.all_frames_as_yaml()) or {}
        except yaml.YAMLError:
            return []
        return sorted(
            name for name in frames if name.startswith(self._marker_prefix)
        )
