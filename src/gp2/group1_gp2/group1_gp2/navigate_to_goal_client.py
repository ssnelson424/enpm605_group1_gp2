# ENPM605 - RO01
# Group Project 2 - Group 1
# Kyle DeGuzman: 120452062
# Stephen Snelson: 12254074
# navigate_to_goal_client.py - Client node that sends goal locations.

from group1_gp2_interfaces.action import NavigateToGoal
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
from scipy.spatial.transform import Rotation as R


class NavigationClient(Node):
    """An action client node that sends the goal locations."""

    def __init__(self, node_name: str) -> None:
        """Initializer function for the client node.

        Args:
            node_name (str): The node name to be used from the main .py file.
        """
        # Initialize the node using the name from the main .py file.
        super().__init__(node_name)

        # Action client implementation. Connect to NavigateToGoal.action and
        # connect to the action server with the same name of "navigate_to_goal".
        self._action_client = ActionClient(
            self,
            NavigateToGoal,  # The .action file interface.
            "navigate_to_goal",  # The action name, shared with the server.
        )

        # Initialize the state. Track if there is an active goal and store the
        # info and any results.
        self._active_goal: int | None = None
        self._goal_info: dict[int, tuple[float, float, float]] = {}
        self._goal_results: dict[int, NavigateToGoal.Result] = {}

        # Declare the parameters for the goals (needed for the yaml file).
        for i in range(1, 4):
            self.declare_parameter(f"goal{i}.x", 0.0)
            self.declare_parameter(f"goal{i}.y", 0.0)
            self.declare_parameter(f"goal{i}.final_heading", 0.0)

        # Import the three goals from the .yaml file using the _load_goals function.
        self._load_goals()

        # Send the first goal to the server to start the robot moving.
        self._active_goal = 1
        self.send_goal(self._active_goal)

    def _load_goals(self) -> None:
        """Function to import the goal information for goals 1, 2 , and 3 from the .yaml file."""
        # Loop through all three goals and look up the parameters in the .yaml file.
        # Then store them in the _goal_info dictionary.
        for i in range(1, 4):
            x = self.get_parameter(f"goal{i}.x").value
            y = self.get_parameter(f"goal{i}.y").value
            yaw = self.get_parameter(f"goal{i}.final_heading").value
            self._goal_info[i] = (x, y, yaw)

        # Validation: Log an error if the three goals could not be loaded.
        # Otherwise, log to the terminal the 3 goals that were loaded.
        if any(v is None for goal in self._goal_info.values() for v in goal):
            self.get_logger().error("Could not load the goal parameters.")
        else:
            # Format the data into a list so the dict itself isn't printed.
            formatted_goals = [
                f"({x:.2f}, {y:.2f}, {yaw:.2f})" for x, y, yaw in self._goal_info.values()
            ]
            self.get_logger().info(f"Loaded 3 goals: [{', '.join(formatted_goals)}]")

    def send_goal(self, goal_id: int) -> None:
        """Function to send a navigation goal to the action server.

        Waits for the server to become available, then sends the goal
        with feedback and result callbacks.

        Args:
            goal_id (int): The number of the goal to be used here.
        """
        # Block until the server is available and log a message to the terminal
        # before and after connecting.
        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()
        # Debug line to check connection.
        # self.get_logger().info("Server Connected")

        # Unpack the goal location from the dictionary.
        x, y, heading = self._goal_info[goal_id]

        # Structure the goal message to send to the server. Get the goal
        # from NavigateToGoal.action and get the x, y, and heading information.
        goal_msg = NavigateToGoal.Goal()
        goal_msg.goal_position.x = x
        goal_msg.goal_position.y = y
        goal_msg.final_heading = heading

        # Log a message of the active goal's coordinates and heading to the
        # terminal.
        self.get_logger().info(
            f"--- Sending goal {self._active_goal}/3: ({x:.2f}, {y:.2f}) final_heading: {heading:.2f} ---"
        )

        # Send the goal asynchronously (the goal is sent but there is no waiting
        # for the robot to sotp moving).
        future = self._action_client.send_goal_async(
            goal_msg,  # The goal message.
            feedback_callback=self._feedback_callback,  # Process the server feedback.
        )

        # Process the server goal response. Once the server either accepts or rejects the
        # goal (in goal_callback in the server node), run _goal_response_callback to handle
        # the decision.
        future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future: Future) -> None:
        """Function to handle the goal response from the server.

        If the goal is accepted, requests the result asynchronously.

        Args:
            future (Future): The future object containing the goal handle.
        """
        # Create a goal handle using the result from the future object.
        goal_handle = future.result()
        # Log a message for the goal being rejected.
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected by server.")
            return

        # Log confirmation that the server accepted the goal.
        self.get_logger().info("Goal accepted by server.")

        # Store the created goal handle as an attribute in this class so other
        # callbacks (e.g. feedback) can cancel the goal later if needed.
        self._goal_handle = goal_handle

        # Request the final result asynchronously and register a callback for when it arrives.
        goal_handle.get_result_async().add_done_callback(self._result_callback)

    def _feedback_callback(self, feedback_msg) -> None:
        """Function to handle feedback from the action server.

        Args:
            feedback_msg: The feedback message containing navigation
            progress.
        """
        # Unpack the feedback message data and store to a variable.
        feedback = feedback_msg.feedback

        # Store feedback's current pose.
        pose = feedback.current_pose

        # Get the x and y coordinates.
        x = pose.position.x
        y = pose.position.y

        # Get the quaternion and convert it to yaw.
        q = pose.orientation
        yaw = R.from_quat([q.x, q.y, q.z, q.w]).as_euler("xyz")[2]

        # Log the feedback message's pose, yaw, and remaining distance to the terminal.
        self.get_logger().info(
            f"Feedback: pose=({x:.2f}, {y:.2f}, yaw={yaw:.2f}) remaining={feedback.distance_remaining:.2f}",
            throttle_duration_sec=1.0,
        )

    def _result_callback(self, future: Future) -> None:
        """Function to handle the final result from the action server.

        If the goal was canceled and cancel_and_resend is active,
        sends a new goal.

        Args:
            future (Future): The future object containing the action result.
        """
        # Store the future result and status to variables here.
        result = future.result().result
        # status = future.result().status

        # If the robot fails to reach the goal, log an error message to the terminal
        # and abort. Do NOT send the remaining goals.
        if not result.success:
            self.get_logger().error("Robot failed to reach goal. Aborting...")
            return

        # If the robot succeeded in reaching the goal, store the result to the
        # _goal_results dictionary and log the goal, the total distance, and the
        # elapsed time to the terminal.
        self._goal_results[self._active_goal] = result
        self.get_logger().info(
            f"Goal {self._active_goal}/3 succeeded. total_distance={result.total_distance:.2f}, elapsed time={result.elapsed_time:.2f}"
        )

        # If the number of active goals was less than 3, increase it by 1 and
        # start a trip for the next goal with .send_goal.
        if self._active_goal < 3:
            self._active_goal += 1
            self.send_goal(self._active_goal)

        # If all 3 goals have been reached, log the following message to the
        # terminal, including the total distance and elapsed time.
        else:
            self.get_logger().info("========================================")
            self.get_logger().info("Mission complete. All 3 goals reached.")
            # Loop to print all the goal results data.
            for i in range(1, 4):
                res = self._goal_results[i]
                self.get_logger().info(
                    f"  Goal {i}: total_distance={res.total_distance:.2f}, "
                    f"elapsed_time={res.elapsed_time:.2f}s"
                )
            self.get_logger().info("========================================")
