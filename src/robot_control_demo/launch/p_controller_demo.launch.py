from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Launch arguments
    goal_x_arg = DeclareLaunchArgument(
        "goal_x",
        default_value="5.0",
        description="Goal x coordinate in the odom frame (meters)",
    )
    goal_y_arg = DeclareLaunchArgument(
        "goal_y",
        default_value="3.0",
        description="Goal y coordinate in the odom frame (meters)",
    )
    k_rho_arg = DeclareLaunchArgument(
        "k_rho",
        default_value="0.4",
        description="Proportional gain on distance-to-goal (linear velocity)",
    )
    k_alpha_arg = DeclareLaunchArgument(
        "k_alpha",
        default_value="0.8",
        description="Proportional gain on heading error (angular velocity)",
    )
    goal_tolerance_arg = DeclareLaunchArgument(
        "goal_tolerance",
        default_value="0.10",
        description="Distance at which the goal is considered reached (meters)",
    )

    # Node
    p_controller_node = Node(
        package="robot_control_demo",
        executable="p_controller",
        output="screen",
        parameters=[
            {
                "goal_x": LaunchConfiguration("goal_x"),
                "goal_y": LaunchConfiguration("goal_y"),
                "k_rho": LaunchConfiguration("k_rho"),
                "k_alpha": LaunchConfiguration("k_alpha"),
                "goal_tolerance": LaunchConfiguration("goal_tolerance"),
            }
        ],
    )

    ld = LaunchDescription()
    ld.add_action(goal_x_arg)
    ld.add_action(goal_y_arg)
    ld.add_action(k_rho_arg)
    ld.add_action(k_alpha_arg)
    ld.add_action(goal_tolerance_arg)
    ld.add_action(p_controller_node)
    return ld
