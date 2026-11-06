"""Launch Gazebo, online mapping, Nav2 and RViz for goal-directed navigation."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('amr_description')
    nav2_share = get_package_share_directory('nav2_bringup')
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
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_share, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': 'True',
            'autostart': 'True',
            'params_file': os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
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
    return LaunchDescription([gazebo, slam, navigation, rviz])
