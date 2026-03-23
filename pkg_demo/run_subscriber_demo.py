import rclpy
from first_pkg.subscriber_demo import SubscriberDemo


def main(args=None):
    rclpy.init(args=args)
    node = SubscriberDemo("subscriber_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        node.destroy_node()
        rclpy.shutdown()