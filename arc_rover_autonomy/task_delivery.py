import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from geometry_msgs.msg import PoseStamped 
import time

class GorevYoneticisi(Node):
    def __init__(self):
        super().__init__('task_delivery_node')
        
        self.mod_pub = self.create_publisher(String, 'robot_modu', 10)
        
        
        self.subscription = self.create_subscription(
            PoseStamped, 
            '/detected_object_pose', 
            self.takip_et, 
            10)
        
        self.mevcut_durum = "BEKLEMEDE" 
        self.get_logger().info('Lupus Arm Görev Yöneticisi Başlatıldı. Durum: BEKLEMEDE')

    def takip_et(self, msg):
        obj_x = msg.pose.position.x
        obj_y = msg.pose.position.y
        obj_z = msg.pose.position.z

        # BURASI DEĞİŞTİ: Kendi kendine mod değiştirmemeli
        if self.mevcut_durum == "BEKLEMEDE" :
            if 0 < obj_z < 1.0: 
                # Sadece log basalım, mod değiştirmeyelim
                self.get_logger().info(f'Nesne Görüş Alanında (Mesafe: {obj_z:.2f}m). Onay Bekleniyor...')
                # self.durum_degistir("OTONOM")  <-- BU SATIRI SİLDİK VEYA YORUMA ALDIK
                self.mevcut_durum = "HIZALANIYOR"

        elif self.mevcut_durum == "HIZALANIYOR":
            # Hedef hata paylarını (tolerans) URDF hassasiyetine göre güncelledik
            hata_x = abs(obj_x - 0.0)
            hata_y = abs(obj_y - 0.0)

            if hata_x < 0.05 and hata_y < 0.02:
                self.get_logger().info('Hizalanma Tamam! Parça Tutuluyor...')
                self.mevcut_durum = "TUTUYOR"
                self.parca_tut()

    def durum_degistir(self, mod_adi):
        msg = String()
        msg.data = mod_adi
        self.mod_pub.publish(msg)
        self.get_logger().info(f'Robot Modu Değiştirildi: {mod_adi}')

    def parca_tut(self):
        self.get_logger().info('>>> GRIPPER (sag_joint) KAPATILIYOR...')
        
        self.durum_degistir("MANUEL") 
        self.get_logger().info('GÖREV BAŞARIYLA TAMAMLANDI.')
        self.mevcut_durum = "TAMAMLANDI"

def main(args=None):
    rclpy.init(args=args)
    node = GorevYoneticisi()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()