from setuptools import find_packages, setup

package_name = "group1_gp2"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/gp2.launch.py"]),
        ("share/" + package_name + "/config", ["config/goals.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="kdeguzma",
    maintainer_email="kdeguzma@umd.edu",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "navigate_to_goal_server = group1_gp2.scripts.main_navigate_to_goal_server:main",
            "navigate_to_goal_client = group1_gp2.scripts.main_navigate_to_goal_client:main",
        ],
    },
)
