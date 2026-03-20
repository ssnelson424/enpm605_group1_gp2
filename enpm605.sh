# enpm605.sh
# Source this file from your shell rc file:
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.bashrc   # bash users
#   echo "source ~/enpm605_ws/enpm605.sh" >> ~/.zshrc    # zsh users

# ── Bash ─────────────────────────────────────────────────────────────────────
if [ -n "$BASH_VERSION" ]; then
    function enpm605() {
        source /opt/ros/jazzy/setup.bash
        source ~/enpm605_ws/install/setup.bash
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
        eval "$(register-python-argcomplete3 ros2)"
        complete -o nospace -o default -F _python_argcomplete ros2
        cd ~/enpm605_ws
    }
fi

# ── Zsh ──────────────────────────────────────────────────────────────────────
if [ -n "$ZSH_VERSION" ]; then
    function enpm605() {
        source /opt/ros/jazzy/setup.zsh
        source ~/enpm605_ws/install/setup.zsh
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.zsh
        eval "$(register-python-argcomplete3 ros2)"
        cd ~/enpm605_ws
    }
fi