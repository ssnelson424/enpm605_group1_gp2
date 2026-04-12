# Status constants
uint8 PENDING=0
uint8 IN_PROGRESS=1
uint8 COMPLETED=2
uint8 FAILED=3

# Fields
std_msgs/Header header
string task_id
string task_description
uint8 status
float64 completion_percentage
string message
