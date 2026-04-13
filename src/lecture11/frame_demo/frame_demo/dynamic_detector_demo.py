"""ArUco marker detector that broadcasts each marker pose as a TF frame.

The node subscribes to a color image topic and the matching CameraInfo
topic, runs OpenCV's ``ArucoDetector`` on every frame, estimates the
6-DoF pose of each detected marker with ``cv2.solvePnP`` (using the
``IPPE_SQUARE`` solver, designed for planar square markers), and
broadcasts one TF transform per marker. The child frame is named
``aruco_marker_<id>`` where ``<id>`` is the integer marker ID, so
different markers produce distinct frames automatically. The parent
frame is copied from the incoming image's ``header.frame_id`` (the
camera optical frame), which makes the published transforms usable by
downstream nodes that already know the camera's place in the TF tree.

An annotated debug image with marker outlines and pose axes is
republished on ``aruco_detection_image`` for quick visual verification
in ``rqt_image_view``.

Defaults target the rosbot_xl simulated OAK-D camera
(``/oak/rgb/color`` + ``/oak/stereo/camera_info``, since the sim bridges
only the stereo CameraInfo); all topic names, the marker size, the
ArUco dictionary, and the TF-publishing flag are exposed as ROS
parameters and overridable via launch arguments.
"""

import cv2
import numpy as np
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import TransformBroadcaster


class ArucoDetectorDemo(Node):
    """Detects ArUco markers and publishes their pose as TF frames."""

    def __init__(self):
        """Initialize the ArUco detector node.

        Declares ROS parameters (camera topics, marker size, dictionary ID,
        TF publishing flag), sets up the OpenCV ``ArucoDetector`` with the
        chosen dictionary, creates subscriptions for the color image and
        CameraInfo topics using sensor-data QoS, and initializes the TF
        broadcaster and debug-image publisher.
        """
        super().__init__("aruco_detector")

        # Parameters
        self.declare_parameter("camera_image_topic", "/oak/rgb/color")
        self.declare_parameter("camera_info_topic", "/oak/stereo/camera_info")
        self.declare_parameter("marker_size", 0.194)  # meters
        self.declare_parameter("dictionary_id", "DICT_5X5_250")
        self.declare_parameter("publish_tf", True)
        # solvePnP returns a pose in the camera *optical* convention
        # (X right, Y down, Z forward), but the image header usually
        # carries the ROS-convention mounting frame. Set this to the
        # camera's optical frame for the TFs to land correctly.
        # Empty => fall back to image_header.frame_id.
        self.declare_parameter("parent_frame_id", "")

        self._camera_image_topic = self.get_parameter("camera_image_topic").value
        self._camera_info_topic = self.get_parameter("camera_info_topic").value
        self._marker_size = self.get_parameter("marker_size").value
        self._dictionary_id_str = self.get_parameter("dictionary_id").value
        self._publish_tf = self.get_parameter("publish_tf").value
        self._parent_frame_id = self.get_parameter("parent_frame_id").value

        # Camera calibration (populated by camera_info callback)
        self._camera_matrix = None
        self._dist_coeffs = None

        # CV bridge + OpenCV ArUco detector (new API)
        self._bridge = CvBridge()
        dict_const = getattr(cv2.aruco, self._dictionary_id_str)
        self._detector = cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(dict_const),
            cv2.aruco.DetectorParameters(),
        )

        # Object points for a single marker centered at its own origin,
        # lying in the XY plane. Order matches detectMarkers corner order:
        # top-left, top-right, bottom-right, bottom-left.
        half = self._marker_size / 2.0
        self._marker_object_points = np.array(
            [[-half, half, 0.0], [half, half, 0.0],
             [half, -half, 0.0], [-half, -half, 0.0]],
            dtype=np.float32,
        )

        # Standard sensor-data QoS (BEST_EFFORT) — compatible with both
        # RELIABLE and BEST_EFFORT publishers, the convention for cameras.
        self._image_sub = self.create_subscription(
            Image, self._camera_image_topic,
            self._image_callback, qos_profile_sensor_data,
        )
        self._info_sub = self.create_subscription(
            CameraInfo, self._camera_info_topic,
            self._camera_info_callback, qos_profile_sensor_data,
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
        """Process a single CameraInfo message and unsubscribe.

        Extracts the 3x3 intrinsic matrix (K) and the distortion
        coefficients (D) from the message, stores them for use by the
        image callback, and destroys the subscription since camera
        intrinsics are static and only need to be received once.

        Args:
            msg: CameraInfo message containing the camera calibration data.
        """
        self._camera_matrix = np.array(msg.k, dtype=np.float64).reshape(3, 3)
        self._dist_coeffs = np.array(msg.d, dtype=np.float64)
        self.get_logger().info(
            f"Camera intrinsics received:\n{self._camera_matrix}\n"
            f"distortion={self._dist_coeffs}"
        )
        self.destroy_subscription(self._info_sub)

    def _image_callback(self, msg: Image):
        """Process each incoming camera frame for ArUco marker detection.

        Converts the ROS Image to an OpenCV BGR image via ``cv_bridge``,
        runs the ArUco detector to find marker corners and IDs, estimates
        each marker's 6-DoF pose using ``cv2.solvePnP`` with the
        ``IPPE_SQUARE`` solver, optionally broadcasts TF transforms, and
        publishes an annotated debug image with marker outlines and pose
        axes drawn on it.

        Skips processing if camera intrinsics have not yet been received.

        Args:
            msg: ROS Image message from the color camera topic.
        """
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
                # Per-marker pose via solvePnP with IPPE_SQUARE — the
                # recommended replacement for the removed
                # estimatePoseSingleMarkers on planar square markers.
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

                cv2.drawFrameAxes(
                    cv_image, self._camera_matrix, self._dist_coeffs,
                    rvec, tvec, self._marker_size * 0.5,
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

    def _broadcast_marker_tf(self, image_header, marker_id, rvec, tvec):
        """Broadcast a TF transform from the camera optical frame to a marker.

        Converts the Rodrigues rotation vector to a quaternion using
        scipy and publishes a ``TransformStamped`` message. The parent
        frame is taken from the image header (camera optical frame) and
        the child frame is named ``aruco_marker_<marker_id>``.

        Args:
            image_header: The ``std_msgs/Header`` from the source image,
                providing the timestamp and parent frame ID.
            marker_id: Integer ID of the detected ArUco marker, used to
                form the child frame name.
            rvec: Rodrigues rotation vector (3x1) from ``solvePnP``,
                representing the marker's orientation relative to the camera.
            tvec: Translation vector (3x1) from ``solvePnP``, representing
                the marker's position relative to the camera in meters.
        """
        # rvec (Rodrigues vector) -> quaternion [x, y, z, w] via scipy.
        qx, qy, qz, qw = Rotation.from_rotvec(rvec.flatten()).as_quat()

        t = TransformStamped()
        t.header.stamp = image_header.stamp
        t.header.frame_id = self._parent_frame_id or image_header.frame_id
        t.child_frame_id = f"aruco_marker_{marker_id}"
        t.transform.translation.x = float(tvec[0])
        t.transform.translation.y = float(tvec[1])
        t.transform.translation.z = float(tvec[2])
        t.transform.rotation.x = float(qx)
        t.transform.rotation.y = float(qy)
        t.transform.rotation.z = float(qz)
        t.transform.rotation.w = float(qw)

        self._tf_broadcaster.sendTransform(t)
