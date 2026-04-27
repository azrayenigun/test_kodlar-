import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # Paket adın
    package_name = 'arc_rover_autonomy'
    pkg_path = get_package_share_directory(package_name)
    
    # URDF dosyasının yolu (lupus_arm.urdf olarak güncelledik)
    urdf_file = os.path.join(pkg_path, 'urdf', 'lupus_arm.urdf')
    
    # URDF içeriğini oku
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toxml()

    return LaunchDescription([
        # 1. Robot State Publisher (Orijinal dosyadaki robot_state_publisher)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),

        # 2. Joint State Publisher GUI (Orijinal dosyadaki slider ekranı)
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui'
        ),

        # 3. RViz2 (Orijinal dosyadaki görselleştirme ekranı)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            # Eğer urdf.rviz dosyan varsa buraya yolunu ekleyebiliriz
        )
    ])
