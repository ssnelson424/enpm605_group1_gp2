"""Demonstrate manual transform composition with PyKDL.

Rather than asking tf2 to chain the two hops implicitly, this node looks
up each hop on its own:

    odom -> overhead_camera_optical_frame
    overhead_camera_optical_frame -> static_aruco_box

and composes them locally with PyKDL:

    T_odom_box = T_odom_camera * T_camera_box

The composed pose is logged. Students can compare the KDL result with a
direct ``lookup_transform(odom, static_aruco_box)`` to confirm that KDL
and TF2 produce identical answers; KDL just makes the chaining explicit.
"""

import PyKDL
import rclpy
from geometry_msgs.msg import Pose, TransformStamped
from rclpy.duration import Duration
from rclpy.node import Node
from tf2_ros import Buffer, TransformException, TransformListener


def transform_to_kdl(t: TransformStamped) -> PyKDL.Frame:
    """Convert a ``TransformStamped`` into a ``PyKDL.Frame``."""
    p = t.transform.translation
    q = t.transform.rotation
    return PyKDL.Frame(
        PyKDL.Rotation.Quaternion(q.x, q.y, q.z, q.w),
        PyKDL.Vector(p.x, p.y, p.z),
    )


def kdl_to_pose(frame: PyKDL.Frame) -> Pose:
    """Convert a ``PyKDL.Frame`` into a ``geometry_msgs/Pose``."""
    pose = Pose()
    pose.position.x = frame.p.x()
    pose.position.y = frame.p.y()
    pose.position.z = frame.p.z()
    qx, qy, qz, qw = frame.M.GetQuaternion()
    pose.orientation.x = qx
    pose.orientation.y = qy
    pose.orientation.z = qz
    pose.orientation.w = qw
    return pose


class KdlChainDemo(Node):
    """Compose two TF hops manually with PyKDL and log the result."""

    def __init__(self):
        super().__init__("kdl_chain_demo")

        self.declare_parameter("target_frame", "odom")
        self.declare_parameter("intermediate_frame", "overhead_camera_optical_frame")
        self.declare_parameter("source_frame", "static_aruco_box")
        self.declare_parameter("period", 1.0)

        self._target = self.get_parameter("target_frame").value
        self._middle = self.get_parameter("intermediate_frame").value
        self._source = self.get_parameter("source_frame").value
        period = float(self.get_parameter("period").value)

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        self._timer = self.create_timer(period, self._timer_callback)

        self.get_logger().info(
            f"KDL chain demo: {self._target} <- {self._middle} <- {self._source}"
        )

    def _timer_callback(self):
        try:
            t_target_middle = self._tf_buffer.lookup_transform(
                self._target, self._middle, rclpy.time.Time(),
                timeout=Duration(seconds=0.1),
            )
            t_middle_source = self._tf_buffer.lookup_transform(
                self._middle, self._source, rclpy.time.Time(),
                timeout=Duration(seconds=0.1),
            )
        except TransformException as e:
            self.get_logger().warn(
                f"TF lookup failed: {e}", throttle_duration_sec=2.0
            )
            return

        # Step 1: convert both TFs to KDL frames.
        kdl_target_middle = transform_to_kdl(t_target_middle)
        kdl_middle_source = transform_to_kdl(t_middle_source)

        # Step 2: chain them via KDL multiplication.
        kdl_target_source = kdl_target_middle * kdl_middle_source

        # Step 3: convert back to a ROS Pose.
        pose = kdl_to_pose(kdl_target_source)
        p, o = pose.position, pose.orientation
        self.get_logger().info(
            f"KDL-composed {self._source} in {self._target}: "
            f"pos=({p.x:.3f}, {p.y:.3f}, {p.z:.3f}) "
            f"quat=({o.x:.3f}, {o.y:.3f}, {o.z:.3f}, {o.w:.3f})"
        )
