"""
ActiveSplat ROS 2 Launch File
Launches the mapper_node and planner_node with configurable parameters.
"""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get the package share directory for resolving default config paths
    pkg_share = get_package_share_directory('activesplat')

    # ---- Declare launch arguments (equivalent to <arg> in ROS1 XML) ----
    declare_mapper = DeclareLaunchArgument('mapper', default_value='SplaTAM')
    declare_config = DeclareLaunchArgument('config', default_value=os.path.join(pkg_share, 'config', 'datasets', 'gibson.json'))
    declare_scene_id = DeclareLaunchArgument('scene_id', default_value='None')
    declare_gpu_id = DeclareLaunchArgument('gpu_id', default_value='0')
    declare_user_config = DeclareLaunchArgument('user_config', default_value=os.path.join(pkg_share, 'config', 'user_config.json'))
    declare_mode = DeclareLaunchArgument('mode', default_value='AUTO_PLANNING')
    declare_actions = DeclareLaunchArgument('actions', default_value='None')
    declare_parallelized = DeclareLaunchArgument('parallelized', default_value='0')
    declare_debug = DeclareLaunchArgument('debug', default_value='0')
    declare_hide_mapper_windows = DeclareLaunchArgument('hide_mapper_windows', default_value='0')
    declare_hide_planner_windows = DeclareLaunchArgument('hide_planner_windows', default_value='0')
    declare_step_num = DeclareLaunchArgument('step_num', default_value='-1')
    declare_remark = DeclareLaunchArgument('remark', default_value='NONE')
    declare_save_runtime_data = DeclareLaunchArgument('save_runtime_data', default_value='0')

    # ---- Mapper Node ----
    mapper_node = Node(
        package='activesplat',
        executable='mapper_node.py',
        name='mapper_node',
        output='screen',
        arguments=[
            '--mapper', LaunchConfiguration('mapper'),
            '--config', LaunchConfiguration('config'),
            '--scene_id', LaunchConfiguration('scene_id'),
            '--user_config', LaunchConfiguration('user_config'),
            '--gpu_id', LaunchConfiguration('gpu_id'),
            '--mode', LaunchConfiguration('mode'),
            '--actions', LaunchConfiguration('actions'),
            '--parallelized', LaunchConfiguration('parallelized'),
            '--hide_windows', LaunchConfiguration('hide_mapper_windows'),
            '--save_runtime_data', LaunchConfiguration('save_runtime_data'),
            '--debug', LaunchConfiguration('debug'),
            '--remark', LaunchConfiguration('remark'),
        ],
        parameters=[{'step_num': LaunchConfiguration('step_num')}],
    )

    # ---- Planner Node ----
    planner_node = Node(
        package='activesplat',
        executable='planner_node.py',
        name='planner_node',
        output='screen',
        arguments=[
            '--config', LaunchConfiguration('config'),
            '--hide_windows', LaunchConfiguration('hide_planner_windows'),
            '--save_runtime_data', LaunchConfiguration('save_runtime_data'),
            '--debug', LaunchConfiguration('debug'),
        ],
    )

    return LaunchDescription([
        # Argument declarations
        declare_mapper,
        declare_config,
        declare_scene_id,
        declare_gpu_id,
        declare_user_config,
        declare_mode,
        declare_actions,
        declare_parallelized,
        declare_debug,
        declare_hide_mapper_windows,
        declare_hide_planner_windows,
        declare_step_num,
        declare_remark,
        declare_save_runtime_data,
        # Nodes
        mapper_node,
        planner_node,
    ])
