# enpm605.sh
# Source this file from your shell rc file:
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.bashrc   # bash users
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.zshrc    # zsh users

# ── Bash ─────────────────────────────────────────────────────────────────────
# Only define the function if the current shell is Bash
if [ -n "$BASH_VERSION" ]; then
    function enpm605() {
        # Source the ROS 2 Jazzy base installation (sets PATH, PYTHONPATH, etc.)
        source /opt/ros/jazzy/setup.bash

        # # Source the course workspace (makes your packages visible to ros2 run/launch)
        # source ~/enpm605_ws/install/setup.bash

        # # Enable Tab autocompletion for colcon commands
        # source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash

        # # Enable Tab autocompletion for ros2 CLI commands
        # eval "$(register-python-argcomplete3 ros2)"

        # # Configure the ros2 completer to not add a space after completion
        # # and to fall back to default file completion when no match is found
        # complete -o nospace -o default -F _python_argcomplete ros2

        # Navigate to the workspace root
        cd ~/enpm605_ws
    }
fi

# ── Zsh ──────────────────────────────────────────────────────────────────────
# Only define the function if the current shell is Zsh
if [ -n "$ZSH_VERSION" ]; then
    function enpm605() {
        # Source the ROS 2 Jazzy base installation (sets PATH, PYTHONPATH, etc.)
        source /opt/ros/jazzy/setup.zsh

        # # Source the course workspace (makes your packages visible to ros2 run/launch)
        # source ~/enpm605_ws/install/setup.zsh

        # # Enable Tab autocompletion for colcon commands
        # source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.zsh

        # # Enable Tab autocompletion for ros2 CLI commands
        # # Zsh handles argcomplete natively so no extra complete call is needed
        # eval "$(register-python-argcomplete3 ros2)"

        # Navigate to the workspace root
        cd ~/enpm605_ws
    }
fi