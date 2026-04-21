"""Launch the dynamic ArUco detector together with the marker listener.

Starts the detector (which broadcasts a TF per detected marker under
`oak_rgb_camera_optical_frame`) and a listener node that periodically
looks up each `aruco_marker_*` frame in the `odom` frame and prints
its (x, y, z) position.
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
        description="Frame in which marker poses are reported.",
    )
    marker_prefix_arg = DeclareLaunchArgument(
        "marker_prefix",
        default_value="aruco_marker_",
        description="TF frame name prefix to listen for.",
    )
    period_arg = DeclareLaunchArgument(
        "period",
        default_value="1.0",
        description="Seconds between marker lookups.",
    )

    detector_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("frame_demo"),
                "launch",
                "dynamic_detector_demo.launch.py",
            )
        )
    )

    listener_node = Node(
        package="frame_demo",
        executable="aruco_marker_listener",
        output="screen",
        parameters=[
            {
                "target_frame": LaunchConfiguration("target_frame"),
                "marker_prefix": LaunchConfiguration("marker_prefix"),
                "period": LaunchConfiguration("period"),
            }
        ],
    )

    return LaunchDescription(
        [
            target_frame_arg,
            marker_prefix_arg,
            period_arg,
            detector_launch,
            listener_node,
        ]
    )
