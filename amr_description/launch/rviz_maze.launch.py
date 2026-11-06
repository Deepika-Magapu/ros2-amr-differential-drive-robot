"""Launch RViz with the clean maze map visible and live lidar obstacles."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('amr_description')
    rviz_config = os.path.join(pkg_share, 'config', 'maze.rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
    )
    maze_markers = Node(
        package='amr_description',
        executable='maze_map_markers.py',
        name='maze_map_markers',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )
    return LaunchDescription([maze_markers, rviz])
