import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
import time
import math

class TasimaGorevi(Node):
    def __init__(self):
        super().__init__('task_delivery_node')
        
        self.declare_parameter('is_simulation', True) 
        self.is_sim = self.get_parameter('is_simulation').get_parameter_value().bool_value  

        if self.is_sim:
            self.get_logger().info('>>> MOD: GAZEBO SIMULASYON') 
            self.arm_topic = '/arm_controller/joint_trajectory' 
            self.gripper_topic = '/gripper_controller/joint_trajectory' 
        else:
            self.get_logger().info('>>> MOD: REEL ROBOT (CANLI)') 
            self.arm_topic = '/real_arm_controller/joint_trajectory' 
            self.gripper_topic = '/real_arm_gripper_controller/joint_trajectory' 

        
        self.gripper_pub = self.create_publisher(JointTrajectory, self.gripper_topic, 10) 
        self.arm_pub = self.create_publisher(JointTrajectory, self.arm_topic, 10) 
        self.subscription = self.create_subscription(Pose, 'camera_data', self.operasyon_baslat, 10) 
        
        self.is_holding = False
        self.get_logger().info('Lupus Arm: Hibrit Kontrol Sistemi Aktif.')


    def ters_kinematik_hesapla(self, x, y, z):  
        L1, L2, L3 = 0.2, 0.55, 0.45  
        joint1 = math.atan2(y, x) 
        r = math.sqrt(x**2 + y**2)
        s = z - L1
        D = (r**2 + s**2 - L2**2 - L3**2) / (2 * L2 * L3) 
        D = max(-1.0, min(1.0, D))
        joint3 = math.atan2(math.sqrt(1 - D**2), D)
        joint2 = math.atan2(s, r) - math.atan2(L3 * math.sin(joint3), L2 + L3 * math.cos(joint3)) 
        return [joint1, joint2, joint3, 0.0, 0.0, 0.0] 

    def operasyon_baslat(self, msg):
        if not self.is_holding:
            hedef_x = msg.position.x - 0.1
            hedef_y = msg.position.y 
            hedef_z = msg.position.z 

            self.gripper_kontrol(0.04) 
            time.sleep(1.5)

            acilar = self.ters_kinematik_hesapla(hedef_x, hedef_y, hedef_z) 
            self.kol_hareket_ettir(acilar) 
            time.sleep(4.0)
            
            self.gripper_kontrol(0.0) 
            self.is_holding = True
            time.sleep(2.0)
            
            self.kol_hareket_ettir([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])


    def gripper_kontrol(self, aciklik):
        msg = JointTrajectory()
        msg.joint_names = ['left_finger_joint']
        point = JointTrajectoryPoint()
        point.positions = [aciklik]
        point.time_from_start.sec = 1
        msg.points.append(point)
        self.gripper_pub.publish(msg)

    def kol_hareket_ettir(self, pozisyonlar):
        msg = JointTrajectory()
        msg.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']
        point = JointTrajectoryPoint()
        point.positions = pozisyonlar
        point.time_from_start.sec = 2
        msg.points.append(point)
        self.arm_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TasimaGorevi()
    rclpy.spin(node)
    rclpy.shutdown()


