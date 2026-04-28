import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    moveit_pkg = get_package_share_directory('lupus_arm_config')
    xacro_file = os.path.join(moveit_pkg, 'config', 'LupusArm.urdf.xacro')
    doc = xacro.process_file(xacro_file, mappings={'use_gazebo': 'true'})
    robot_desc = doc.toxml()

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        )
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'LupusArm', '-z', '0.1'],
        output='screen'
    )

    load_jsb = Node(
        package="controller_manager", executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    load_arm = Node(
        package="controller_manager", executable="spawner",
        arguments=["arm_controller"],
    )
    load_gripper = Node(
        package="controller_manager", executable="spawner",
        arguments=["gripper_controller"],
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        RegisterEventHandler(
            event_handler=OnProcessExit(target_action=spawn_entity, on_exit=[load_jsb])
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(target_action=load_jsb, on_exit=[load_arm, load_gripper])
        ),
    ])
