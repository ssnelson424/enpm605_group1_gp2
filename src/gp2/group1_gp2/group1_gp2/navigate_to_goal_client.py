
# ENPM605 - RO01
# Group Project 2 - Group 1 
# Stephen Snelson 12254074
# Navigate to Goal Client Main Function

"""
This module 
"""

from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node
from group1_gp2_interfaces.action import NavigateToGoal

class NavigationClient(Node):
    """An action client node that sends the goal locations."""

    def __init__(self, node_name: str) -> None:
        """Initialize the Navigate action client.

        Args:
            node_name: Name of the node
        """
        super().__init__(node_name)
        self._action_client = ActionClient(
            self,  # the current node
            NavigateToGoal,  # the action type
            "navigate_to_goal",  # the action name
        )

        self._active_goal = None
        self._goal_info = {}
        self._goal_results = {}
        
        self.declare_parameter("cancel_and_resend", False)
        self._cancel_and_resend = (
            self.get_parameter("cancel_and_resend").get_parameter_value().bool_value
        )

        #import goals from yaml file
        self.get_goals()
        
        #send the first goal to the server
        self._active_goal = 1
        self.send_goal(self._active_goal)
        
        
        
        
        
        

    def get_goals(self) -> None:
        """imports the goal information for goal 1,2,3 from the yaml files"""

        for i in range (1,4):
            x = self.get_parameter(f"goal{i}.x").value
            y = self.get_parameter(f"goal{i}.y").value
            ori = self.get_parameter(f"goal{i}.final_heading").value
            self._goal_info[i] = (x,y,ori)   
        
        self.get_logger().info(f"Loaded 3 goals. {self._goal_info}")            
            
    
    def send_goal(self, iterator:int) -> None:
        """Send a navigation goal to the action server.

        Waits for the server to become available, then sends the goal
        with feedback and result callbacks.

        Args:
            iterator: Goal #
        """
        self._feedback_count = 0
        self._canceling = False
        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()
        self.get_logger().info("Server Connected")
        
        #upack goal location from dictionary
        x,y,heading = self._goal_info[iterator]
        
        #structure goal message to send to server
        goal_msg = NavigateToGoal.Goal()
        goal_msg.goal_position.x = x
        goal_msg.goal_position.y = y
        goal_msg.final_heading = heading

        #print goal message to logger
        self.get_logger().info(
            f"Sending goal {self._active_goal}/3: ({x}, {y}) heading: {heading}"
        )
        
        # send the goal asynchronously
        future = self._action_client.send_goal_async(
            goal_msg, # the goal
            feedback_callback=self._feedback_callback # process server feedback
        )
        
        # process server goal response
        future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        """Handle the goal response from the server.

        If the goal is accepted, requests the result asynchronously.

        Args:
            future: The future containing the goal handle.
        """
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected.")
            return

        # Log confirmation that the server accepted the goal
        self.get_logger().info("Goal accepted.")

        # Store the goal handle so other callbacks (e.g. feedback) can cancel the goal
        self._goal_handle = goal_handle

        # Request the final result asynchronously and register a callback for when it arrives
        goal_handle.get_result_async().add_done_callback(self._result_callback)

    def _feedback_callback(self, feedback_msg) -> None:
        """Handle feedback from the action server.

        Args:
            feedback_msg: The feedback message containing navigation progress.
        """
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"Feedback: pose={feedback.current_pose}, remaining={feedback.distance_remaining}",
            throttle_duration_sec = 1.0
        )

    def _cancel_done_callback(self, future) -> None:
        """Handle the cancel response.

        The new goal is sent from _result_callback once the canceled
        result is received, to avoid racing with the result future.

        Args:
            future: The future containing the cancel response.
        """
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info("Cancel accepted by server.")
        else:
            self.get_logger().warn("Cancel request was rejected.")
            self._canceling = False

    def _result_callback(self, future) -> None:
        """Handle the final result from the action server.

        If the goal was canceled and cancel_and_resend is active,
        sends a new goal.

        Args:
            future: The future containing the action result.
        """
        result = future.result().result
        status = future.result().status

        if result.success:
            self._goal_results[self._active_goal] = result
            self.get_logger().info(
                f"Goal {self._active_goal}/3 succeeded:" 
                f"Total distance: {result.total_distance},"
                f"Elapsed time: {result.elapsed_time}\n"
            )
            if self._active_goal < 3:                
                self._active_goal += 1
                self.send_goal(self._active_goal)       

            if self._active_goal ==3:
                self.get_logger().info(
                    f"Goal {self._active_goal}/3 succeeded.\n"
                    f"=====================================\n"
                    f"Mission Complete. All 3 Goals Reached\n"
                    f"  Goal 1: total_distance = {self._goal_results[1].total_distance}, elapsed time={self._goal_results[1].elapsed_time}\n"
                    f"  Goal 2: total_distance = {self._goal_results[2].total_distance}, elapsed time={self._goal_results[2].elapsed_time}\n"
                    f"  Goal 3: total_distance = {self._goal_results[3].total_distance}, elapsed time={self._goal_results[3].elapsed_time}\n"
                    f"=====================================\n"
                )            
            
        else:
            self.get_logger().warn(f"Navigation Cancelled!")
            self.get_logger().info(f"Total distance: {result.total_distance}, Elapsed time: {result.elapsed_time}")
