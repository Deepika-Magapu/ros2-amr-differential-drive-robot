import os
import uuid
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('amr_description')
    pkg_prefix = get_package_prefix('amr_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    urdf_path = os.path.join(pkg_share, 'urdf', 'amr.urdf')
    default_world = os.path.join(pkg_share, 'worlds', 'room_world.sdf')
    default_gui_config = os.path.join(pkg_share, 'config', 'gazebo_gui.config')
    world_path = LaunchConfiguration('world')
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')

    # Add custom Gazebo GUI plugin directory
    gui_plugin_dir = os.path.join(pkg_prefix, 'lib', 'amr_description')
    existing_gui_path = os.environ.get('IGN_GUI_PLUGIN_PATH', '')
    combined_gui_path = f"{gui_plugin_dir}:{existing_gui_path}" if existing_gui_path else gui_plugin_dir

    # Isolate this Gazebo transport graph from stale servers
    gazebo_partition = f'amr_sim_{uuid.uuid4().hex}'
    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r --gui-config ', default_gui_config, ' ', world_path]}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', 'robot_description', '-name', 'amr',
            '-x', spawn_x, '-y', spawn_y, '-z', spawn_z,
        ]
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/world/nav_world/model/amr/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/gazebo_click_point@geometry_msgs/msg/Point[gz.msgs.Vector3d',
            '/world/nav_world/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/world/nav_world/model/amr/joint_state', '/joint_states'),
            ('/world/nav_world/clock', '/clock'),
        ],
        output='screen'
    )

    odom_tf = Node(
        package='amr_description',
        executable='odom_tf_broadcaster.py',
        name='odom_tf_broadcaster',
        output='screen',
    )

    gazebo_goal_manager = Node(
        package='amr_description',
        executable='gazebo_goal_manager.py',
        name='gazebo_goal_manager',
        output='screen',
    )

    room_markers = Node(
        package='amr_description',
        executable='room_markers.py',
        name='room_markers',
        output='screen',
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='IGN_PARTITION', value=gazebo_partition),
        SetEnvironmentVariable(name='IGN_GUI_PLUGIN_PATH', value=combined_gui_path),
        DeclareLaunchArgument('world', default_value=default_world),
        DeclareLaunchArgument('spawn_x', default_value='0.0'),
        DeclareLaunchArgument('spawn_y', default_value='0.0'),
        DeclareLaunchArgument('spawn_z', default_value='0.433'),
        gz_sim,
        robot_state_publisher,
        spawn_entity,
        bridge,
        odom_tf,
        gazebo_goal_manager,
        room_markers,
    ])
