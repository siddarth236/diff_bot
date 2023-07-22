import os
import time
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit

def generate_launch_description():

    package_name='diff_bot'

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Including the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )

    # Running the spawner node from the gazebo_ros package.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')
    
    diff_drive_spawner = Node(package="controller_manager",executable="spawner",
                              arguments=["diff_cont"])
    joint_broad_spawner = Node(package="controller_manager",executable="spawner",
                               arguments=["joint_broad"])

    delayed_diff_drive_spawner = RegisterEventHandler(event_handler=OnProcessExit(
                                    target_action=spawn_entity,
                                    on_exit=[diff_drive_spawner]))
    delayed_joint_broad_spawner = RegisterEventHandler(event_handler=OnProcessExit(
                                    target_action=spawn_entity,
                                    on_exit=[joint_broad_spawner]))

    return LaunchDescription([rsp,gazebo,spawn_entity,
                              delayed_diff_drive_spawner,delayed_joint_broad_spawner])
