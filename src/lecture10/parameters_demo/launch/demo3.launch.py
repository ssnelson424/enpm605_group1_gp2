"""Launch file that starts lidar_demo with a YAML file and a launch argument override."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Generate a launch description for the lidar_demo node.

    Loads parameters from the YAML file and overrides ``lidar_model``
    with a value provided via a launch argument (default: "velodyne").

    Returns:
        LaunchDescription: Launch description with lidar_demo node
            configured via YAML and a launch argument override.
    """
    parameter_file = PathJoinSubstitution([
        FindPackageShare("parameters_demo"),
        "config",
        "parameters_demo.yaml",
    ])

    lidar_model_arg = DeclareLaunchArgument(
        "lidar_model",
        default_value="velodyne",
        description="Model of the lidar sensor",
    )

    lidar_demo = Node(
        package="parameters_demo",
        executable="lidar_demo",
        name="lidar_demo",
        parameters=[
            parameter_file,
            {"lidar_model": LaunchConfiguration("lidar_model")},
        ],
    )

    return LaunchDescription([lidar_model_arg, lidar_demo])
