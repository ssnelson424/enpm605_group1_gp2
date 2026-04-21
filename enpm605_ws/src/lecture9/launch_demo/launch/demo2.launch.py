from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="demo_nodes_py",
                executable="talker",
                output="screen",
                emulate_tty=True,
            ),
            Node(
                package="demo_nodes_py",
                executable="listener",
                output="screen",
                emulate_tty=True,
            ),
        ]
    )
