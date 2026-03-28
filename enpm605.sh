# enpm605.sh
# Source this file from your shell rc file:
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.bashrc   # bash users
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.zshrc    # zsh users


# ROS 2 environment
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# export ROS_LOCALHOST_ONLY=1   # uncomment to restrict to localhost

# ROS 2 aliases
alias cb="colcon build --symlink-install"
alias cbs="colcon build --symlink-install --packages-select"
alias cbu="colcon build --symlink-install --packages-up-to"
alias ct="colcon test"
alias ctr="colcon test-result --verbose"
alias srcros="source /opt/ros/${ROS_DISTRO}/setup.zsh"
alias srcws="source install/setup.zsh"
alias rn="ros2 node list"
alias rt="ros2 topic list"
alias rte="ros2 topic echo"
alias rti="ros2 topic info"
alias rs="ros2 service list"
alias rp="ros2 param list"
alias rr="ros2 run"
alias rl="ros2 launch"
alias rbag="ros2 bag"

# Clean ROS 2 workspace build artifacts
rosclean() {
  echo "Removing build/ install/ log/ directories..."
  rm -rf build/ install/ log/
  echo "Done. Workspace cleaned."
}

# Quick colcon build a single package and source
cbb() {
  colcon build --symlink-install --packages-select "$1" && source install/setup.zsh
}

# ── Bash ─────────────────────────────────────────────────────────────────────
if [ -n "$BASH_VERSION" ]; then
    function enpm605() {
        ROS_DISTRO="jazzy"
        # Source the ROS 2 ROS_DISTRO base installation
        source /opt/ros/${ROS_DISTRO}/setup.bash
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
        ROS_DISTRO="jazzy"
        # Source the ROS 2 ROS_DISTRO base installation
        source /opt/ros/${ROS_DISTRO}/setup.zsh
        # Source the course workspace
        source ~/enpm605_ws/install/setup.zsh
        # Enable tab completion for colcon (zsh hook)
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.zsh
        # Navigate to the workspace root
        cd ~/enpm605_ws
    }
fi