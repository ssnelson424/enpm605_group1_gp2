from setuptools import find_packages, setup
import os
from glob import glob

package_name = "frame_demo"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
        (os.path.join("share", package_name, "config"), glob("config/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Zeid Kootbally",
    maintainer_email="zeidk@umd.edu",
    description=(
        "ENPM605 Lecture 12 demo package on coordinate frames. Detects "
        "ArUco markers from a camera image stream and broadcasts each "
        "marker pose as a TF frame named after the marker ID."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "aruco_detector = frame_demo.scripts.main_aruco_detector_demo:main",
            "static_aruco_detector = frame_demo.scripts.main_static_aruco_detector:main",
            "aruco_marker_listener = frame_demo.scripts.main_aruco_marker_listener:main",
            "kdl_chain_demo = frame_demo.scripts.main_kdl_chain_demo:main",
        ],
    },
)
