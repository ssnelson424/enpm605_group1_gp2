import math

from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R


class ProportionalController(Node):
    MAX_LINEAR = 0.5    # m/s
    MAX_ANGULAR = 1.0   # rad/s

    def __init__(self):
        super().__init__("p_controller")
        self.declare_parameter("goal_x", 5.0)
        self.declare_parameter("goal_y", 3.0)
        self.declare_parameter("k_rho", 0.4)
        self.declare_parameter("k_alpha", 0.8)
        self.declare_parameter("goal_tolerance", 0.10)

        self._goal_x = self.get_parameter("goal_x").get_parameter_value().double_value
        self._goal_y = self.get_parameter("goal_y").get_parameter_value().double_value
        self._k_rho = self.get_parameter("k_rho").get_parameter_value().double_value
        self._k_alpha = self.get_parameter("k_alpha").get_parameter_value().double_value
        self._tolerance = self.get_parameter("goal_tolerance").get_parameter_value().double_value

        self._cmd_pub = self.create_publisher(TwistStamped, "cmd_vel", 10)
        self._odom_sub = self.create_subscription(
            Odometry, "odometry/filtered", self._odom_callback, 10
        )
        self._timer = self.create_timer(0.05, self._control_loop)

        self._x = 0.0
        self._y = 0.0
        self._yaw = 0.0
        self._goal_reached = False
        self._odom_received = False

        self.get_logger().info(
            f"ProportionalController started — goal=({self._goal_x:.2f}, {self._goal_y:.2f}), "
            f"k_rho={self._k_rho}, k_alpha={self._k_alpha}, tolerance={self._tolerance}"
        )
        self.get_logger().info("Waiting for odometry on 'odometry/filtered'...")

    def _odom_callback(self, msg: Odometry):
        if not self._odom_received:
            self._odom_received = True
            self.get_logger().info("First odometry message received — starting control loop.")
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        quat = [q.x, q.y, q.z, q.w]
        self._yaw = R.from_quat(quat).as_euler("xyz")[2]

    def _control_loop(self):
        if self._goal_reached:
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

        if rho < self._tolerance:
            self.get_logger().info("Goal reached!")
            self._goal_reached = True
            stop = TwistStamped()
            stop.header.stamp = self.get_clock().now().to_msg()
            self._cmd_pub.publish(stop)  # all-zero stop
            return

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
            -self.MAX_ANGULAR, min(self.MAX_ANGULAR, self._k_alpha * alpha)
        )
        self._cmd_pub.publish(cmd)

        self.get_logger().info(
            f"pose=({self._x:.2f}, {self._y:.2f}, yaw={self._yaw:.2f}) "
            f"rho={rho:.2f} alpha={alpha:.2f} "
            f"cmd=(v={cmd.twist.linear.x:.2f}, w={cmd.twist.angular.z:.2f})",
            throttle_duration_sec=1.0,
        )
