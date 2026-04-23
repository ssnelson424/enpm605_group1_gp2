import math
import time
from typing import Any

import rclpy
from geometry_msgs.msg import TwistStamped
from group1_gp2_interfaces.action import NavigateToGoal
from nav_msgs.msg import Odometry
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import GoalRequest, ServerGoalHandle
from rclpy.node import Node
from scipy.spatial.transform import Rotation as R


class NavigateToGoalServer(Node):
    """Server node which uses the p_controller.py logic for goals."""

    MAX_LINEAR = 0.5  # m/s
    MAX_ANGULAR = 1.0  # rad/s

    def __init__(self, node_name: str) -> None:
        """Initialize the proportional controller node.

        Declares ROS parameters for the goal position (``goal_x``,
        ``goal_y``, ``goal_yaw``), controller gains (``k_rho``,
        ``k_alpha``, ``k_yaw``), and tolerances (``goal_tolerance``,
        ``yaw_tolerance``). Creates publishers for ``cmd_vel`` and
        ``goal_reached``, subscribers for ``odometry/filtered`` and
        ``goal_pose``, and a 20 Hz control loop.

        Args:
            node_name (str): The node name to be used from the main .py file.
        """
        super().__init__(node_name)

        # Gains and tolerances
        self.declare_parameter("k_rho", 0.4)
        self.declare_parameter("k_alpha", 0.8)
        self.declare_parameter("k_yaw", 0.8)
        self.declare_parameter("goal_tolerance", 0.10)
        self.declare_parameter("yaw_tolerance", 0.05)

        self._k_rho = self.get_parameter("k_rho").value
        self._k_alpha = self.get_parameter("k_alpha").value
        self._k_yaw = self.get_parameter("k_yaw").value
        self._tolerance = self.get_parameter("goal_tolerance").value
        self._yaw_tolerance = self.get_parameter("yaw_tolerance").value

        # Publisher (velocity).
        self._cmd_pub = self.create_publisher(TwistStamped, "/cmd_vel", 10)

        # Subscriber (odometry).
        self._odom_sub = self.create_subscription(
            Odometry,
            "/odometry/filtered",
            self._odom_callback,
            10,
        )

        # Action server implementation. Connect to
        # NavigateToGoal.action.
        self._action_server = ActionServer(
            self,
            NavigateToGoal,
            "navigate_to_goal",
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        # State
        self._x = 0.0
        self._y = 0.0
        self._yaw = 0.0
        self._odom_received = False

        self.get_logger().info(
            f"NavigateToGoalServer started — "
            f"gains: k_rho={self._k_rho}, k_alpha={self._k_alpha}, "
            f"k_yaw={self._k_yaw}"
        )

    def goal_callback(self, goal_request: GoalRequest) -> GoalResponse:
        """Function for the goal callback. Rejects if the point is not
        a number.

        Args:
            goal_request (GoalRequest): The goal from NavigateToGoal.action.

        Returns:
            GoalResponse: REJECT if the point is not a valid number, ACCEPT otherwise.
        """
        x = goal_request.goal_position.x
        y = goal_request.goal_position.y
        yaw = goal_request.final_heading

        # Check if the point is valid (invalid if NaN or Inf).
        if (
            math.isnan(x)
            or math.isnan(y)
            or math.isnan(yaw)
            or math.isinf(x)
            or math.isinf(y)
            or math.isinf(yaw)
        ):
            # Log the warning for invalid values, then send a REJECT as
            # the response.
            self.get_logger().warn("Goal rejected: Invalid values")
            return GoalResponse.REJECT
        # Log the message for the goal, then send an ACCEPT as the response.
        self.get_logger().info(f"Goal accepted: ({x:.2f}, {y:.2f}, final_heading={yaw:.2f})")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Function to accept cancellation requests.

        Args:
            goal_handle (ServerGoalHandle): The active goal instance to be canceled.

        Returns:
            CancelResponse: ACCEPT on the CancelResponse.
        """
        # THIS FUNCTION DOESN'T STOP THE ROBOT!!!
        self.get_logger().info("Cancel request received.")
        return CancelResponse.ACCEPT

    def _odom_callback(self, msg: Odometry) -> None:
        """Update the robot's pose from an odometry message.

        Extracts the x/y position and yaw angle (converted from the
        orientation quaternion via scipy) and stores them for use in
        the control loop. Logs once when the first message arrives.
        FROM p_controller.py.

        Args:
            msg: Odometry message from ``odometry/filtered``.
        """
        if not self._odom_received:
            self._odom_received = True
            self.get_logger().info("First odometry message received — state initialized.")
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        yaw = R.from_quat([q.x, q.y, q.z, q.w]).as_euler("xyz")[2]
        # Normalize the angle for control stability.
        self._yaw = math.atan2(math.sin(yaw), math.cos(yaw))

    def execute_callback(self, goal_handle: ServerGoalHandle) -> Any:
        """Compute and publish a velocity command toward the goal.
        FROM p_controller.py.

        Operates in two phases:
        - **Phase 1 (position)**
        - **Phase 2 (orientation)**

        Args:
            goal_handle (ServerGoalHandle): The handle for the active goal request.

        Returns:
            NavigateToGoal.Result: The final result containing success (bool),
            total_distance (float), and elapsed_time (float). I had to change this
            to Any in the type hinting because NavigateToGoal.Result causes issues
            with MyPy.
        """
        goal: NavigateToGoal.Goal = goal_handle.request
        self._goal_x = goal.goal_position.x
        self._goal_y = goal.goal_position.y
        self._goal_yaw = goal.final_heading

        # Wait for the odometry.
        while not self._odom_received:
            self.get_logger().warn("No odometry received yet on 'odometry/filtered'.")
            time.sleep(0.1)

        # Use a frequency of 20 Hz.
        rate = self.create_rate(20)

        start_time = self.get_clock().now()
        total_distance = 0.0

        last_feedback_time = self.get_clock().now()

        while rclpy.ok():
            # Cancellation check: stop the robot and return the result.
            if goal_handle.is_cancel_requested:
                self.get_logger().info("Goal canceled")
                self._stop_robot()
                goal_handle.canceled()

                result = NavigateToGoal.Result()
                result.success = False
                result.total_distance = total_distance
                result.elapsed_time = 0.0
                return result

            dx = self._goal_x - self._x
            dy = self._goal_y - self._y
            rho = math.sqrt(dx**2 + dy**2)
            total_distance += rho

            if rho > self._tolerance:
                # Phase 1: drive toward the goal position.
                angle_to_goal = math.atan2(dy, dx)
                alpha = math.atan2(
                    math.sin(angle_to_goal - self._yaw),
                    math.cos(angle_to_goal - self._yaw),
                )
                cmd = TwistStamped()
                cmd.header.stamp = self.get_clock().now().to_msg()
                cmd.twist.linear.x = max(-0.5, min(0.5, self._k_rho * rho))
                cmd.twist.angular.z = max(-1.0, min(1.0, self._k_alpha * alpha))
                self._cmd_pub.publish(cmd)

            else:
                # Phase 2: rotate in place to reach the desired yaw.
                yaw_error = math.atan2(
                    math.sin(self._goal_yaw - self._yaw),
                    math.cos(self._goal_yaw - self._yaw),
                )
                if abs(yaw_error) < self._yaw_tolerance:
                    # Goal fully reached (position + orientation)
                    self.get_logger().info(
                        f"Goal reached: ({self._goal_x:.2f}, {self._goal_y:.2f}, final_heading={self._goal_yaw:.2f})"
                    )
                    self._stop_robot()
                    goal_handle.succeed()

                    end_time = self.get_clock().now()

                    result = NavigateToGoal.Result()
                    result.success = True
                    result.total_distance = total_distance
                    result.elapsed_time = (end_time - start_time).nanoseconds * 1e-9
                    return result

                cmd = TwistStamped()
                cmd.header.stamp = self.get_clock().now().to_msg()
                cmd.twist.angular.z = max(-1.0, min(1.0, self._k_yaw * yaw_error))

                self._cmd_pub.publish(cmd)

                # Feedback publishing (no faster than 5 Hz, no slower than 1 Hz).
                now = self.get_clock().now()
                if (now - last_feedback_time).nanoseconds > 1e9:
                    feedback = NavigateToGoal.Feedback()
                    feedback.distance_remaining = rho
                    goal_handle.publish_feedback(feedback)
                    last_feedback_time = now

                rate.sleep()

    def _stop_robot(self) -> None:
        """Helper function for execute_callback. Stops
        the robot."""
        stop = TwistStamped()
        stop.header.stamp = self.get_clock().now().to_msg()
        stop.header.frame_id = ""

        # Set all the linear and angular velocities to 0.
        stop.twist.linear.x = 0.0
        stop.twist.linear.y = 0.0
        stop.twist.linear.z = 0.0

        stop.twist.angular.x = 0.0
        stop.twist.angular.y = 0.0
        stop.twist.angular.z = 0.0

        self._cmd_pub.publish(stop)
