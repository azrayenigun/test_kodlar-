#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import PoseStamped 
from std_msgs.msg import String, Bool
from .moveit_bridge import LupusMoveItController
from .gripper_controller import GripperController


class AnaBeyin(Node):
    def __init__(self):
        super().__init__('ana_otonomi_node')
        
        self.robot_kol = LupusMoveItController(self)
        
        self.gripper = GripperController(self)
        
        self.mevcut_mod = "MANUEL" 
        self.system_is_active = False

        self.vision_sub = self.create_subscription(
            PoseStamped, 
            '/detected_object_pose', 
            self.otonomi_dongusu, 
            10
        )
        
        self.mod_sub = self.create_subscription(
            String, 
            'robot_modu', 
            self.mod_degistir, 
            10
        )
        
        self.status_sub = self.create_subscription(
            Bool, 
            'system_active', 
            self.status_callback, 
            10
        )
        
        self.get_logger().info('Lupus Beyni Başlatıldı ')
        self.get_logger().info(f'Mod: {self.mevcut_mod} | Aktif: {self.system_is_active}')

    def status_callback(self, msg):
        
        self.system_is_active = msg.data
        self.get_logger().info(f'Sistem Durumu: {"AKTİF" if msg.data else "DURDURULDU"}')

    def mod_degistir(self, msg):
        
        komut = msg.data.upper()
        
        # task_delivery'den gelen POSE komutlarını işler
        if komut.startswith("POSE:"):
            self.pose_komutu_isle(komut)
            return
        
        # Sistem aktif değilse ve mod değişikliği değilse izin verme
        if not self.system_is_active and komut not in ["MANUEL", "OTONOM"]:
            self.get_logger().warn(f'Sistem aktif değil! "{komut}" komutu çalıştırılamadı.')
            return

        # Mod değişiklikleri
        if komut in ["MANUEL", "OTONOM"]:
            self.mevcut_mod = komut
            self.get_logger().info(f'MOD DEĞİŞTİRİLDİ: {self.mevcut_mod}')
            return
        
        # Görev komutları (sistem aktifken)
        if komut == "USB_GOREVI":
            self.get_logger().info('USB Takma görevi başlatılıyor...')
            self.robot_kol.gorev_usb_tak()
            
        elif komut == "KLAVYE_GOREVI":
            self.get_logger().info('Klavye basma görevi başlatılıyor...')
            self.robot_kol.gorev_tusa_bas()
            
        elif komut == "HOME":
            self.get_logger().info('Home pozisyonuna gidiliyor...')
            self.robot_kol.go_to_named_pose("home")
            
        elif komut == "GRIPPER_AC":
            self.get_logger().info('Gripper açılıyor...')
            self.gripper.open_gripper()
            
        elif komut == "GRIPPER_KAPAT":
            self.get_logger().info('Gripper kapatılıyor...')
            self.gripper.close_gripper()
            
        else:
            self.get_logger().warn(f'Bilinmeyen komut: {komut}')
    
    def pose_komutu_isle(self, komut):
       
        try:
            # Komutu parçala
            parts = komut.split(":")
            if len(parts) != 4:
                self.get_logger().error(f'Geçersiz POSE formatı: {komut}')
                return
            
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            
            self.get_logger().info(f'POSE komutu alındı: X={x:.3f}, Y={y:.3f}, Z={z:.3f}')
            
            # Robotkolu hareket ettir
            self.robot_kol.go_to_pose(x, y, z)
            
        except Exception as e:
            self.get_logger().error(f'POSE komutu işlenirken hata: {e}')

    def otonomi_dongusu(self, msg):
        
        # Sadece otonom modda ve sistem aktifse çalış
        if not self.system_is_active or self.mevcut_mod != "OTONOM":
            return
        
        # Nesne pozisyonu
        x = msg.pose.position.x
        y = msg.pose.position.y
        z = msg.pose.position.z
        
        self.get_logger().info(f'Nesne tespit edildi: X={x:.3f}, Y={y:.3f}, Z={z:.3f}')
        
        # Güvenli yükseklikte kalması için
        safe_z = max(0.30, z + 0.10)  # En az 30cm yükseklikte
        
        self.robot_kol.go_to_pose(x, y, safe_z)


def main(args=None):
    
    rclpy.init(args=args)
    
    node = AnaBeyin()
    
    # MultiThreaded executor oluştur
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    
    try:
        node.get_logger().info('MultiThreaded Executor başlatıldı (4 thread)')
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Kullanıcı tarafından durduruldu')
    except Exception as e:
        node.get_logger().error(f'Hata: {e}')
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
