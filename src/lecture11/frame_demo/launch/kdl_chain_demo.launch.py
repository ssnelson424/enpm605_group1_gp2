"""Launch the static ArUco detector together with the KDL chain demo.

Starts the static detector (which publishes
    odom -> overhead_camera -> overhead_camera_optical_frame
             -> static_aruco_box
) and a KDL node that looks up the two hops separately and composes
them locally with PyKDL to recover odom -> static_aruco_box.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    target_frame_arg = DeclareLaunchArgument(
        "target_frame",
        default_value="odom",
        description="Frame in which the composed pose is reported.",
    )
    intermediate_frame_arg = DeclareLaunchArgument(
        "intermediate_frame",
        default_value="overhead_camera_optical_frame",
        description="Frame between target and source for the manual KDL chain.",
    )
    source_frame_arg = DeclareLaunchArgument(
        "source_frame",
        default_value="static_aruco_box",
        description="Frame whose pose is composed into the target frame.",
    )
    period_arg = DeclareLaunchArgument(
        "period",
        default_value="1.0",
        description="Seconds between KDL compositions.",
    )

    static_detector_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("frame_demo"),
                "launch",
                "static_aruco_detector.launch.py",
            )
        )
    )

    kdl_node = Node(
        package="frame_demo",
        executable="kdl_chain_demo",
        output="screen",
        parameters=[
            {
                "target_frame": LaunchConfiguration("target_frame"),
                "intermediate_frame": LaunchConfiguration("intermediate_frame"),
                "source_frame": LaunchConfiguration("source_frame"),
                "period": LaunchConfiguration("period"),
            }
        ],
    )

    return LaunchDescription(
        [
            target_frame_arg,
            intermediate_frame_arg,
            source_frame_arg,
            period_arg,
            static_detector_launch,
            kdl_node,
        ]
    )
