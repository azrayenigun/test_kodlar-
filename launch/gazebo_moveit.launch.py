import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
import xacro


def generate_launch_description():
    # === MoveIt config (lupus_arm_config'den) ===
    # use_gazebo=true ile xacro işleyip URDF'i oluştur (Gazebo plugin dahil)
    moveit_pkg = get_package_share_directory('lupus_arm_config')
    xacro_file = os.path.join(moveit_pkg, 'config', 'LupusArm.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file, mappings={'use_gazebo': 'true'}).toxml()

    moveit_config = (
        MoveItConfigsBuilder("LupusArm", package_name="lupus_arm_config")
        .robot_description(mappings={'use_gazebo': 'true'})
        .to_moveit_configs()
    )

    # === Gazebo ===
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        )
    )

    # === Robot State Publisher ===
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # === Robotu Gazebo'ya spawn et ===
    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'LupusArm', '-z', '0.1'],
        output='screen'
    )

    # === Controller spawner'lar (Gazebo'nun controller_manager'ına) ===
    load_jsb = Node(
        package='controller_manager', executable='spawner',
        arguments=['joint_state_broadcaster'],
    )
    load_arm = Node(
        package='controller_manager', executable='spawner',
        arguments=['arm_controller'],
    )
    load_gripper = Node(
        package='controller_manager', executable='spawner',
        arguments=['gripper_controller'],
    )

    # === MoveIt move_group node ===
    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict(), {'use_sim_time': True}],
    )

    # === RViz ===
    rviz_config = os.path.join(moveit_pkg, 'config', 'moveit.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            {'use_sim_time': True},
        ],
    )

    return LaunchDescription([
        gazebo_launch,
        rsp,
        spawn,
        # Spawn bittikten sonra controller'ları sıralı yükle
        RegisterEventHandler(
            event_handler=OnProcessExit(target_action=spawn, on_exit=[load_jsb])
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(target_action=load_jsb, on_exit=[load_arm, load_gripper])
        ),
        # MoveIt + RViz birkaç saniye gecikmeli (Gazebo controller_manager hazır olsun)
        TimerAction(period=5.0, actions=[move_group, rviz]),
    ])
