cmake_minimum_required(VERSION 3.14)
project(custom_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SensorReading.msg"
  "srv/ComputeTrajectory.srv"
  "action/Navigate.action"
  DEPENDENCIES std_msgs geometry_msgs action_msgs
)

ament_package()
