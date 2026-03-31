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

    talker = Node(
        package="demo_nodes_py", executable="talker",
        output="screen", emulate_tty=True,
    )

    listener = Node(
        package="demo_nodes_py", executable="listener",
        output="screen", emulate_tty=True,
    )

    chatter_group = GroupAction(
        condition=IfCondition(LaunchConfiguration("enable_chatter")),
        actions=[talker, listener],
    )

    ld = LaunchDescription()
    ld.add_action(enable_arg)
    ld.add_action(chatter_group)

    return ld
