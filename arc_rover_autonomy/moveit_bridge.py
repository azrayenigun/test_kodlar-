#!/usr/bin/env python3
"""
LupusArm MoveIt2 Bridge - Doğrudan Action Client Yaklaşımı
pymoveit2 kullanmadan MoveGroup action'ını direkt çağırır
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint, PositionConstraint, OrientationConstraint
from moveit_msgs.msg import BoundingVolume, MotionPlanRequest
from shape_msgs.msg import SolidPrimitive
from sensor_msgs.msg import JointState
import time
from .gripper_controller import GripperController


class LupusMoveItController:
    """
    MoveGroup action client ile robotkolu kontrol eden sınıf
    """
    
    def __init__(self, node):
        self.node = node
        self.node.get_logger().info('LupusMoveItController başlatılıyor...')
        
        # MoveGroup action client
        self._action_client = ActionClient(
            self.node,
            MoveGroup,
            '/move_action'
        )
        
        # Gripper kontrolcüsü
        self.gripper = GripperController(self.node)
        
        # Joint isimleri
        self.joint_names = [
            "Joint_1",
            "Joint_2", 
            "Joint_3",
            "Joint_4",
            "Joint_5",
            "Joint_6"
        ]
        
        # Planning group
        self.group_name = "arm"
        
        # End effector
        self.end_effector_link = "Gripper_Base_Link"
        
        # Action server'ı bekle
        self.node.get_logger().info('MoveGroup action server bekleniyor...')
        self._action_client.wait_for_server(timeout_sec=10.0)
        
        self.node.get_logger().info('LUPUS KÖPRÜSÜ AKTİF!')
    
    def go_to_joint_positions(self, joint_positions):
        """
        Joint uzayında hedef açılara git
        
        Args:
            joint_positions: [J1, J2, J3, J4, J5, J6] radyan cinsinden
        """
        self.node.get_logger().info(f'Joint hedefi: {[f"{j:.2f}" for j in joint_positions]}')
        
        # Goal mesajı oluştur
        goal_msg = MoveGroup.Goal()
        
        # Planning group
        goal_msg.request.group_name = self.group_name
        
        # Joint constraints ekle
        joint_constraints = Constraints()
        
        for i, (name, position) in enumerate(zip(self.joint_names, joint_positions)):
            constraint = JointConstraint()
            constraint.joint_name = name
            constraint.position = float(position)
            constraint.tolerance_above = 0.01
            constraint.tolerance_below = 0.01
            constraint.weight = 1.0
            joint_constraints.joint_constraints.append(constraint)
        
        goal_msg.request.goal_constraints.append(joint_constraints)
        
        # Planning ayarları
        goal_msg.request.num_planning_attempts = 10
        goal_msg.request.allowed_planning_time = 5.0
        goal_msg.request.max_velocity_scaling_factor = 0.2
        goal_msg.request.max_acceleration_scaling_factor = 0.2
        
        # Workspace
        goal_msg.request.workspace_parameters.header.frame_id = "base_link"
        goal_msg.request.workspace_parameters.min_corner.x = -1.0
        goal_msg.request.workspace_parameters.min_corner.y = -1.0
        goal_msg.request.workspace_parameters.min_corner.z = -1.0
        goal_msg.request.workspace_parameters.max_corner.x = 1.0
        goal_msg.request.workspace_parameters.max_corner.y = 1.0
        goal_msg.request.workspace_parameters.max_corner.z = 1.0
        
        # Plan ve execute
        goal_msg.planning_options.plan_only = False
        
        # Goal gönder (NON-BLOCKING)
        self.node.get_logger().info('MoveGroup goal gönderiliyor...')
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        
        # BLOCKING WAIT - doğrudan result() çağrısı
        try:
            goal_handle = send_goal_future.result(timeout=10.0)
        except Exception as e:
            self.node.get_logger().error(f'Goal gönderilirken hata: {e}')
            return False
        
        if not goal_handle.accepted:
            self.node.get_logger().error('Goal reddedildi!')
            return False
        
        self.node.get_logger().info('Goal kabul edildi, hareket başlıyor...')
        
        # Sonucu bekle (BLOCKING)
        result_future = goal_handle.get_result_async()
        
        try:
            result = result_future.result(timeout=30.0).result
        except Exception as e:
            self.node.get_logger().error(f'Sonuç alınırken hata: {e}')
            return False
        
        if result.error_code.val == 1:  # SUCCESS
            self.node.get_logger().info('Hareket tamamlandı!')
            return True
        else:
            self.node.get_logger().error(f'Hareket başarısız! Error code: {result.error_code.val}')
            return False
    
    def go_to_pose(self, x, y, z, orientation_w=1.0):
        """
        Cartesian uzayda hedef pozisyona git (IK kullanır)
        
        Args:
            x, y, z: Hedef pozisyon (metre)
            orientation_w: Quaternion (varsayılan: düz aşağı)
        """
        self.node.get_logger().info(f'Hedef Pose: X={x:.3f}, Y={y:.3f}, Z={z:.3f}')
        
        # Goal mesajı oluştur
        goal_msg = MoveGroup.Goal()
        
        # Planning group
        goal_msg.request.group_name = self.group_name
        
        # Position constraint
        pose_constraint = Constraints()
        
        # Position
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = "base_link"
        pos_constraint.link_name = self.end_effector_link
        
        # Bounding volume (küçük box)
        bounding_volume = BoundingVolume()
        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.01, 0.01, 0.01]  # 1cm tolerance
        bounding_volume.primitives.append(primitive)
        
        # Hedef pose
        target_pose = PoseStamped()
        target_pose.header.frame_id = "base_link"
        target_pose.pose.position.x = float(x)
        target_pose.pose.position.y = float(y)
        target_pose.pose.position.z = float(z)
        target_pose.pose.orientation.w = float(orientation_w)
        
        bounding_volume.primitive_poses.append(target_pose.pose)
        pos_constraint.constraint_region = bounding_volume
        pos_constraint.weight = 1.0
        
        pose_constraint.position_constraints.append(pos_constraint)
        
        # Orientation constraint
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = "base_link"
        ori_constraint.link_name = self.end_effector_link
        ori_constraint.orientation = target_pose.pose.orientation
        ori_constraint.absolute_x_axis_tolerance = 0.1
        ori_constraint.absolute_y_axis_tolerance = 0.1
        ori_constraint.absolute_z_axis_tolerance = 0.1
        ori_constraint.weight = 1.0
        
        pose_constraint.orientation_constraints.append(ori_constraint)
        
        goal_msg.request.goal_constraints.append(pose_constraint)
        
        # Planning ayarları
        goal_msg.request.num_planning_attempts = 10
        goal_msg.request.allowed_planning_time = 5.0
        goal_msg.request.max_velocity_scaling_factor = 0.2
        goal_msg.request.max_acceleration_scaling_factor = 0.2
        
        # Workspace
        goal_msg.request.workspace_parameters.header.frame_id = "base_link"
        goal_msg.request.workspace_parameters.min_corner.x = -1.0
        goal_msg.request.workspace_parameters.min_corner.y = -1.0
        goal_msg.request.workspace_parameters.min_corner.z = -1.0
        goal_msg.request.workspace_parameters.max_corner.x = 1.0
        goal_msg.request.workspace_parameters.max_corner.y = 1.0
        goal_msg.request.workspace_parameters.max_corner.z = 1.0
        
        # Plan ve execute
        goal_msg.planning_options.plan_only = False
        
        # Goal gönder (NON-BLOCKING)
        self.node.get_logger().info('MoveGroup goal gönderiliyor (Pose)...')
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        
        # BLOCKING WAIT
        try:
            goal_handle = send_goal_future.result(timeout=10.0)
        except Exception as e:
            self.node.get_logger().error(f'Goal gönderilirken hata: {e}')
            return False
        
        if not goal_handle.accepted:
            self.node.get_logger().error('Goal reddedildi!')
            return False
        
        self.node.get_logger().info('Goal kabul edildi, planning başlıyor...')
        
        # Sonucu bekle (BLOCKING)
        result_future = goal_handle.get_result_async()
        
        try:
            result = result_future.result(timeout=30.0).result
        except Exception as e:
            self.node.get_logger().error(f'Sonuç alınırken hata: {e}')
            return False
        
        if result.error_code.val == 1:  # SUCCESS
            self.node.get_logger().info('Hareket tamamlandı!')
            return True
        else:
            self.node.get_logger().error(f'Hareket başarısız! Error code: {result.error_code.val}')
            return False
    
    def go_to_named_pose(self, pose_name):
        """
        SRDF'de tanımlı pozisyona git (örn: "home")
        
        Args:
            pose_name: SRDF'deki grup durumu adı
        """
        self.node.get_logger().info(f'"{pose_name}" pozisyonuna gidiliyor...')
        
        # SRDF'de tanımlı "home" pozisyonu
        if pose_name.lower() == "home":
            home_joints = [1.3185, 0.0954, -0.1475, 0.0, -0.46, -0.1041]
            return self.go_to_joint_positions(home_joints)
        else:
            self.node.get_logger().warn(f'Bilinmeyen pose: {pose_name}')
            return False
    
    # ==================== GÖREV FONKSİYONLARI ====================
    
    def gorev_usb_tak(self):
        """
        USB Takma Görevi
        """
        self.node.get_logger().info('USB Takma görevi başlatıldı')
        
        # USB portuna yaklaş
        self.go_to_pose(0.30, 0.0, 0.25)
        time.sleep(1)
        
        # Hassas hizalanma
        self.go_to_pose(0.35, 0.0, 0.20)
        time.sleep(1)
        
        # İtme hareketi
        self.go_to_pose(0.38, 0.0, 0.20)
        
        self.node.get_logger().info('USB Takıldı!')
        return True
    
    def gorev_tusa_bas(self):
        """
        Klavye Tuşuna Basma Görevi
        """
        self.node.get_logger().info('Tuş basma görevi başlatıldı')
        
        # Klavye üstüne konumlan
        self.go_to_pose(0.25, -0.10, 0.15)
        time.sleep(1)
        
        # Tuşa bas
        self.go_to_pose(0.25, -0.10, 0.10)
        time.sleep(1)
        
        # Geri çekil
        self.go_to_pose(0.25, -0.10, 0.15)
        
        self.node.get_logger().info('Tuş basıldı!')
        return True
    
    def gorev_nesne_tut(self, nesne_x, nesne_y, nesne_z):
        """
        Nesneyi tutma hareketi (pick)
        """
        self.node.get_logger().info(f'Nesne tutuluyor: ({nesne_x}, {nesne_y}, {nesne_z})')
        
        # Gripper'ı aç
        self.gripper.open_gripper()
        
        # Nesnenin üstüne git
        self.go_to_pose(nesne_x, nesne_y, nesne_z + 0.10)
        time.sleep(1)
        
        # Yavaşça in
        self.go_to_pose(nesne_x, nesne_y, nesne_z)
        
        # Gripper'ı kapat
        self.gripper.close_gripper()
        
        # Nesneyi kaldır
        self.go_to_pose(nesne_x, nesne_y, nesne_z + 0.10)
        
        self.node.get_logger().info('Nesne tutuldu!')
        return True
    
    def gorev_nesne_birak(self, hedef_x, hedef_y, hedef_z):
        """
        Nesneyi bırakma hareketi (place)
        """
        self.node.get_logger().info(f'Nesne bırakılıyor: ({hedef_x}, {hedef_y}, {hedef_z})')
        
        # Hedef konumun üstüne git
        self.go_to_pose(hedef_x, hedef_y, hedef_z + 0.10)
        time.sleep(1)
        
        # Yavaşça in
        self.go_to_pose(hedef_x, hedef_y, hedef_z)
        
        # Gripper'ı aç
        self.gripper.open_gripper()
        
        # Geri çekil
        self.go_to_pose(hedef_x, hedef_y, hedef_z + 0.10)
        
        self.node.get_logger().info('Nesne bırakıldı!')
        return True


def main(args=None):
    """Test için"""
    rclpy.init(args=args)
    
    node = Node('lupus_moveit_test')
    controller = LupusMoveItController(node)
    
    try:
        # Test: Home pozisyonuna git
        controller.go_to_named_pose("home")
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
