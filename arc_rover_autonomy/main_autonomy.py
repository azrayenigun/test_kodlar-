import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped 
from std_msgs.msg import String, Bool
from .moveit_bridge import LupusMoveItController

class AnaBeyin(Node):
    def __init__(self):
        super().__init__('ana_otonomi_node')
        self.robot_kol = LupusMoveItController(self)
        self.mevcut_mod = "MANUEL" 
        self.system_is_active = False

        self.vision_sub = self.create_subscription(PoseStamped, '/detected_object_pose', self.otonomi_dongusu, 10)
        self.mod_sub = self.create_subscription(String, 'robot_modu', self.mod_degistir, 10)
        self.status_sub = self.create_subscription(Bool, 'system_active', self.status_callback, 10)
        
        self.get_logger().info('Lupus Beyni URDF ile Uyumlu Hale Getirildi.')

    def status_callback(self, msg):
        self.system_is_active = msg.data

    def mod_degistir(self, msg):
        komut = msg.data.upper()
        if not self.system_is_active and komut not in ["MANUEL", "OTONOM"]: return

        if komut == "USB_GOREVI": self.robot_kol.gorev_usb_tak()
        elif komut == "KLAVYE_GOREVI": self.robot_kol.gorev_tusa_bas()
        elif komut == "HOME": self.robot_kol.go_to_named_pose("home")
        elif komut in ["MANUEL", "OTONOM"]:
            self.mevcut_mod = komut
            self.get_logger().info(f'MOD GÜNCELLENDİ: {self.mevcut_mod}')

    def otonomi_dongusu(self, msg):
        if not self.system_is_active or self.mevcut_mod == "MANUEL": return
        # Otonom takip için güvenli Z yüksekliği
        self.robot_kol.go_to_pose(msg.pose.position.x, msg.pose.position.y, 0.30)