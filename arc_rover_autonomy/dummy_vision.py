import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import math

class SahteGoz(Node):
    def __init__(self):
        super().__init__('sahte_goz_node')
        
        self.yayinci = self.create_publisher(PoseStamped, '/detected_object_pose', 10)
        self.timer = self.create_timer(0.1, self.veri_yolla)
        
        self.get_logger().info('Lupus Arm Sahte Göz (Simulation Vision) Başlatıldı.')

    def euler_to_quaternion(self, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        q_w = cr * cp * cy + sr * sp * sy
        q_x = sr * cp * cy - cr * sp * sy
        q_y = cr * sp * cy + sr * cp * sy
        q_z = cr * cp * sy - sr * sp * cy

        return q_x, q_y, q_z, q_w

    def veri_yolla(self):
        msg = PoseStamped()
        
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_color_optical_frame"

        # Konum
        msg.pose.position.x = 0.5
        msg.pose.position.y = 0.2
        msg.pose.position.z = 0.3

        # Yönelim
        roll, pitch, yaw = 0.0, 0.0, 0.0 
        qx, qy, qz, qw = self.euler_to_quaternion(roll, pitch, yaw)

        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw
        
        self.yayinci.publish(msg)
        self.get_logger().info(f'Yayinlanan Poz (Sahte) -> X:{msg.pose.position.x} Y:{msg.pose.position.y}')

def main(args=None):
    rclpy.init(args=args)
    node = SahteGoz()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()