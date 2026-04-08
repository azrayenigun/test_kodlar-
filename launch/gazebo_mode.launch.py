import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    
    pkg_share = get_package_share_directory('arc_rover_autonomy')
    config_file = os.path.join(pkg_share, 'config', 'parametreler.yaml')
    
    
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('arc_rover_autonomy'), 'launch', 'lupus_gazebo.launch.py')
        ])
    )

    
    task_delivery_node = Node(
        package='arc_rover_autonomy',
        executable='task_delivery',
        name='task_delivery_node',
        parameters=[config_file] 
    )

    return LaunchDescription([
        gazebo_launch,
        task_delivery_node
    ])