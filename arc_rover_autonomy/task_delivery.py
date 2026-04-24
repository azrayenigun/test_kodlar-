#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped 
import time
import threading


class GorevYoneticisi(Node):
    
    
    def __init__(self):
        super().__init__('task_delivery_node')
        
        self.mod_pub = self.create_publisher(String, 'robot_modu', 10)
        self.status_pub = self.create_publisher(Bool, 'task_status', 10)
        
        self.vision_sub = self.create_subscription(
            PoseStamped, 
            '/detected_object_pose', 
            self.nesne_tespit_callback, 
            10
        )
        
        # State machine durumları
        self.mevcut_durum = "BEKLEMEDE"
        self.durum_listesi = [
            "BEKLEMEDE",      # Nesne bekleniyor
            "HIZALANIYOR",    # Nesneye doğru hareket ediliyor
            "YAKLASILIYOR",   # Nesnenin üstüne geliniyor
            "TUTULUYOR",      # Gripper kapatılıyor
            "KALDIRILIYOR",   # Nesne kaldırılıyor
            "TASINIYOR",      # Hedef konuma gidiliyor
            "BIRAKILIYOR",    # Gripper açılıyor
            "TAMAMLANDI"      # Görev bitti
        ]
        
        # Nesne ve hedef bilgileri
        self.nesne_x = 0.0
        self.nesne_y = 0.0
        self.nesne_z = 0.0
        
        # Hedef konum
        self.hedef_x = 0.35
        self.hedef_y = 0.20
        self.hedef_z = 0.15
        
        # Tolerans değerleri
        self.hata_tolerans_xy = 0.02  # 2cm
        self.hata_tolerans_z = 0.05   # 5cm
        
        # Güvenlik parametreleri
        self.min_nesne_z = 0.05   # Minimum nesne yüksekliği
        self.max_nesne_z = 1.0    # Maximum görüş mesafesi
        self.safe_height = 0.30   # Güvenli hareket yüksekliği
        
        self.get_logger().info('Görev Yöneticisi Başlatıldı')
        self.get_logger().info(f'Hedef Konum: X={self.hedef_x}, Y={self.hedef_y}, Z={self.hedef_z}')
        self.get_logger().info(f'Durum: {self.mevcut_durum}')
    
    def nesne_tespit_callback(self, msg):
        
        self.nesne_x = msg.pose.position.x
        self.nesne_y = msg.pose.position.y
        self.nesne_z = msg.pose.position.z
        
        # State machine'i çalıştır
        self.state_machine_update()
    
    def state_machine_update(self):
        
        if self.mevcut_durum == "BEKLEMEDE":
            self.durum_beklemede()
            
        elif self.mevcut_durum == "HIZALANIYOR":
            self.durum_hizalaniyor()
            
        elif self.mevcut_durum == "YAKLASILIYOR":
            self.durum_yaklasiliyor()
            
        elif self.mevcut_durum == "TUTULUYOR":
            self.durum_tutuluyor()
            
        elif self.mevcut_durum == "KALDIRILIYOR":
            self.durum_kaldiriliyor()
            
        elif self.mevcut_durum == "TASINIYOR":
            self.durum_tasiniyor()
            
        elif self.mevcut_durum == "BIRAKILIYOR":
            self.durum_birakiliyor()
    
    # ==================== STATE MACHINE FONKSIYONLARI ====================
    
    def durum_beklemede(self):
        """
        BEKLEMEDE: Nesnenin görüş alanında olup olmadığını kontrol et
        """
        # Nesne geçerli mesafede mi?
        if self.min_nesne_z < self.nesne_z < self.max_nesne_z:
            self.get_logger().info(f'Nesne tespit edildi! Mesafe: {self.nesne_z:.2f}m')
            self.durum_degistir("HIZALANIYOR")
    
    def durum_hizalaniyor(self):
        """
        HIZALANIYOR: Nesneye XY düzleminde hizalan
        """
        hata_x = abs(self.nesne_x - 0.0)  # Robotun merkezine hizala
        hata_y = abs(self.nesne_y - 0.0)
        
        self.get_logger().info(f'Hizalanma - Hata X:{hata_x:.3f}, Y:{hata_y:.3f}')
        
        if hata_x < self.hata_tolerans_xy and hata_y < self.hata_tolerans_xy:
            self.get_logger().info('Hizalanma tamam!')
            self.durum_degistir("YAKLASILIYOR")
        else:
            # Hizalanma komutu gönder
            self.get_logger().info('Hizalanma devam ediyor...')
    
    def durum_yaklasiliyor(self):
        """
        YAKLASILIYOR: Nesnenin tam üstüne konumlan
        """
        self.get_logger().info('Nesneye yaklaşılıyor...')
        
        # Nesnenin tam üstüne git (safe height'ta)
        self.robot_kol_komutu(
            komut_tipi="POSE",
            x=self.nesne_x,
            y=self.nesne_y,
            z=self.safe_height
        )
        
        # 2 saniye bekle (hareket tamamlansın)
        time.sleep(2)
        
        self.durum_degistir("TUTULUYOR")
    
    def durum_tutuluyor(self):
        """
        TUTULUYOR: Aşağı in, gripper'ı kapat, nesneyi tut
        """
        self.get_logger().info('Nesne tutuluyor...')
        
        # Adım 1: Gripper'ı aç
        self.gripper_komutu("AC")
        time.sleep(1)
        
        # Adım 2: Yavaşça aşağı in
        self.robot_kol_komutu(
            komut_tipi="POSE",
            x=self.nesne_x,
            y=self.nesne_y,
            z=self.nesne_z + 0.02  # Nesnenin 2cm üstü
        )
        time.sleep(2)
        
        # Adım 3: Gripper'ı kapat
        self.gripper_komutu("KAPAT")
        time.sleep(1)
        
        self.get_logger().info('Nesne tutuldu!')
        self.durum_degistir("KALDIRILIYOR")
    
    def durum_kaldiriliyor(self):
        """
        KALDIRILIYOR: Nesneyi kaldır
        """
        self.get_logger().info('Nesne kaldırılıyor...')
        
        # Güvenli yüksekliğe çık
        self.robot_kol_komutu(
            komut_tipi="POSE",
            x=self.nesne_x,
            y=self.nesne_y,
            z=self.safe_height
        )
        time.sleep(2)
        
        self.durum_degistir("TASINIYOR")
    
    def durum_tasiniyor(self):
        """
        TASINIYOR: Nesneyi hedef konuma taşı
        """
        self.get_logger().info(f'Hedef konuma taşınıyor: ({self.hedef_x}, {self.hedef_y}, {self.hedef_z})')
        
        # Hedef konumun üstüne git (safe height'ta)
        self.robot_kol_komutu(
            komut_tipi="POSE",
            x=self.hedef_x,
            y=self.hedef_y,
            z=self.safe_height
        )
        time.sleep(3)
        
        self.durum_degistir("BIRAKILIYOR")
    
    def durum_birakiliyor(self):
        """
        BIRAKILIYOR: Nesneyi bırak
        """
        self.get_logger().info('Nesne bırakılıyor...')
        
        # Hedef yüksekliğe in
        self.robot_kol_komutu(
            komut_tipi="POSE",
            x=self.hedef_x,
            y=self.hedef_y,
            z=self.hedef_z + 0.05  # Hedefin 5cm üstü
        )
        time.sleep(2)
        
        # Gripper'ı aç
        self.gripper_komutu("AC")
        time.sleep(1)
        
        # Geri çekil
        self.robot_kol_komutu(
            komut_tipi="POSE",
            x=self.hedef_x,
            y=self.hedef_y,
            z=self.safe_height
        )
        time.sleep(2)
        
        self.get_logger().info('GÖREV BAŞARIYLA TAMAMLANDI!')
        self.durum_degistir("TAMAMLANDI")
        
        # Başarı bildirimi
        self.gorev_basarili_bildir()
    
    # ==================== YARDIMCI FONKSIYONLAR ====================
    
    def durum_degistir(self, yeni_durum):
        
        if yeni_durum in self.durum_listesi:
            self.mevcut_durum = yeni_durum
            self.get_logger().info(f'DURUM DEĞİŞTİ: {yeni_durum}')
            
            status_msg = Bool()
            status_msg.data = (yeni_durum == "TAMAMLANDI")
            self.status_pub.publish(status_msg)
        else:
            self.get_logger().error(f'Geçersiz durum: {yeni_durum}')
    
    def robot_kol_komutu(self, komut_tipi, x=0.0, y=0.0, z=0.0):
        
        self.get_logger().info(f'Robot Kol Komutu: {komut_tipi} -> X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f}')
        
        # Özel komut formatı
        if komut_tipi == "POSE":
            # Format: "POSE:X:Y:Z"
            komut = f"POSE:{x:.3f}:{y:.3f}:{z:.3f}"
        elif komut_tipi == "HOME":
            komut = "HOME"
        else:
            komut = komut_tipi
        
        msg = String()
        msg.data = komut
        self.mod_pub.publish(msg)
        
        self.get_logger().info(f'Komut gönderildi: {komut}')
    
    def gripper_komutu(self, komut):
        
        msg = String()
        msg.data = f"GRIPPER_{komut}"
        self.mod_pub.publish(msg)
        self.get_logger().info(f'Gripper Komutu: {komut}')
    
    def gorev_basarili_bildir(self):
        
        msg = String()
        msg.data = "MANUEL"  # Görevi bitir, manuel moda geç
        self.mod_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = GorevYoneticisi()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\n Görev yöneticisi durduruldu')
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
