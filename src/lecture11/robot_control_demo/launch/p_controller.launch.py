"""Launch the ROSbot Gazebo simulation and the proportional controller.

Launch Arguments
----------------
goal_x : float
    Goal x position in metres (default: 5.0).
goal_y : float
    Goal y position in metres (default: 0.0).
goal_yaw : float
    Goal yaw in radians (default: pi/2).
k_rho : float
    Proportional gain for distance error (default: 0.4).
k_alpha : float
    Proportional gain for heading error (default: 0.8).
k_yaw : float
    Proportional gain for final yaw error (default: 0.8).
goal_tolerance : float
    Position tolerance in metres (default: 0.10).
yaw_tolerance : float
    Yaw tolerance in radians (default: 0.05).
"""

import math
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # Launch arguments
    goal_x_arg = DeclareLaunchArgument(
        "goal_x",
        default_value="5.0",
        description="Goal x position in metres.",
    )
    goal_y_arg = DeclareLaunchArgument(
        "goal_y",
        default_value="5.0",
        description="Goal y position in metres.",
    )
    goal_yaw_arg = DeclareLaunchArgument(
        "goal_yaw",
        default_value=str(math.pi / 2),
        description="Goal yaw in radians.",
    )
    k_rho_arg = DeclareLaunchArgument(
        "k_rho",
        default_value="0.4",
        description="Proportional gain for distance error.",
    )
    k_alpha_arg = DeclareLaunchArgument(
        "k_alpha",
        default_value="0.8",
        description="Proportional gain for heading error.",
    )
    k_yaw_arg = DeclareLaunchArgument(
        "k_yaw",
        default_value="0.8",
        description="Proportional gain for final yaw error.",
    )
    goal_tolerance_arg = DeclareLaunchArgument(
        "goal_tolerance",
        default_value="0.10",
        description="Position tolerance in metres.",
    )
    yaw_tolerance_arg = DeclareLaunchArgument(
        "yaw_tolerance",
        default_value="0.05",
        description="Yaw tolerance in radians.",
    )


    # Proportional controller node
    p_controller_node = Node(
        package="robot_control_demo",
        executable="p_controller",
        name="p_controller",
        parameters=[
            {
                "goal_x": LaunchConfiguration("goal_x"),
                "goal_y": LaunchConfiguration("goal_y"),
                "goal_yaw": LaunchConfiguration("goal_yaw"),
                "k_rho": LaunchConfiguration("k_rho"),
                "k_alpha": LaunchConfiguration("k_alpha"),
                "k_yaw": LaunchConfiguration("k_yaw"),
                "goal_tolerance": LaunchConfiguration("goal_tolerance"),
                "yaw_tolerance": LaunchConfiguration("yaw_tolerance"),
            }
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            goal_x_arg,
            goal_y_arg,
            goal_yaw_arg,
            k_rho_arg,
            k_alpha_arg,
            k_yaw_arg,
            goal_tolerance_arg,
            yaw_tolerance_arg,
            p_controller_node,
        ]
    )
