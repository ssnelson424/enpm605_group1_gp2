from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()
    talker = Node(
        package="demo_nodes_py", executable="talker",
        output="screen", emulate_tty=True,
    )
    listener = Node(
        package="demo_nodes_py", executable="listener",
        output="screen", emulate_tty=True,
    )
    ld.add_action(talker)
    ld.add_action(listener)
    return ld
