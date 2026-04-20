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
        self.create_timer(0.1, self.check_keyboard)
        print("\n" + "="*30 + "\nLUPUS ARM HAZIR\n[r] Kilidi Aç\n[1] Manuel\n[h] Home\n" + "="*30)

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
        if key == 'r': self.update_state(True, "SISTEM AKTIF")
        elif key == 's': self.update_state(False, "SISTEM DURDURULDU")
        elif key == 'h' and self.is_running: self.send_mod("HOME")
        elif key == 'u' and self.is_running: self.send_mod("USB_GOREVI")
        elif key == 'k' and self.is_running: self.send_mod("KLAVYE_GOREVI")
        elif key == '1': self.send_mod("MANUEL")
        elif key == '2': self.send_mod("OTONOM")

    def send_mod(self, mod):
        msg = String()
        msg.data = mod
        self.mod_pub.publish(msg)
        self.get_logger().info(f'Emir: {mod}')

    def update_state(self, state, log):
        self.is_running = state
        msg = Bool()
        msg.data = state
        self.status_pub.publish(msg)
        print(f"\n>>> {log} <<<")

def main(args=None):
    rclpy.init(args=args)
    master = MasterControl()
    try:
        rclpy.spin(master)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        master.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()