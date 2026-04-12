"""Launch file that starts camera_demo and lidar_demo using a YAML parameter file."""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Generate a launch description for camera_demo and lidar_demo nodes.

    Both nodes load their parameters from the shared YAML configuration
    file located in the package's config directory.

    Returns:
        LaunchDescription: Launch description with both nodes configured
            via the YAML parameter file.
    """
    parameter_file = PathJoinSubstitution([
        FindPackageShare("parameters_demo"),
        "config",
        "parameters_demo.yaml",
    ])

    camera_demo = Node(
        package="parameters_demo",
        executable="camera_demo",
        name="camera_demo",
        parameters=[parameter_file],
    )

    lidar_demo = Node(
        package="parameters_demo",
        executable="lidar_demo",
        name="lidar_demo",
        parameters=[parameter_file],
    )

    return LaunchDescription([camera_demo, lidar_demo])
