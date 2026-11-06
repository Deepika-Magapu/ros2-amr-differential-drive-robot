"""Launch map localization and Nav2 without starting Gazebo or RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory('amr_description')
    nav2_share = get_package_share_directory('nav2_bringup')
    params_path = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    params_file = RewrittenYaml(
        source_file=params_path,
        param_rewrites={
            'set_initial_pose': 'true',
            'amcl.ros__parameters.initial_pose.x': LaunchConfiguration('initial_pose_x'),
            'amcl.ros__parameters.initial_pose.y': LaunchConfiguration('initial_pose_y'),
            'amcl.ros__parameters.initial_pose.yaw': LaunchConfiguration('initial_pose_yaw'),
        },
        convert_types=True,
    )
    map_file = LaunchConfiguration('map')

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'localization_launch.py')
        ),
        launch_arguments={
            'map': map_file,
            'params_file': params_file,
            'use_sim_time': 'True',
            'autostart': 'True',
        }.items(),
    )
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'True',
            'autostart': 'True',
            'params_file': params_file,
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value='/home/deepika/ros2_ws/maps/room_map.yaml', description='Saved occupancy map YAML file'),
        DeclareLaunchArgument('initial_pose_x', default_value='0.0'),
        DeclareLaunchArgument('initial_pose_y', default_value='0.0'),
        DeclareLaunchArgument('initial_pose_yaw', default_value='0.0'),
        localization,
        navigation,
    ])
