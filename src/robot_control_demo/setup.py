from setuptools import find_packages, setup
import os
from glob import glob

package_name = "robot_control_demo"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # Include launch files
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Zeid Kootbally",
    maintainer_email="zeidk@umd.edu",
    description=(
        "ENPM605 demo package showcasing ROS 2 robot control concepts, "
        "including a proportional (P) controller that drives a "
        "differential-drive robot to a configurable goal pose, along with "
        "supporting publisher, service, and action examples."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "p_controller = robot_control_demo.scripts.main_p_controller_demo:main",
        ],
    },
)
