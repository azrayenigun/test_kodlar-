import rclpy
from rclpy.node import Node
from std_msgs.msg import String 

class Mesajci(Node): 
    def __init__(self):
        super().__init__('yayin_node')  
        self.yayinci = self.create_publisher(String, 'robot_kanali', 10)
        self.timer = self.create_timer(0.5, self.mesaj_yolla)  

    def mesaj_yolla(self):
        msg = String()
        msg.data = 'Robot kol hazir!'
        self.yayinci.publish(msg)
        self.get_logger().info('Mesaj gonderildi: ' + msg.data)

def main(args=None):
    rclpy.init(args=args)
    node = Mesajci()
    rclpy.spin(node)  