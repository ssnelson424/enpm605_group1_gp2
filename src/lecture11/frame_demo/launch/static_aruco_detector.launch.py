from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    camera_image_topic_arg = DeclareLaunchArgument(
        "camera_image_topic",
        default_value="/overhead_camera/image_raw",
        description="Color image topic to subscribe to",
    )
    camera_info_topic_arg = DeclareLaunchArgument(
        "camera_info_topic",
        default_value="/overhead_camera/camera_info",
        description="CameraInfo topic matching the image topic",
    )
    marker_size_arg = DeclareLaunchArgument(
        "marker_size",
        default_value="0.1",
        description="Physical edge length of the ArUco marker (meters)",
    )
    dictionary_id_arg = DeclareLaunchArgument(
        "dictionary_id",
        default_value="DICT_5X5_250",
        description="OpenCV ArUco dictionary constant name",
    )
    child_frame_id_arg = DeclareLaunchArgument(
        "child_frame_id",
        default_value="static_aruco_box",
        description="Child frame name for the published static transform",
    )

    # Broadcast the overhead camera's fixed pose (from the world SDF)
    # as a static transform from odom -> overhead_camera so the camera
    # frame is connected to the robot's TF tree.
    camera_static_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="overhead_camera_static_tf",
        arguments=[
            "--x", "2.0",
            "--y", "2.0",
            "--z", "2.0",
            "--roll", "0.0",
            "--pitch", "1.5708",
            "--yaw", "0.0",
            "--frame-id", "odom",
            "--child-frame-id", "overhead_camera",
        ],
        output="screen",
    )

    static_aruco_detector_node = Node(
        package="frame_demo",
        executable="static_aruco_detector",
        output="screen",
        parameters=[
            {
                "camera_image_topic": LaunchConfiguration("camera_image_topic"),
                "camera_info_topic": LaunchConfiguration("camera_info_topic"),
                "marker_size": LaunchConfiguration("marker_size"),
                "dictionary_id": LaunchConfiguration("dictionary_id"),
                "child_frame_id": LaunchConfiguration("child_frame_id"),
            }
        ],
    )

    ld = LaunchDescription()
    ld.add_action(camera_image_topic_arg)
    ld.add_action(camera_info_topic_arg)
    ld.add_action(marker_size_arg)
    ld.add_action(dictionary_id_arg)
    ld.add_action(child_frame_id_arg)
    ld.add_action(camera_static_tf_node)
    ld.add_action(static_aruco_detector_node)
    return ld
