import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose 

class AnaBeyin(Node):
    def __init__(self):
        super().__init__('ana_otonomi_node')

        self.declare_parameter('kp_degeri', 1.0) 
        self.kp = self.get_parameter('kp_degeri').get_parameter_value().double_value
        
        self.subscription = self.create_subscription(Pose, 'camera_data', self.karar_ver, 10)
        self.get_logger().info('Robot Beyni Calisiyor: P-Kontrolcu Aktif!')

    def karar_ver(self, msg):
        
        hedef_x = msg.position.x
        hedef_y = msg.position.y
        hedef_z = msg.position.z
        
        
        mevcut_konum_x = 0.0
        
        
        
        hata = hedef_x - mevcut_konum_x
        
       
        
        kp = 2.0
        hesaplanan_hiz = kp * hata

        
        if hata > 0.05: 
            self.get_logger().info(f'HEDEF UZAKTA! Mesafe: {hata:.2f}m | Motor Hizi: {hesaplanan_hiz:.2f}')
            self.get_logger().info('Komut: Hedefe dogru ilerle...')
        else:
            
            self.get_logger().info('HEDEFİN ÜSTÜNDEYİM! Dur ve Parçayı Tut.')

def main(args=None):
    rclpy.init(args=args)
    node = AnaBeyin()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()