#!/usr/bin/env python3
"""
Lupus Arm Gripper Controller
Gripper_Joint_1 ve Gripper_Joint_2 kontrolü
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class GripperController:
    """
    Paralel gripper kontrolcüsü
    Gripper_Joint_1: -0.05 → 0.0 (sol parmak)
    Gripper_Joint_2:  0.0 → 0.05 (sağ parmak)
    """
    
    def __init__(self, node):
        self.node = node
        self.node.get_logger().info('GripperController başlatılıyor...')
        
        # Action client oluştur
        self.action_client = ActionClient(
            node,
            FollowJointTrajectory,
            '/gripper_controller/follow_joint_trajectory'
        )
        
        # Sunucuyu bekle
        self.node.get_logger().info('Gripper controller sunucusu bekleniyor...')
        self.action_client.wait_for_server(timeout_sec=5.0)
        
        # Gripper parametreleri (parametreler.yaml'den)
        self.declare_parameters()
        
        self.node.get_logger().info('Gripper Controller hazır!')
    
    def declare_parameters(self):
        """ROS parametrelerini oku"""
        # Varsayılan değerler
        self.gripper_open_pos = 0.04  # 40mm açık
        self.gripper_close_pos = 0.0  # 0mm kapalı
        
        # Parametrelerden oku (eğer varsa)
        try:
            self.gripper_open_pos = self.node.get_parameter('gripper_open_pos').value
            self.gripper_close_pos = self.node.get_parameter('gripper_close_pos').value
        except:
            self.node.get_logger().warn(' Gripper parametreleri bulunamadı, varsayılan kullanılıyor')
    
    def open_gripper(self, wait=True):
        """
        Gripper'ı aç
        
        Args:
            wait: Hareketi bekle (True) veya async (False)
        """
        self.node.get_logger().info('Gripper açılıyor...')
        return self._send_gripper_command(
            joint1_pos=-self.gripper_open_pos,  # Sol parmak sola
            joint2_pos=self.gripper_open_pos,   # Sağ parmak sağa
            duration_sec=1.0,
            wait=wait
        )
    
    def close_gripper(self, wait=True):
        """
        Gripper'ı kapat (nesneyi tut)
        """
        self.node.get_logger().info(' Gripper kapatılıyor...')
        return self._send_gripper_command(
            joint1_pos=-self.gripper_close_pos,  # Sol parmak merkeze
            joint2_pos=self.gripper_close_pos,   # Sağ parmak merkeze
            duration_sec=1.0,
            wait=wait
        )
    
    def set_gripper_position(self, width_mm, wait=True):
        """
        Gripper'ı belirli genişliğe ayarla
        
        Args:
            width_mm: Parmaklar arası mesafe (mm)
            wait: Hareketi bekle
        """
        width_m = width_mm / 1000.0  # mm'yi metre'ye çevir
        half_width = width_m / 2.0
        
        self.node.get_logger().info(f' Gripper genişliği: {width_mm}mm ayarlanıyor')
        
        return self._send_gripper_command(
            joint1_pos=-half_width,
            joint2_pos=half_width,
            duration_sec=1.0,
            wait=wait
        )
    
    def _send_gripper_command(self, joint1_pos, joint2_pos, duration_sec=1.0, wait=True):
        """
        Gripper'a trajectory gönder
        
        Args:
            joint1_pos: Gripper_Joint_1 hedef pozisyonu (metre)
            joint2_pos: Gripper_Joint_2 hedef pozisyonu (metre)
            duration_sec: Hareket süresi (saniye)
            wait: Hareketi bekle
        """
        # Goal mesajı oluştur
        goal_msg = FollowJointTrajectory.Goal()
        
        # Joint isimleri
        goal_msg.trajectory.joint_names = [
            'Gripper_Joint_1',
            'Gripper_Joint_2'
        ]
        
        # Trajectory point oluştur
        point = JointTrajectoryPoint()
        point.positions = [float(joint1_pos), float(joint2_pos)]
        point.velocities = [0.0, 0.0]
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        
        goal_msg.trajectory.points.append(point)
        goal_msg.trajectory.header.stamp = self.node.get_clock().now().to_msg()
        
        # Goal gönder
        send_goal_future = self.action_client.send_goal_async(goal_msg)
        
        if wait:
            # Sonucu bekle
            rclpy.spin_until_future_complete(self.node, send_goal_future)
            goal_handle = send_goal_future.result()
            
            if not goal_handle.accepted:
                self.node.get_logger().error(' Gripper komutu reddedildi!')
                return False
            
            # Sonucu bekle
            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self.node, result_future)
            
            result = result_future.result().result
            if result.error_code == 0:
                self.node.get_logger().info(' Gripper hareketi tamamlandı')
                return True
            else:
                self.node.get_logger().error(f' Gripper hatası: {result.error_code}')
                return False
        else:
            # Async - bekle
            return True


# Test için standalone node
class GripperTestNode(Node):
    def __init__(self):
        super().__init__('gripper_test_node')
        self.gripper = GripperController(self)
    
    def test_sequence(self):
        """Test sekansı"""
        import time
        
        self.get_logger().info(' Gripper test başlıyor...')
        
        # Test 1: Aç
        self.gripper.open_gripper()
        time.sleep(2)
        
        # Test 2: Kapat
        self.gripper.close_gripper()
        time.sleep(2)
        
        # Test 3: Özel genişlik (20mm)
        self.gripper.set_gripper_position(20)
        time.sleep(2)
        
        # Test 4: Tekrar aç
        self.gripper.open_gripper()
        
        self.get_logger().info(' Test tamamlandı!')


def main(args=None):
    rclpy.init(args=args)
    node = GripperTestNode()
    
    try:
        node.test_sequence()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
