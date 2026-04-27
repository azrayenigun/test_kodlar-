import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Paket ve Dosya Yollarını Tanımla
    package_name = 'arc_rover_autonomy'
    pkg_path = get_package_share_directory(package_name)
    
    # Yeni URDF ismimiz: lupus_arm.urdf
    urdf_file = os.path.join(pkg_path, 'urdf', 'lupus_arm.urdf')
    
    # URDF'i işle
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toxml()

    # 2. Gazebo'nun Ana Launch Dosyasını Dahil Et (empty_world.launch yerine)
    gazebo_ros_path = get_package_share_directory('gazebo_ros')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_path, 'launch', 'gazebo.launch.py')
        )
    )

    # 3. Robot State Publisher (TF ağacını kurar)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True # Gazebo saatini kullanması için kritik
        }]
    )

    # 4. Robotu Gazebo'ya "Spawn" Eden Düğüm (spawn_model yerine)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', 
                   '-entity', 'LupusArm',
                   '-x', '0', '-y', '0', '-z', '0.1'], # Hafif yukarıda başlatmak iyidir
        output='screen'
    )

    # 5. Static Transform (Orijinal dosyadaki tf_footprint_base yerine)
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_footprint_base',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint']
    )


# --- Düğümleri Tanımlama Kısmı (return satırından önce olmalı) ---
    
    # 5. Joint State Broadcaster (Eklemlerin durumunu okur)
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # 6. Arm Controller (Eklemlere hareket emri gönderir)
    load_arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )

    # --- LaunchDescription Kısmı ---
    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        static_tf,
        load_joint_state_broadcaster, # Değişkeni buraya ekledik
        load_arm_controller           # Değişkeni buraya ekledik
    ])
