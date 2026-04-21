"""Proportional controller that drives a differential-drive robot to a goal.

Uses a two-phase P-controller:

- **Phase 1 (position):** ``k_rho`` scales the distance to the goal into
  a linear velocity, while ``k_alpha`` scales the heading error into an
  angular velocity. The robot steers toward the goal until it is within
  ``goal_tolerance`` meters.
- **Phase 2 (orientation):** once the position is reached, ``k_yaw``
  scales the remaining yaw error into a pure angular velocity until the
  heading is within ``yaw_tolerance`` radians of ``goal_yaw``.

Goals can be set two ways:

1. **Via parameters** (``goal_x``, ``goal_y``, ``goal_yaw``) — the
   controller starts navigating immediately if a nonzero goal is set.
2. **Via the** ``goal_pose`` **topic** (``PoseStamped``) — a new goal
   overrides the current one and resets the controller. This allows
   external nodes to sequence multiple goals.

When a goal is fully reached (position **and** orientation), the
controller publishes ``Bool(True)`` on the ``goal_reached`` topic and
sends a zero-velocity stop command.

Subscribes to ``odometry/filtered`` for pose feedback and publishes
``TwistStamped`` commands on ``cmd_vel``.
"""

import math

from geometry_msgs.msg import PoseStamped, TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from scipy.spatial.transform import Rotation as R
from std_msgs.msg import Bool


