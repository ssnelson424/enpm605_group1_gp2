# enpm605.sh
# Source this file from your shell rc file:
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.bashrc   # bash users
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.zshrc    # zsh users

# ── Bash ─────────────────────────────────────────────────────────────────────
if [ -n "$BASH_VERSION" ]; then
    function enpm605() {
        # Source the ROS 2 Jazzy base installation
        source /opt/ros/jazzy/setup.bash
        # Source the course workspace
        source ~/enpm605_ws/install/setup.bash
        # Enable tab completion for colcon
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
        # Enable tab completion for ros2
        eval "$(register-python-argcomplete ros2)"
        # Navigate to the workspace root
        cd ~/enpm605_ws
    }
fi

# ── Zsh ──────────────────────────────────────────────────────────────────────
# Only define the function if the current shell is Zsh
if [ -n "$ZSH_VERSION" ]; then
    function enpm605() {
        # Source the ROS 2 Jazzy base installation
        source /opt/ros/jazzy/setup.zsh
        # Source the course workspace
        source ~/enpm605_ws/install/setup.zsh
        # Enable tab completion for colcon (zsh hook)
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.zsh
        # Navigate to the workspace root
        cd ~/enpm605_ws
    }
fi