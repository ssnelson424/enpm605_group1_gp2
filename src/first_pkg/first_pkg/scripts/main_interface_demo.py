"""Entry point for the interface_demo executable.

Demonstrates how to create and populate a geometry_msgs/Pose message
with nested Point and Quaternion fields.
"""

from geometry_msgs.msg import Pose, Point, Quaternion


def main(args=None):
    """Create a Pose message, populate its fields, and print it.

    Args:
        args (list, optional): Command-line arguments (unused in this demo).
    """
    # Instantiate the top-level message
    pose = Pose()

    # Populate the nested Point field (position in 3D space)
    pose.position = Point()
    pose.position.x = 1.0
    pose.position.y = 2.5
    pose.position.z = 0.0

    # Populate the nested Quaternion field (orientation as a unit quaternion)
    pose.orientation = Quaternion()
    pose.orientation.x = 0.0
    pose.orientation.y = 0.0
    pose.orientation.z = 0.0
    pose.orientation.w = 1.0  # identity rotation (no rotation)

    print(pose)

    # print(f"Position: x={pose.position.x}, y={pose.position.y}, z={pose.position.z}")
    # print(f"Orientation: x={pose.orientation.x}, y={pose.orientation.y}, z={pose.orientation.z}, w={pose.orientation.w}")
