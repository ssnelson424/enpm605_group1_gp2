
Kyle DeGuzman: 

Initialized the package setup/skeleton layout on GitHub so it followed the required file layout to make all the files work. Modified package metadata and added yaml and Action Interface. Implemented and debugged the Action Server node and its main file before merging everything with the Client Node on Github. Added detailed comments, docstrings, and type hinting. Implemented launch file and debugged server and client nodes.

Stephen Snelson:
Implemented Action Client node and main file. Performed Cancellation Demo and uploaded cancel_demo.png. Various debugging and organization to meet specificaiton requirements.

Cancel_demo Notes:
We were able to get the server client to perform as expected during the cancel demo (proper output to screen), however we were unable to get the CLI terminal to print "goal cancelled / results ...". It did print "cancelling goal..." as seen in the Cancel_Demo_Output.png. It also printed "executor is already spinning." We attribute this to a limitation in the ROS2 CLI tools. When ctrl+C is pressed, the CLI sends a cancel request, but it terminates its executor prematurely, leading to the "executor is already spinning" message instead of properly waiting for and displaying the cancel confirmation and results. Despite this, the server correctly processes the cancellation, stops the robot, calls the goal_handle.canceled() and returns the results, as confirmed by the server logs.