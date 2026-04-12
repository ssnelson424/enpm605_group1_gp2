"""Demo node that publishes random velocities and subscribes to odometry.

Publishes random linear and angular velocities on ``cmd_vel`` at a fixed
rate, and subscribes to ``odometry/filtered`` to log the robot's current
pose. Intended purely for demonstration purposes — the robot will wander
randomly.
"""

import random

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from scipy.spatial.transform import Rotation as R


class RandomMoverDemo(Node):
    """Publishes random cmd_vel and logs odometry."""

    MAX_LINEAR = 0.5   # m/s
    MAX_ANGULAR = 1.0  # rad/s

    def __init__(self):
        """Initialize the random mover node.

        Declares the ``publish_rate`` parameter (default 2.0 Hz), creates
        a ``TwistStamped`` publisher on ``cmd_vel``, an ``Odometry``
        subscriber on ``odometry/filtered``, and a periodic timer that
        publishes random velocity commands at the configured rate.
        """
        super().__init__("random_mover")

        self.declare_parameter("publish_rate", 2.0)  # Hz
        publish_rate = self.get_parameter("publish_rate").value

        self._cmd_pub = self.create_publisher(TwistStamped, "cmd_vel", 10)
        self._odom_sub = self.create_subscription(
            Odometry, "odometry/filtered", self._odom_callback, 10
        )
        self._timer = self.create_timer(1.0 / publish_rate, self._publish_random_cmd)

        self.get_logger().info(
            f"RandomMoverDemo started — publishing random cmd_vel at {publish_rate} Hz"
        )

    def _odom_callback(self, msg: Odometry):
        """Log the robot's current pose from an odometry message.

        Extracts x, y, and yaw from the odometry message and logs them
        at a throttled rate of once per second.

        Args:
            msg: Odometry message from ``odometry/filtered``.
        """
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        yaw = R.from_quat([q.x, q.y, q.z, q.w]).as_euler("xyz")[2]
        self.get_logger().info(
            f"Odom: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}",
            throttle_duration_sec=1.0,
        )

    def _publish_random_cmd(self):
        """Generate and publish a random velocity command.

        Samples ``linear.x`` uniformly from [-MAX_LINEAR, MAX_LINEAR] and
        ``angular.z`` from [-MAX_ANGULAR, MAX_ANGULAR], timestamps the
        ``TwistStamped`` message, and publishes it on ``cmd_vel``. Logs
        the command at a throttled rate of once per second.
        """
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.twist.linear.x = random.uniform(-self.MAX_LINEAR, self.MAX_LINEAR)
        cmd.twist.angular.z = random.uniform(-self.MAX_ANGULAR, self.MAX_ANGULAR)
        self._cmd_pub.publish(cmd)
        self.get_logger().info(
            f"cmd_vel: v={cmd.twist.linear.x:.2f}, w={cmd.twist.angular.z:.2f}",
            throttle_duration_sec=1.0,
        )
