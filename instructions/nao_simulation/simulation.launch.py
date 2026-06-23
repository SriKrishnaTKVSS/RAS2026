import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    bridge_config = os.path.join(
        os.path.expanduser('~'), 'nao_ws', 'src', 'nao_control', 'config', 'bridge.yaml'
    )

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gz', 'sim', '-r'],
            output='screen',
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['--ros-args', '-p', f'config_file:={bridge_config}'],
            output='screen',
        ),
    ])
