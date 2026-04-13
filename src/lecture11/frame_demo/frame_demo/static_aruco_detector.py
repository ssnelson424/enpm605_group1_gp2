"""Detect a single ArUco marker and publish its pose as a static TF frame.

Subscribes to a color image topic and matching CameraInfo topic, runs
OpenCV's ``ArucoDetector`` until one marker is detected with a valid
``solvePnP`` solution, then publishes a single static transform from the
camera optical frame to a child frame named ``static_aruco_box`` using
``StaticTransformBroadcaster`` (latched on ``/tf_static``). After the
static transform is published the node stops processing further frames.
"""

import cv2
import numpy as np
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import StaticTransformBroadcaster


class StaticArucoDetector(Node):
    """Detects one ArUco marker and publishes a single static TF."""

    def __init__(self):
        super().__init__("static_aruco_detector")

        self.declare_parameter("camera_image_topic", "/overhead_camera/image_raw")
        self.declare_parameter("camera_info_topic", "/overhead_camera/camera_info")
        self.declare_parameter("marker_size", 0.1)  # meters
        self.declare_parameter("dictionary_id", "DICT_5X5_250")
        self.declare_parameter("child_frame_id", "static_aruco_box")
        # Optional override for the TF parent frame. solvePnP returns a pose
        # in the camera *optical* convention (X right, Y down, Z forward),
        # but the image header usually carries a ROS-convention mounting
        # frame. Set this to an optical-frame name to publish correctly.
        # Empty string => fall back to image_header.frame_id.
        self.declare_parameter("parent_frame_id", "")

        self._camera_image_topic = self.get_parameter("camera_image_topic").value
        self._camera_info_topic = self.get_parameter("camera_info_topic").value
        self._marker_size = self.get_parameter("marker_size").value
        self._dictionary_id_str = self.get_parameter("dictionary_id").value
        self._child_frame_id = self.get_parameter("child_frame_id").value
        self._parent_frame_id = self.get_parameter("parent_frame_id").value

        self._camera_matrix = None
        self._dist_coeffs = None
        self._tf_published = False

        self._bridge = CvBridge()
        dict_const = getattr(cv2.aruco, self._dictionary_id_str)
        self._detector = cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(dict_const),
            cv2.aruco.DetectorParameters(),
        )

        half = self._marker_size / 2.0
        self._marker_object_points = np.array(
            [[-half, half, 0.0], [half, half, 0.0],
             [half, -half, 0.0], [-half, -half, 0.0]],
            dtype=np.float32,
        )

        self._image_sub = self.create_subscription(
            Image, self._camera_image_topic,
            self._image_callback, qos_profile_sensor_data,
        )
        self._info_sub = self.create_subscription(
            CameraInfo, self._camera_info_topic,
            self._camera_info_callback, qos_profile_sensor_data,
        )

        self._static_tf_broadcaster = StaticTransformBroadcaster(self)

        self.get_logger().info(
            f"Static ArUco detector started: image={self._camera_image_topic}, "
            f"info={self._camera_info_topic}, "
            f"dict={self._dictionary_id_str}, marker_size={self._marker_size} m, "
            f"child_frame_id={self._child_frame_id}"
        )
        self.get_logger().info("Waiting for camera_info...")

    def _camera_info_callback(self, msg: CameraInfo):
        self._camera_matrix = np.array(msg.k, dtype=np.float64).reshape(3, 3)
        self._dist_coeffs = np.array(msg.d, dtype=np.float64)
        self.get_logger().info(
            f"Camera intrinsics received:\n{self._camera_matrix}\n"
            f"distortion={self._dist_coeffs}"
        )
        self.destroy_subscription(self._info_sub)

    def _image_callback(self, msg: Image):
        if self._tf_published:
            return
        if self._camera_matrix is None:
            self.get_logger().warn(
                "Image received before camera_info; skipping.",
                throttle_duration_sec=2.0,
            )
            return

        try:
            cv_image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge conversion failed: {e}")
            return

        corners, ids, _ = self._detector.detectMarkers(cv_image)
        if ids is None or len(ids) == 0:
            return

        image_points = corners[0].reshape(-1, 2).astype(np.float32)
        success, rvec, tvec = cv2.solvePnP(
            self._marker_object_points,
            image_points,
            self._camera_matrix,
            self._dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE,
        )
        if not success:
            self.get_logger().warn("solvePnP failed; waiting for another frame.")
            return

        self._publish_static_tf(msg.header, rvec, tvec)
        self._tf_published = True
        self.get_logger().info(
            f"Published static TF {msg.header.frame_id} -> {self._child_frame_id} "
            f"(marker id {int(ids.flatten()[0])}); halting further detection."
        )
        self.destroy_subscription(self._image_sub)

    def _publish_static_tf(self, image_header, rvec, tvec):
        qx, qy, qz, qw = Rotation.from_rotvec(rvec.flatten()).as_quat()

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self._parent_frame_id or image_header.frame_id
        t.child_frame_id = self._child_frame_id
        t.transform.translation.x = float(tvec[0])
        t.transform.translation.y = float(tvec[1])
        t.transform.translation.z = float(tvec[2])
        t.transform.rotation.x = float(qx)
        t.transform.rotation.y = float(qy)
        t.transform.rotation.z = float(qz)
        t.transform.rotation.w = float(qw)

        self._static_tf_broadcaster.sendTransform(t)
