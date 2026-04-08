import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Dinleyici(Node):
    def __init__(self):
        super().__init__('dinleyici_node')
         
        self.abonelik = self.create_subscription(String, 'robot_kanali', self.mesaji_yazdir, 10)

    def mesaji_yazdir(self, msg):
        
        self.get_logger().info('Robot kolundan gelen veri: ' + msg.data)

def main(args=None):
    rclpy.init(args=args)
    node = Dinleyici()
    rclpy.spin(node)