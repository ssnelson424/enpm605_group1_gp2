from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    enable_arg = DeclareLaunchArgument(
        "enable_chatter",
        default_value="false",
        description="Set to 'true' to start the talker/listener group.",
    )

    chatter_group = GroupAction(
        condition=IfCondition(LaunchConfiguration("enable_chatter")),
        actions=[
            Node(
                package="demo_nodes_py", executable="talker",
                output="screen", emulate_tty=True,
            ),
            Node(
                package="demo_nodes_py", executable="listener",
                output="screen", emulate_tty=True,
            ),
        ],
    )

    return LaunchDescription([enable_arg, chatter_group])
