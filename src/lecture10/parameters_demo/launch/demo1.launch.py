"""Launch file that starts camera_demo with inline parameters."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Generate a launch description for the camera_demo node.

    Returns:
        LaunchDescription: Launch description with camera_demo node
            configured with inline parameters.
    """
    camera_demo = Node(
        package="parameters_demo",
        executable="camera_demo",
        name="camera_demo",
        parameters=[
            {
                "camera_name": "rear_cam",
                "fps": 15,
            }
        ],
    )

    return LaunchDescription([camera_demo])
