import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose  

class SahteGoz(Node):
    def __init__(self):
        super().__init__('sahte_goz_node')
         
        self.yayinci = self.create_publisher(Pose, 'camera_data', 10)
        self.timer = self.create_timer(0.1, self.veri_yolla)  

    def veri_yolla(self):
        msg = Pose()
         
        msg.position.x = 0.5
        msg.position.y = 0.0
        msg.position.z = 0.3
        
        self.yayinci.publish(msg)
        self.get_logger().info('Sahte hedef koordinatlari: X:0.5, Y:0.0, Z:0.3')

def main(args=None):
    rclpy.init(args=args)
    node = SahteGoz()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()