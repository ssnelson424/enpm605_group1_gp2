import rclpy
from first_pkg.publisher_demo import PublisherDemo

def main(args=None):
    rclpy.init(args=args)
    node = PublisherDemo("publisher_demo")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        node.destroy_node()
        rclpy.shutdown()