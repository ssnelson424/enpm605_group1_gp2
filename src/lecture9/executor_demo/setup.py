from setuptools import find_packages, setup

package_name = 'executor_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Zeid Kootbally',
    maintainer_email='zeidk@umd.edu',
    description='Demo package for ROS 2 executors and callback groups.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'single_threaded_demo = executor_demo.scripts.main_single_threaded_demo:main',
            'mutex_demo = executor_demo.scripts.main_mutex_demo:main',
            'reentrant_demo = executor_demo.scripts.main_reentrant_demo:main',
            'slow_cb_demo = executor_demo.scripts.main_slow_cb_demo:main',
        ],
    },
)
