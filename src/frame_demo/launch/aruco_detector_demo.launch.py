from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    camera_image_topic_arg = DeclareLaunchArgument(
        "camera_image_topic",
        default_value="/oak/rgb/color",
        description="Color image topic to subscribe to",
    )
    camera_info_topic_arg = DeclareLaunchArgument(
        "camera_info_topic",
        default_value="/oak/stereo/camera_info",
        description="CameraInfo topic matching the image topic",
    )
    marker_size_arg = DeclareLaunchArgument(
        "marker_size",
        default_value="0.194",
        description="Physical edge length of each ArUco marker (meters)",
    )
    dictionary_id_arg = DeclareLaunchArgument(
        "dictionary_id",
        default_value="DICT_5X5_250",
        description="OpenCV ArUco dictionary constant name",
    )
    publish_tf_arg = DeclareLaunchArgument(
        "publish_tf",
        default_value="true",
        description="Whether to broadcast TF frames for detected markers",
    )

    aruco_detector_node = Node(
        package="frame_demo",
        executable="aruco_detector",
        output="screen",
        parameters=[
            {
                "camera_image_topic": LaunchConfiguration("camera_image_topic"),
                "camera_info_topic": LaunchConfiguration("camera_info_topic"),
                "marker_size": LaunchConfiguration("marker_size"),
                "dictionary_id": LaunchConfiguration("dictionary_id"),
                "publish_tf": LaunchConfiguration("publish_tf"),
            }
        ],
    )

    ld = LaunchDescription()
    ld.add_action(camera_image_topic_arg)
    ld.add_action(camera_info_topic_arg)
    ld.add_action(marker_size_arg)
    ld.add_action(dictionary_id_arg)
    ld.add_action(publish_tf_arg)
    ld.add_action(aruco_detector_node)
    return ld
