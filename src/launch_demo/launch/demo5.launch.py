from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node


def generate_launch_description():
    talker = Node(
        package="demo_nodes_py", executable="talker",
        output="screen", emulate_tty=True,
    )

    listener = Node(
        package="demo_nodes_py", executable="listener",
        output="screen", emulate_tty=True,
    )

    chatter_group = GroupAction([talker, listener])

    ld = LaunchDescription()
    ld.add_action(chatter_group)

    return ld
