# ENPM605 - RO01
# Group Project 2 - Group 1
# Kyle DeGuzman: 120452062
# Stephen Snelson: 12254074
# navigate_to_goal_client.py - Client node that sends goal locations.

from group1_gp2_interfaces.action import NavigateToGoal
from rclpy.action import ActionClient
from rclpy.node import Node


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
        self._active_goal = None
        self._goal_info = {}
        self._goal_results = {}

        # Set cancel_and_resend as a parameter with declare_parameter and initialize
        # it as False. Then read the value with get_parameter. Allows the user to
        # set the values in a terminal.
        self.declare_parameter("cancel_and_resend", False)
        self._cancel_and_resend = (
            self.get_parameter("cancel_and_resend").get_parameter_value().bool_value
        )

        # Import the three goals from the .yaml file using the get_goals function.
        self.get_goals()

        # Send the first goal to the server to start the robot moving.
        self._active_goal = 1
        self.send_goal(self._active_goal)

    def get_goals(self) -> None:
        """Function to import the goal information for goals 1, 2 , and 3 from the .yaml file."""
        # Loop through all three goals and look up the parameters in the .yaml file.
        # Then store them in the _goal_info dictionary.
        for i in range(1, 4):
            x = self.get_parameter(f"goal{i}.x").value
            y = self.get_parameter(f"goal{i}.y").value
            ori = self.get_parameter(f"goal{i}.final_heading").value
            self._goal_info[i] = (x, y, ori)
        # Log to the terminal the 3 goals that were loaded.
        self.get_logger().info(f"Loaded 3 goals. {self._goal_info}")

    def send_goal(self, iterator: int) -> None:
        """Function to send a navigation goal to the action server.

        Waits for the server to become available, then sends the goal
        with feedback and result callbacks.

        Args:
            iterator (int): The number of the goal to be used here.
        """
        # Set the feedback count as 0 and the canceling status as False since
        # it needs to wait for the action server.
        self._feedback_count = 0
        self._canceling = False

        # Block until the server is available and log a message to the terminal
        # before and after connecting.
        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()
        self.get_logger().info("Server Connected")

        # Unpack the goal location from the dictionary.
        x, y, heading = self._goal_info[iterator]

        # Structure the goal message to send to the server. Get the goal
        # from NavigateToGoal.action and get the x, y, and heading information.
        goal_msg = NavigateToGoal.Goal()
        goal_msg.goal_position.x = x
        goal_msg.goal_position.y = y
        goal_msg.final_heading = heading

        # Log a message of the active goal's coordinates and heading to the
        # terminal.
        self.get_logger().info(f"Sending goal {self._active_goal}/3: ({x}, {y}) heading: {heading}")

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
            self.get_logger().warn("Goal rejected.")
            return

        # Log confirmation that the server accepted the goal.
        self.get_logger().info("Goal accepted.")

        # Store the created goal handle as an attribute in this class so other
        # callbacks (e.g. feedback) can cancel the goal later if needed.
        self._goal_handle = goal_handle

        # Request the final result asynchronously and register a callback for when it arrives.
        goal_handle.get_result_async().add_done_callback(self._result_callback)

    def _feedback_callback(self, feedback_msg: NavigateToGoal.Feedback) -> None:
        """Function to handle feedback from the action server.

        Args:
            feedback_msg (NavigateToGoal.Feedback): The feedback message containing navigation
            progress.
        """
        # Unpack the feedback message data and store to a variable.
        feedback = feedback_msg.feedback
        # Log the feedback message's pose and remaining distance to the terminal.
        self.get_logger().info(
            f"Feedback: pose={feedback.current_pose}, remaining={feedback.distance_remaining}",
            throttle_duration_sec=1.0,
        )

    def _cancel_done_callback(self, future: Future) -> None:
        """Function to handle the cancel response.

        The new goal is sent from _result_callback once the canceled
        result is received, to avoid racing with the result future.

        Args:
            future (Future): The future object containing the cancel response.
        """
        # Store the result of the future object into a variable.
        cancel_response = future.result()
        # If the cancellation was successful (at least 1), log the following message
        # to the terminal.
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info("Cancel accepted by server.")

        # Otherwise, log a warning to the terminal and set the status to False.
        else:
            self.get_logger().warn("Cancel request was rejected.")
            self._canceling = False

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

        # If the robot succeeded in reaching the goal, store the result to the
        # _goal_results dictionary and log the goal, the total distance, and the
        # elapsed time to the terminal.
        if result.success:
            self._goal_results[self._active_goal] = result
            self.get_logger().info(
                f"Goal {self._active_goal}/3 succeeded:"
                f"Total distance: {result.total_distance},"
                f"Elapsed time: {result.elapsed_time}\n"
            )

            # If the number of active goals was less than 3, increase it by 1 and
            # start a trip for the next goal with .send_goal.
            if self._active_goal < 3:
                self._active_goal += 1
                self.send_goal(self._active_goal)

            # If all 3 goals have been reached, log the following message to the
            # terminal, including the total distance and elapsed time.
            if self._active_goal == 3:
                self.get_logger().info(
                    f"Goal {self._active_goal}/3 succeeded.\n"
                    f"=====================================\n"
                    f"Mission Complete. All 3 Goals Reached\n"
                    f"  Goal 1: total_distance = {self._goal_results[1].total_distance}, elapsed time={self._goal_results[1].elapsed_time}\n"
                    f"  Goal 2: total_distance = {self._goal_results[2].total_distance}, elapsed time={self._goal_results[2].elapsed_time}\n"
                    f"  Goal 3: total_distance = {self._goal_results[3].total_distance}, elapsed time={self._goal_results[3].elapsed_time}\n"
                    f"=====================================\n"
                )

        # If the robot failed to reach the goal, log the following warning and a message
        # with the total distance and elapsed time.
        else:
            self.get_logger().warn("Navigation Cancelled!")
            self.get_logger().info(
                f"Total distance: {result.total_distance}, Elapsed time: {result.elapsed_time}"
            )
