# ENPM605 - RO01
# Group Project 2 - Group 1
# Kyle DeGuzman: 120452062
# Stephen Snelson: 12254074
# navigate_to_goal_server.py - Server node using the p_controller.py logic.

import math
import time
from typing import Any

import rclpy
from geometry_msgs.msg import Pose, TwistStamped
from group1_gp2_interfaces.action import NavigateToGoal
from nav_msgs.msg import Odometry
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node
from scipy.spatial.transform import Rotation as R


class NavigateToGoalServer(Node):
    """Server node which uses the p_controller.py logic for goals."""

    MAX_LINEAR = 0.5  # m/s
    MAX_ANGULAR = 1.0  # rad/s

    def __init__(self, node_name: str) -> None:
        """Initialize the server node. Logic from the p_controller.py node.

        Declares ROS parameters for the controller gains (k_rho, k_alpha,
        k_yaw), and tolerances (goal_tolerance, yaw_tolerance). Creates a
        publisher for cmd_vel and a subscriber for odometry/filtered. Uses a
        20 Hz control loop with feedback publishing in between 1-5 Hz.

        Args:
            node_name (str): The node name to be used from the main .py file.
        """
        # Initialize the node using the name from the main .py file.
        super().__init__(node_name)

        # Default gains and tolerances parameters set with declare_parameter.
        self.declare_parameter("k_rho", 0.4)
        self.declare_parameter("k_alpha", 0.8)
        self.declare_parameter("k_yaw", 0.8)
        self.declare_parameter("goal_tolerance", 0.10)
        self.declare_parameter("yaw_tolerance", 0.05)

        # Read the values with get_parameter. Allows the user to set the values
        # in a terminal.
        self._k_rho = self.get_parameter("k_rho").value
        self._k_alpha = self.get_parameter("k_alpha").value
        self._k_yaw = self.get_parameter("k_yaw").value
        self._tolerance = self.get_parameter("goal_tolerance").value
        self._yaw_tolerance = self.get_parameter("yaw_tolerance").value

        # Publisher for velocity, publishes to /cmd_vel and uses a default
        # QoS policy.
        self._cmd_pub = self.create_publisher(TwistStamped, "/cmd_vel", 10)

        # Subscriber for odometry, subscribes to /odometry/filtered and uses
        # the odom callback and a default QoS policy.
        self._odom_sub = self.create_subscription(
            Odometry,
            "/odometry/filtered",
            self._odom_callback,
            10,
        )

        # Action server implementation. Connect to NavigateToGoal.action
        # and use three callbacks, execute (main controller logic), goal (check
        # for valid goal points), and cancel (cancel a goal instance).
        self._action_server = ActionServer(
            self,
            NavigateToGoal,  # The .action file interface.
            "navigate_to_goal",  # The action name, shared with the client.
            execute_callback=self._execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        # Initialize the state. Yaw is for orientation. Initialize the odom
        # state to False so the odom callback can start.
        self._x = 0.0
        self._y = 0.0
        self._yaw = 0.0
        self._odom_received = False
        # Log to the terminal the gains and a message that the node has started.
        self.get_logger().info(
            f"NavigateToGoalServer started — "
            f"gains: k_rho={self._k_rho}, k_alpha={self._k_alpha}, "
            f"k_yaw={self._k_yaw}"
        )

    def goal_callback(self, goal_request: NavigateToGoal.Goal) -> GoalResponse:
        """Function for the goal callback. Rejects if the point is not
        a number.

        Args:
            goal_request (NavigateToGoal.Goal): The goal from NavigateToGoal.action.

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
        # THIS FUNCTION DOESN'T STOP THE ROBOT!!! It just accepts the
        # CancelResponse!
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
        # Change the odom state to True and log initialization.
        if not self._odom_received:
            self._odom_received = True
            self.get_logger().info("First odometry message received — state initialized.")

        # Store the x and y position from msg as attributes.
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y

        # Define the quaternion.
        q = msg.pose.pose.orientation

        # Convert the quaternion to an orientation angle.
        yaw = R.from_quat([q.x, q.y, q.z, q.w]).as_euler("xyz")[2]

        # Normalize the angle for control stability, then store as an attribute.
        self._yaw = math.atan2(math.sin(yaw), math.cos(yaw))

    def _execute_callback(self, goal_handle: ServerGoalHandle) -> Any:
        """Compute and publish a velocity command toward the goal.
        FROM p_controller.py.

        Operates in two phases:
        - Phase 1 (position)
        - Phase 2 (orientation)

        Args:
            goal_handle (ServerGoalHandle): The handle for the active goal request.

        Returns:
            NavigateToGoal.Result: The final result containing success (bool),
            total_distance (float), and elapsed_time (float). I had to change this
            to Any in the type hinting because NavigateToGoal.Result causes issues
            with MyPy.
        """
        # Extract the goal data from the request so it can be used in this
        # callback. Get its x, y, and yaw data.
        goal: NavigateToGoal.Goal = goal_handle.request
        self._goal_x = goal.goal_position.x
        self._goal_y = goal.goal_position.y
        self._goal_yaw = goal.final_heading

        # Wait for the odometry and warn if the state is still False.
        while not self._odom_received:
            self.get_logger().warn("No odometry received yet on 'odometry/filtered'.")
            time.sleep(0.1)

        # Use a frequency of 20 Hz for the while loop.
        rate = self.create_rate(20)

        # Access the internal clock object that ROS 2 manages and use it for
        # the start time. Initialize the total distance.
        start_time = self.get_clock().now()
        total_distance = 0.0

        # Initialize the last feedback time with the internal clock object.
        last_feedback_time = self.get_clock().now()

        # Keep this node running as long as ROS 2 is active.
        while rclpy.ok():
            # Cancellation check: If there is a cancel request, log a message
            # and stop the robot using a helper function.
            if goal_handle.is_cancel_requested:
                self.get_logger().info("Goal canceled")
                self._stop_robot()
                goal_handle.canceled()
                # Set the result data and return it. Since the task was canceled,
                # success is False. Set the total distance and set the time as 0.
                result = NavigateToGoal.Result()
                result.success = False
                result.total_distance = total_distance
                result.elapsed_time = 0.0
                return result

            # If there is no cancel request, find the change in x and y
            # distance and the approximate distance covered, then add to the
            # total distance.
            dx = self._goal_x - self._x
            dy = self._goal_y - self._y
            rho = math.sqrt(dx**2 + dy**2)
            total_distance += rho

            # If the approximate distance is greater than the goal tolerance,
            # continue driving to the goal (phase 1).
            if rho > self._tolerance:
                # Phase 1: drive toward the goal position.
                # Get the angle to the goal, then normalize to determine where
                # the robot needs to actually face.
                angle_to_goal = math.atan2(dy, dx)
                alpha = math.atan2(
                    math.sin(angle_to_goal - self._yaw),
                    math.cos(angle_to_goal - self._yaw),
                )
                # Implement the velocity command (both linear and angular) using the differences
                # between the gains and actual total linear distance (rho values) and
                # normalized angle (alpha values). Apply a timestamp then publish.
                cmd = TwistStamped()
                cmd.header.stamp = self.get_clock().now().to_msg()
                cmd.twist.linear.x = max(-0.5, min(0.5, self._k_rho * rho))
                cmd.twist.angular.z = max(-1.0, min(1.0, self._k_alpha * alpha))
                self._cmd_pub.publish(cmd)

            # If the approximate distance is less than the goal tolerance, then
            # simply adjust the orientation (now in phase 2).
            else:
                # Phase 2: rotate in place to reach the desired yaw.
                # Determine the difference between the goal yaw and the current
                # yaw.
                yaw_error = math.atan2(
                    math.sin(self._goal_yaw - self._yaw),
                    math.cos(self._goal_yaw - self._yaw),
                )
                # Use the difference to compare against the yaw tolerance. If it is
                # less than the tolerance, then the goal has been reached.
                if abs(yaw_error) < self._yaw_tolerance:
                    # Goal fully reached (position + orientation). Log the info
                    # to the terminal.
                    self.get_logger().info(
                        f"Goal reached: ({self._goal_x:.2f}, {self._goal_y:.2f}, final_heading={self._goal_yaw:.2f})"
                    )
                    # Stop the robot with the helper function. Mark the goal as
                    # succeeded using the goal_handle.
                    self._stop_robot()
                    goal_handle.succeed()

                    # Add a timestamp for when this task was completed.
                    end_time = self.get_clock().now()

                    # Set the result data and return it. Since the task completed,
                    # set success as True. Set the total distance and determine the
                    # total elapsed time.
                    result = NavigateToGoal.Result()
                    result.success = True
                    result.total_distance = total_distance
                    result.elapsed_time = (end_time - start_time).nanoseconds * 1e-9
                    return result

                # Otherwise, if the yaw error is still greater than the yaw tolerance,
                # continue adjusting the angle with the difference between the error yaw
                # and the gain. Use this to adjust angular velocity, then apply a timestamp
                # and publish the command.
                cmd = TwistStamped()
                cmd.header.stamp = self.get_clock().now().to_msg()
                cmd.twist.angular.z = max(-1.0, min(1.0, self._k_yaw * yaw_error))
                self._cmd_pub.publish(cmd)

                # Handle throttling for feedback publishing (no faster than 5 Hz,
                # no slower than 1 Hz).
                now = self.get_clock().now()
                # Check if more than 1 second has passed.
                if (now - last_feedback_time).nanoseconds > 1e9:
                    # Create a new feedback message object and set in it the
                    # remaining distance using rho. Send the it as a feedback
                    # update to the client using publish_feedback. Set the new
                    # last_feedback_time as now.
                    feedback = NavigateToGoal.Feedback()

                    # Fill the pose and use a quaternion.
                    feedback.current_pose = Pose()
                    feedback.current_pose.position.x = self._x
                    feedback.current_pose.position.y = self._y

                    q = R.from_euler("z", self._yaw).as_quat()
                    feedback.current_pose.orientation.x = q[0]
                    feedback.current_pose.orientation.y = q[1]
                    feedback.current_pose.orientation.z = q[2]
                    feedback.current_pose.orientation.w = q[3]

                    # Set the remaining distance.
                    feedback.distance_remaining = rho
                    goal_handle.publish_feedback(feedback)
                    last_feedback_time = now

                # Keep the while loop running at the rate of 20 Hz.
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

        # Publish the stop.
        self._cmd_pub.publish(stop)
