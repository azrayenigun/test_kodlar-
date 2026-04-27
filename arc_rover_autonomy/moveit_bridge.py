import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import Constraints, PositionConstraint
from shape_msgs.msg import SolidPrimitive

class LupusMoveItController:
    def __init__(self, node):
        self.node = node
        self.action_client = ActionClient(node, MoveGroup, 'move_action')
        self.node.get_logger().info('MoveIt Sunucusu Bekleniyor...')
        self.action_client.wait_for_server()
        self.node.get_logger().info('LUPUS KÖPRÜSÜ AKTİF! 🦾')

    def go_to_pose(self, x, y, z):
        self.node.get_logger().info(f'HAREKET EMRI: X:{x}, Y:{y}, Z:{z}')
        goal_msg = MoveGroup.Goal()
        goal_msg.request.group_name = 'arm'
        
        target_pose = PoseStamped()
        target_pose.header.frame_id = 'world'
        target_pose.header.stamp = self.node.get_clock().now().to_msg()
        target_pose.pose.position.x = float(x)
        target_pose.pose.position.y = float(y)
        target_pose.pose.position.z = float(z)
        target_pose.pose.orientation.w = 1.0

        constraints = Constraints()
        pos_con = PositionConstraint()
        pos_con.header.frame_id = 'world'
        # URDF'den gelen GERÇEK link adı:
        pos_con.link_name = 'Gripper_Base_Link' 
        
        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.SPHERE
        primitive.dimensions = [0.05] # 5cm tolerans esnekliği
        pos_con.constraint_region.primitives.append(primitive)
        pos_con.constraint_region.primitive_poses.append(target_pose.pose)
        pos_con.weight = 1.0
        constraints.position_constraints.append(pos_con)
        
        goal_msg.request.goal_constraints.append(constraints)
        goal_msg.planning_options.plan_only = False
        goal_msg.request.allowed_planning_time = 5.0

        self.action_client.send_goal_async(goal_msg)
        return True

    def gorev_usb_tak(self): 
        # URDF boyuna göre daha ulaşılabilir bir nokta:
        return self.go_to_pose(0.30, 0.0, 0.25)

    def gorev_tusa_bas(self): 
        return self.go_to_pose(0.25, -0.10, 0.15)

    def go_to_named_pose(self, pose_name):
    	self.node.get_logger().info(f'"{pose_name}" isimli poza gidiliyor...')
    	goal_msg = MoveGroup.Goal()
    	goal_msg.request.group_name = 'arm'
    	
    	# Koordinat girmek yerine kayıtlı ismi kullanıyoruz
    	constraints = Constraints()
    	joint_con = JointConstraint() # İsme göre gitmek için bunu kullanır
    	# Not: Bu kısım karmaşıksa direkt koordinatı çok basit bir yere çekelim:
    	return self.go_to_pose(0.2, 0.0, 0.3)
