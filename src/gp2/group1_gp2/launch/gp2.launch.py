# ENPM605 - RO01
# Group Project 2 - Group 1
# Kyle DeGuzman: 120452062
# Stephen Snelson: 12254074
# gp2.launch.py - Launch file for all nodes.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> None:
    """Main function to launch the client and server nodes."""
    # Resolve the path to config/goals.yaml.
    pkg_share = get_package_share_directory("group1_gp2")
    goals_file = os.path.join(pkg_share, "config", "goals.yaml")

    # Define the goal tolerance argument and yaw tolerance argument.
    goal_tolerance_arg = DeclareLaunchArgument(
        "goal_tolerance",
        default_value="0.10",
        description="Position tolerance in meters",
    )

    yaw_tolerance_arg = DeclareLaunchArgument(
        "yaw_tolerance",
        default_value="0.05",
        description="Yaw tolerance in radians",
    )

    goal_tolerance = LaunchConfiguration("goal_tolerance")
    yaw_tolerance = LaunchConfiguration("yaw_tolerance")

    # Define the action server node.
    server_node = Node(
        package="group1_gp2",
        executable="navigate_to_goal_server",
        name="navigate_to_goal_server",
        output="screen",
        emulate_tty=True,
        parameters=[
            {
                "goal_tolerance": goal_tolerance,
                "yaw_tolerance": yaw_tolerance,
            }
        ],
    )

    # Define the action client node.
    client_node = Node(
        package="group1_gp2",
        executable="navigate_to_goal_client",
        name="navigate_to_goal_client",
        output="screen",
        emulate_tty=True,
        parameters=[goals_file],
    )

    # Return the launch description with the goal tolerance argument, yaw
    # tolerance argument, server node, and client node.
    return LaunchDescription(
        [
            goal_tolerance_arg,
            yaw_tolerance_arg,
            server_node,
            client_node,
        ]
    )
