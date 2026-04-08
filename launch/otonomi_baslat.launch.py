from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        
        Node(
            package='arc_rover_autonomy',
            executable='dummy_vision',
            name='goz_node'
        ),
        
        Node(
            package='arc_rover_autonomy',
            executable='beyin',
            name='beyin_node'
        )
    ])