"""Task status demo node.

Publishes TaskStatus messages that cycle through all status constants,
demonstrating how to use message-level constants in ROS 2.
"""

from rclpy.node import Node

from custom_interfaces.msg import TaskStatus


class TaskStatusDemo(Node):
    """A publisher node that demonstrates TaskStatus message constants."""

    def __init__(self, node_name: str) -> None:
        super().__init__(node_name)
        self._publisher = self.create_publisher(TaskStatus, "task_status", 10)
        self._timer = self.create_timer(2.0, self._timer_callback)
        self._statuses = [
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
        ]
        self._status_names = {
            TaskStatus.PENDING: "PENDING",
            TaskStatus.IN_PROGRESS: "IN_PROGRESS",
            TaskStatus.COMPLETED: "COMPLETED",
            TaskStatus.FAILED: "FAILED",
        }
        self._index = 0
        self.get_logger().info("TaskStatusDemo node started.")

    def _timer_callback(self) -> None:
        """Publish a TaskStatus message cycling through each status constant."""
        msg = TaskStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.task_id = "task_001"
        msg.task_description = "Pick and place operation"
        msg.status = self._statuses[self._index]
        msg.completion_percentage = self._index / (len(self._statuses) - 1) * 100.0
        msg.message = f"Task is {self._status_names[msg.status]}"

        self._publisher.publish(msg)
        self.get_logger().info(
            f"Published: status={self._status_names[msg.status]}, "
            f"completion={msg.completion_percentage:.0f}%"
        )

        # Advance to the next status, wrapping back to 0 after the last one
        self._index = (self._index + 1) % len(self._statuses)
