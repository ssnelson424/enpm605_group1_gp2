"""ArUco marker detector that broadcasts each marker pose as a TF frame.

Subscribes to a color image topic and the matching CameraInfo topic, runs
the OpenCV ArUco detector on each frame, estimates the 6-DoF pose of every
detected marker via solvePnP, and broadcasts one TF transform per marker
with child frame ``aruco_marker_<id>``. An annotated debug image is also
republished on ``aruco_detection_image``.

Compatible with OpenCV >= 4.7 (uses ``cv2.aruco.ArucoDetector`` and
``cv2.solvePnP``; the legacy ``DetectorParameters_create`` and
``estimatePoseSingleMarkers`` APIs were removed in recent releases).
"""

import cv2
import numpy as np
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import TransformBroadcaster


class ArucoDetectorDemo(Node):
    """Detects ArUco markers and publishes their pose as TF frames."""

    def __init__(self):
        super().__init__("aruco_detector")

        # Parameters
        self.declare_parameter("camera_image_topic", "/camera/color/image_raw")
        self.declare_parameter("camera_info_topic", "/camera/color/camera_info")
        self.declare_parameter("marker_size", 0.194)  # meters
        self.declare_parameter("dictionary_id", "DICT_5X5_250")
        self.declare_parameter("publish_tf", True)

        self._camera_image_topic = (
            self.get_parameter("camera_image_topic").get_parameter_value().string_value
        )
        self._camera_info_topic = (
            self.get_parameter("camera_info_topic").get_parameter_value().string_value
        )
        self._marker_size = (
            self.get_parameter("marker_size").get_parameter_value().double_value
        )
        self._dictionary_id_str = (
            self.get_parameter("dictionary_id").get_parameter_value().string_value
        )
        self._publish_tf = (
            self.get_parameter("publish_tf").get_parameter_value().bool_value
        )

        # Camera calibration (populated by camera_info callback)
        self._camera_matrix = None
        self._dist_coeffs = None

        # CV bridge + OpenCV ArUco detector (new API)
        self._bridge = CvBridge()
        dict_const = getattr(cv2.aruco, self._dictionary_id_str)
        self._dictionary = cv2.aruco.getPredefinedDictionary(dict_const)
        self._detector_params = cv2.aruco.DetectorParameters()
        self._detector = cv2.aruco.ArucoDetector(
            self._dictionary, self._detector_params
        )

        # Object points for a single marker centered at its own origin,
        # with the marker lying in the XY plane (Z up out of the marker).
        # Order matches the corner order returned by detectMarkers:
        # top-left, top-right, bottom-right, bottom-left.
        half = self._marker_size / 2.0
        self._marker_object_points = np.array(
            [
                [-half,  half, 0.0],
                [ half,  half, 0.0],
                [ half, -half, 0.0],
                [-half, -half, 0.0],
            ],
            dtype=np.float32,
        )

        # QoS matching typical Gazebo camera publishers
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self._image_sub = self.create_subscription(
            Image, self._camera_image_topic, self._image_callback, sensor_qos
        )
        self._info_sub = self.create_subscription(
            CameraInfo, self._camera_info_topic, self._camera_info_callback, sensor_qos
        )
        self._debug_image_pub = self.create_publisher(
            Image, "aruco_detection_image", 10
        )

        self._tf_broadcaster = TransformBroadcaster(self) if self._publish_tf else None

        self.get_logger().info(
            f"ArUco detector started: image={self._camera_image_topic}, "
            f"info={self._camera_info_topic}, "
            f"dict={self._dictionary_id_str}, marker_size={self._marker_size} m"
        )
        self.get_logger().info("Waiting for camera_info...")

    def _camera_info_callback(self, msg: CameraInfo):
        """Cache the intrinsics and stop subscribing — they are static."""
        self._camera_matrix = np.array(msg.k, dtype=np.float64).reshape(3, 3)
        self._dist_coeffs = np.array(msg.d, dtype=np.float64)
        self.get_logger().info(
            f"Camera intrinsics received:\n{self._camera_matrix}\n"
            f"distortion={self._dist_coeffs}"
        )
        self.destroy_subscription(self._info_sub)

    def _image_callback(self, msg: Image):
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

        if ids is not None and len(ids) > 0:
            for i, marker_id in enumerate(ids.flatten()):
                # Per-marker pose via solvePnP (IPPE_SQUARE is designed for
                # planar square markers and is the recommended replacement
                # for the removed estimatePoseSingleMarkers).
                image_points = corners[i].reshape(-1, 2).astype(np.float32)
                success, rvec, tvec = cv2.solvePnP(
                    self._marker_object_points,
                    image_points,
                    self._camera_matrix,
                    self._dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE,
                )
                if not success:
                    self.get_logger().warn(
                        f"solvePnP failed for marker {int(marker_id)}"
                    )
                    continue

                if self._publish_tf:
                    self._broadcast_marker_tf(
                        msg.header, int(marker_id), rvec, tvec
                    )

                # Draw pose axes for the debug image
                cv2.drawFrameAxes(
                    cv_image,
                    self._camera_matrix,
                    self._dist_coeffs,
                    rvec,
                    tvec,
                    self._marker_size * 0.5,
                )

            cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)

            self.get_logger().info(
                f"Detected markers: {sorted(int(i) for i in ids.flatten())}",
                throttle_duration_sec=1.0,
            )

        # Publish annotated debug image
        try:
            debug_msg = self._bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            debug_msg.header = msg.header
            self._debug_image_pub.publish(debug_msg)
        except Exception as e:
            self.get_logger().error(f"Debug image publish failed: {e}")

    def _broadcast_marker_tf(
        self,
        image_header,
        marker_id: int,
        rvec: np.ndarray,
        tvec: np.ndarray,
    ):
        """Broadcast a TF transform from the camera optical frame to the marker."""
        t = TransformStamped()
        t.header.stamp = image_header.stamp
        t.header.frame_id = image_header.frame_id  # camera optical frame
        t.child_frame_id = f"aruco_marker_{marker_id}"

        t.transform.translation.x = float(tvec[0])
        t.transform.translation.y = float(tvec[1])
        t.transform.translation.z = float(tvec[2])

        # rvec (Rodrigues) -> rotation matrix -> quaternion
        rot_matrix, _ = cv2.Rodrigues(rvec)
        qx, qy, qz, qw = _rotation_matrix_to_quaternion(rot_matrix)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self._tf_broadcaster.sendTransform(t)


def _rotation_matrix_to_quaternion(m: np.ndarray):
    """Convert a 3x3 rotation matrix to (x, y, z, w) quaternion."""
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0.0:
        s = 0.5 / np.sqrt(trace + 1.0)
        qw = 0.25 / s
        qx = (m[2, 1] - m[1, 2]) * s
        qy = (m[0, 2] - m[2, 0]) * s
        qz = (m[1, 0] - m[0, 1]) * s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
        qw = (m[2, 1] - m[1, 2]) / s
        qx = 0.25 * s
        qy = (m[0, 1] + m[1, 0]) / s
        qz = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
        qw = (m[0, 2] - m[2, 0]) / s
        qx = (m[0, 1] + m[1, 0]) / s
        qy = 0.25 * s
        qz = (m[1, 2] + m[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
        qw = (m[1, 0] - m[0, 1]) / s
        qx = (m[0, 2] + m[2, 0]) / s
        qy = (m[1, 2] + m[2, 1]) / s
        qz = 0.25 * s
    return float(qx), float(qy), float(qz), float(qw)
