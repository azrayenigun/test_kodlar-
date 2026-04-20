import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys, select, termios, tty

msg = """
LupusArm Klavye Kontrol Paneli
---------------------------
Tuşlar:
  1 : Manuel Mod
  2 : Otonom Mod
  u : USB Görevi
  k : Klavye Görevi
  h : Home Pozisyonu
  q : Çıkış
---------------------------
"""

class KeyboardTrigger(Node):
    def __init__(self):
        super().__init__('keyboard_trigger_node')
        self.publisher_ = self.create_publisher(String, 'robot_modu', 10)
        self.settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        # stdin'den ham veri okuyabilmek için dosya tanımlayıcısını (fd) alıyoruz
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            # Sadece bir karakter okuyoruz (beklemeden)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def run(self):
        print(msg)
        while True:
            key = self.get_key()
            if key == '1':
                self.send_mod("MANUEL")
            elif key == '2':
                self.send_mod("OTONOM")
            elif key == 'u':
                self.send_mod("USB_GOREVI")
            elif key == 'k':
                self.send_mod("KLAVYE_GOREVI")
            elif key == 'h':
                self.send_mod("HOME")
            elif key == 'q':
                break

    def send_mod(self, data):
        val = String()
        val.data = data
        self.publisher_.publish(val)
        self.get_logger().info(f'Komut Gönderildi: {data}')

def main():
    rclpy.init()
    node = KeyboardTrigger()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
