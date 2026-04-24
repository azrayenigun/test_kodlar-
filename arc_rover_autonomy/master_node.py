#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
import sys, termios, tty, select


class MasterControl(Node):
    def __init__(self):
        super().__init__('master_node')
        
        self.is_running = False
        
        
        self.status_pub = self.create_publisher(Bool, 'system_active', 10)
        self.mod_pub = self.create_publisher(String, 'robot_modu', 10)
        
        # Klavye kontrolü için timer
        self.create_timer(0.1, self.check_keyboard)
        
        
        self.print_menu()
    
    def print_menu(self):
        """Tüm komutları gösteren menü"""
        menu = """
╔════════════════════════════════════════════════════════╗
║           LUPUS ARM KONTROL SİSTEMİ                    ║
╠════════════════════════════════════════════════════════╣
║  SİSTEM KONTROL:                                       ║
║    [r] Kilidi Aç (Sistemi Aktif Et)                    ║
║    [s] Kilidi Kapat (Sistemi Durdur)                   ║
║                                                        ║
║  MOD KONTROL:                                          ║
║    [1] Manuel Mod                                      ║
║    [2] Otonom Mod                                      ║
║                                                        ║
║  ROBOTKOL HAREKETLERİ:                                 ║
║    [h] Home Pozisyonuna Git                            ║
║    [u] USB Takma Görevi Başlat                         ║
║    [k] Klavye Tuşuna Basma Görevi Başlat               ║
║                                                        ║
║  GRİPPER KONTROL:                                      ║
║    [o] Gripper Aç (Open)                               ║
║    [c] Gripper Kapat (Close)                           ║
║                                                        ║
║  DİĞER:                                                ║
║    [m] Menüyü Tekrar Göster                            ║
║    [q] Çıkış                                           ║
╚════════════════════════════════════════════════════════╝
"""
        print(menu)
    
    def get_key(self):
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            key = sys.stdin.read(1) if rlist else ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key
    
    def check_keyboard(self):
       
        key = self.get_key()
        
        if not key:
            return
        
        # Sistem kontrol
        if key == 'r':
            self.update_state(True, "SİSTEM AKTİF EDİLDİ")
        
        elif key == 's':
            self.update_state(False, "SİSTEM DURDURULDU")
        
        # Mod kontrol
        elif key == '1':
            self.send_mod("MANUEL")
            print("\n>>> MANUEL MOD AKTİF <<<")
        
        elif key == '2':
            self.send_mod("OTONOM")
            print("\n>>> OTONOM MOD AKTİF <<<")
        
        # Robotkol hareketleri (sadece sistem aktifken)
        elif key == 'h' and self.is_running:
            self.send_mod("HOME")
            print("\n>>> HOME POZİSYONUNA GİDİLİYOR <<<")
        
        elif key == 'u' and self.is_running:
            self.send_mod("USB_GOREVI")
            print("\n>>> USB TAKMA GÖREVİ BAŞLATILDI <<<")
        
        elif key == 'k' and self.is_running:
            self.send_mod("KLAVYE_GOREVI")
            print("\n>>> KLAVYE BASMA GÖREVİ BAŞLATILDI <<<")
        
        # Gripper kontrol (sistem aktifken)
        elif key == 'o' and self.is_running:
            self.send_mod("GRIPPER_AC")
            print("\n>>> GRİPPER AÇILIYOR <<<")
        
        elif key == 'c' and self.is_running:
            self.send_mod("GRIPPER_KAPAT")
            print("\n>>> GRİPPER KAPATILIYOR <<<")
        
        
        elif key == 'm':
            self.print_menu()
        
        elif key == 'q':
            print("\n>>> PROGRAM SONLANDIRILIYOR <<<")
            raise KeyboardInterrupt
        
        # Geçersiz tuş veya sistem kapalı uyarısı
        elif key in ['h', 'u', 'k', 'o', 'c'] and not self.is_running:
            print("\n  SİSTEM AKTİF DEĞİL! Önce [r] tuşuna basın.")
    
    def send_mod(self, mod):
        
        msg = String()
        msg.data = mod
        self.mod_pub.publish(msg)
        self.get_logger().info(f'Komut gönderildi: {mod}')
    
    def update_state(self, state, log):
        
        self.is_running = state
        
        msg = Bool()
        msg.data = state
        self.status_pub.publish(msg)
        
        print(f"\n{'='*50}")
        print(f">>> {log} <<<")
        print(f"{'='*50}")


def main(args=None):
    rclpy.init(args=args)
    master = MasterControl()
    
    try:
        rclpy.spin(master)
    except (KeyboardInterrupt, SystemExit):
        print("\n\n>>> Master Control Kapatıldı <<<\n")
    finally:
        master.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
