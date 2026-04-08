import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts  

class HesapMakinesi(Node):
    def __init__(self):
        super().__init__('hesap_makinesi_servisi')
         
        self.srv = self.create_service(AddTwoInts, 'sayi_topla', self.toplama_yap)

    def toplama_yap(self, request, response):
         
        response.sum = request.a + request.b
        self.get_logger().info(f'Gelen istek: a={request.a}, b={request.b}')
        self.get_logger().info(f'Gonderilen yanit: {response.sum}')
        return response

def main(args=None):
    rclpy.init(args=args)
    node = HesapMakinesi()
    rclpy.spin(node)