from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node


def generate_launch_description():
    chatter_group = GroupAction(
        [
            Node(
                package="demo_nodes_py", executable="talker",
                output="screen", emulate_tty=True,
            ),
            Node(
                package="demo_nodes_py", executable="listener",
                output="screen", emulate_tty=True,
            ),
        ]
    )

    return LaunchDescription([chatter_group])
