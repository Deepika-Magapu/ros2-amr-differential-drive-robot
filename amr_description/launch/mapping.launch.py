"""Launch Gazebo, online SLAM and RViz for teleoperated map building."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('amr_description')
    slam_share = get_package_share_directory('slam_toolbox')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'gazebo.launch.py'))
    )
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(slam_share, 'launch', 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': 'True',
            'slam_params_file': os.path.join(pkg_share, 'config', 'slam_params.yaml'),
        }.items(),
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'config', 'omron.rviz')],
        parameters=[{'use_sim_time': True}],
    )
    return LaunchDescription([gazebo, slam, rviz])
