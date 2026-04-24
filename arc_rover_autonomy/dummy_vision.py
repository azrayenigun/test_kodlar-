#!/usr/bin/env python3
"""
LupusArm Sahte Vizyon (Dummy Vision) Node
==========================================
Görüntü işleme pipeline'ı henüz hazır olmadığı için bu node
sahte (sabit) bir nesne pozu yayınlıyor. Gerçek vision pipeline
geldiğinde bu dosya silinecek veya devre dışı bırakılacak.

KONTRAT (Büşra ile mutabık kalınan):
- Topic: /detected_object_pose
- Mesaj tipi: geometry_msgs/msg/PoseStamped
- Frame: base_link (robot tabanına göre)
- Frekans: 10 Hz
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import math


class SahteGoz(Node):
    def __init__(self):
        super().__init__('sahte_goz_node')

        self.yayinci = self.create_publisher(
            PoseStamped,
            '/detected_object_pose',
            10
        )

        self.timer = self.create_timer(0.1, self.veri_yolla)

        self.test_x = 0.5
        self.test_y = 0.0
        self.test_z = 0.7

        self.get_logger().info('LupusArm Sahte Goz baslatildi')
        self.get_logger().info(f'Topic: /detected_object_pose')
        self.get_logger().info(f'Frame: base_link')
        self.get_logger().info(f'Test pozu: X={self.test_x}, Y={self.test_y}, Z={self.test_z}')

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
        msg.header.frame_id = "base_link"

        msg.pose.position.x = self.test_x
        msg.pose.position.y = self.test_y
        msg.pose.position.z = self.test_z

        roll, pitch, yaw = 0.0, 0.0, 0.0
        qx, qy, qz, qw = self.euler_to_quaternion(roll, pitch, yaw)

        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw

        self.yayinci.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SahteGoz()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Kullanici tarafindan durduruldu')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
