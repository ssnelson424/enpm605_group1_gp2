from geometry_msgs.msg import Pose, Point, Quaternion

def main(args=None):
    # instantiate the top-level message
    pose = Pose()

    # populate the nested Point field
    pose.position = Point()
    pose.position.x = 1.0
    pose.position.y = 2.5
    pose.position.z = 0.0

    # populate the nested Quaternion field
    pose.orientation = Quaternion()
    pose.orientation.x = 0.0
    pose.orientation.y = 0.0
    pose.orientation.z = 0.0
    pose.orientation.w = 1.0  # identity rotation

    print(pose)