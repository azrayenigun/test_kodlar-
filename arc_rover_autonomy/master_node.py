import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import sys, select, termios, tty


from arc_rover_autonomy.dummy_vision import SahteGoz
from arc_rover_autonomy.main_autonomy import AnaBeyin
from arc_rover_autonomy.task_delivery import TasimaGorevi

class MasterControl(Node):
    def __init__(self, executor, node_list):
        super().__init__('master_node')
        self.executor = executor
        self.node_list = node_list
        self.is_running = True
        self.settings = termios.tcgetattr(sys.stdin)
        
        
        self.timer = self.create_timer(0.1, self.check_keyboard)
        self.get_logger().info('\n' + '='*40 + '\nMASTER NODE: [s] DURDUR | [r] BASLAT | [q] CIK\n' + '='*40)

    def check_keyboard(self):
        key = self.get_key()
        if key == 's':
            self.stop_system()
        elif key == 'r':
            self.start_system()
        elif key == 'q':
            self.get_logger().error('CIKIS YAPILIYOR...')
            rclpy.shutdown()
            sys.exit(0)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def stop_system(self):
        if self.is_running:
            self.get_logger().warn('!!! SISTEM DONDURULDU (PAUSED) !!!')
            for node in self.node_list:
                try:
                    self.executor.remove_node(node)
                except:
                    pass
            self.is_running = False

    def start_system(self):
        if not self.is_running:
            self.get_logger().info('>>> SISTEM DEVAM EDIYOR (RESUMED) <<<')
            for node in self.node_list:
                try:
                    self.executor.add_node(node)
                except:
                    pass
            self.is_running = True

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor(num_threads=8)

    goz = SahteGoz()
    beyin = AnaBeyin()
    tasima = TasimaGorevi()
    node_list = [goz, beyin, tasima]

    master = MasterControl(executor, node_list)
    executor.add_node(master)
    
    
    for n in node_list:
        executor.add_node(n)

    try:
        executor.spin()
    except  (KeyboardInterrupt, SystemExit):
        pass
    finally:
        if rclpy.ok():    
            executor.shutdown()
            rclpy.shutdown()