class ProportionalController(Node):
    """Drive to a 2-D goal pose using proportional linear and angular control."""

    MAX_LINEAR = 0.5    # m/s
    MAX_ANGULAR = 1.0   # rad/s

    def __init__(self):
        """Initialize the proportional controller node.

        Declares ROS parameters for the goal position (``goal_x``,
        ``goal_y``, ``goal_yaw``), controller gains (``k_rho``,
        ``k_alpha``, ``k_yaw``), and tolerances (``goal_tolerance``,
        ``yaw_tolerance``). Creates publishers for ``cmd_vel`` and
        ``goal_reached``, subscribers for ``odometry/filtered`` and
        ``goal_pose``, and a 20 Hz timer that runs the control loop.
        """
        super().__init__("p_controller")

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

        # Goal (from parameters — overridden by goal_pose topic)
        self.declare_parameter("goal_x", 0.0)
        self.declare_parameter("goal_y", 0.0)
        self.declare_parameter("goal_yaw", 0.0)

        self._goal_x = self.get_parameter("goal_x").value
        self._goal_y = self.get_parameter("goal_y").value
        self._goal_yaw = self.get_parameter("goal_yaw").value

        # Publishers
        self._cmd_pub = self.create_publisher(TwistStamped, "cmd_vel", 10)
        self._goal_reached_pub = self.create_publisher(Bool, "goal_reached", 10)

        # Subscribers
        self._odom_sub = self.create_subscription(
            Odometry, "odometry/filtered", self._odom_callback, 10
        )
        self._goal_sub = self.create_subscription(
            PoseStamped, "goal_pose", self._goal_callback, 10
        )

        # Timer
        self._timer = self.create_timer(0.05, self._control_loop)

        # State
        self._x = 0.0
        self._y = 0.0
        self._yaw = 0.0
        self._odom_received = False
        self._goal_reached = False
        # Start navigating only if a nonzero goal was set via parameters.
        self._goal_active = (
            self._goal_x != 0.0
            or self._goal_y != 0.0
            or self._goal_yaw != 0.0
        )

        self.get_logger().info(
            f"ProportionalController started — "
            f"gains: k_rho={self._k_rho}, k_alpha={self._k_alpha}, "
            f"k_yaw={self._k_yaw}"
        )
        if self._goal_active:
            self.get_logger().info(
                f"Initial goal from parameters: "
                f"({self._goal_x:.2f}, {self._goal_y:.2f}, "
                f"yaw={self._goal_yaw:.2f})"
            )
        else:
            self.get_logger().info(
                "No initial goal — waiting for goal on 'goal_pose' topic."
            )

    def _goal_callback(self, msg: PoseStamped):
        """Accept a new goal pose from the ``goal_pose`` topic.

        Extracts the x, y position and yaw orientation from the
        ``PoseStamped`` message, resets the goal-reached flag, and
        activates the controller. This allows external nodes to
        sequence multiple goals.

        Args:
            msg: Goal pose; only x, y, and yaw (from the quaternion)
                are used. The frame_id is ignored — the goal is assumed
                to be in the odometry frame.
        """
        self._goal_x = msg.pose.position.x
        self._goal_y = msg.pose.position.y
        q = msg.pose.orientation
        self._goal_yaw = R.from_quat([q.x, q.y, q.z, q.w]).as_euler("xyz")[2]
        self._goal_reached = False
        self._goal_active = True
        self.get_logger().info(
            f"New goal received: ({self._goal_x:.2f}, {self._goal_y:.2f}, "
            f"yaw={self._goal_yaw:.2f})"
        )

    def _odom_callback(self, msg: Odometry):
        """Update the robot's pose from an odometry message.

        Extracts the x/y position and yaw angle (converted from the
        orientation quaternion via scipy) and stores them for use in
        the control loop. Logs once when the first message arrives.

        Args:
            msg: Odometry message from ``odometry/filtered``.
        """
        if not self._odom_received:
            self._odom_received = True
            self.get_logger().info(
                "First odometry message received — control loop active."
            )
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self._yaw = R.from_quat([q.x, q.y, q.z, q.w]).as_euler("xyz")[2]

    def _control_loop(self):
        """Compute and publish a velocity command toward the goal.

        Called at 20 Hz by a timer. Operates in two phases:

        - **Phase 1 (position):** while ``rho > goal_tolerance``,
          computes proportional linear and angular velocities to steer
          toward ``(goal_x, goal_y)``.
        - **Phase 2 (orientation):** once position is reached, rotates
          in place until ``|yaw_error| < yaw_tolerance``.

        When both tolerances are satisfied, publishes ``Bool(True)`` on
        ``goal_reached``, sends a zero-velocity stop command, and
        deactivates until a new goal arrives.

        Does nothing if no goal is active, the goal has already been
        reached, or no odometry has been received yet.
        """
        if not self._goal_active or self._goal_reached:
            return

        if not self._odom_received:
            self.get_logger().warn(
                "No odometry received yet on 'odometry/filtered'.",
                throttle_duration_sec=2.0,
            )
            return

        dx = self._goal_x - self._x
        dy = self._goal_y - self._y
        rho = math.sqrt(dx**2 + dy**2)

        if rho > self._tolerance:
            # Phase 1: drive toward the goal position
            angle_to_goal = math.atan2(dy, dx)
            alpha = math.atan2(
                math.sin(angle_to_goal - self._yaw),
                math.cos(angle_to_goal - self._yaw),
            )
            cmd = TwistStamped()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.twist.linear.x = max(
                -self.MAX_LINEAR, min(self.MAX_LINEAR, self._k_rho * rho)
            )
            cmd.twist.angular.z = max(
                -self.MAX_ANGULAR,
                min(self.MAX_ANGULAR, self._k_alpha * alpha),
            )
            self._cmd_pub.publish(cmd)
            self.get_logger().info(
                f"[position] pose=({self._x:.2f}, {self._y:.2f}, "
                f"yaw={self._yaw:.2f}) rho={rho:.2f} alpha={alpha:.2f} "
                f"cmd=(v={cmd.twist.linear.x:.2f}, "
                f"w={cmd.twist.angular.z:.2f})",
                throttle_duration_sec=1.0,
            )
        else:
            # Phase 2: rotate in place to reach the desired yaw
            yaw_error = math.atan2(
                math.sin(self._goal_yaw - self._yaw),
                math.cos(self._goal_yaw - self._yaw),
            )
            if abs(yaw_error) < self._yaw_tolerance:
                # Goal fully reached (position + orientation)
                self.get_logger().info(
                    f"Goal reached: ({self._goal_x:.2f}, "
                    f"{self._goal_y:.2f}, yaw={self._goal_yaw:.2f})"
                )
                self._goal_reached = True
                stop = TwistStamped()
                stop.header.stamp = self.get_clock().now().to_msg()
                self._cmd_pub.publish(stop)
                self._goal_reached_pub.publish(Bool(data=True))
                return

            cmd = TwistStamped()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.twist.angular.z = max(
                -self.MAX_ANGULAR,
                min(self.MAX_ANGULAR, self._k_yaw * yaw_error),
            )
            self._cmd_pub.publish(cmd)
            self.get_logger().info(
                f"[orientation] yaw={self._yaw:.2f} "
                f"goal_yaw={self._goal_yaw:.2f} "
                f"error={yaw_error:.2f} "
                f"cmd=(w={cmd.twist.angular.z:.2f})",
                throttle_duration_sec=1.0,
            )
