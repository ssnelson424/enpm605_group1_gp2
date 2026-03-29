from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    talker_arg = DeclareLaunchArgument(
        "start_talker",
        default_value="false",
        description="Set to 'true' to start the talker node.",
    )

    talker = Node(
        package="demo_nodes_py",
        executable="talker",
        output="screen",
        emulate_tty=True,
        condition=IfCondition(LaunchConfiguration("start_talker")),
    )

    listener = Node(
        package="demo_nodes_py",
        executable="listener",
        output="screen",
        emulate_tty=True,
    )

    return LaunchDescription([talker_arg, talker, listener])
