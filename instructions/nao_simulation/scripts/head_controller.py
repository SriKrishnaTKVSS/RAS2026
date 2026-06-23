import math
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class HeadController(Node):
    HEAD_JOINTS = ['HeadYaw', 'HeadPitch']

    def __init__(self):
        super().__init__('head_controller')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.timer = self.create_timer(0.1, self.look_around)
        self.t = 0.0
        self.get_logger().info('Head controller active — looking around')

    def look_around(self):
        self.t += 0.1
        yaw = 0.8 * math.sin(self.t * 0.5)
        pitch = 0.3 * math.sin(self.t * 0.3 + 1.0)

        msg = JointTrajectory()
        msg.joint_names = self.HEAD_JOINTS
        point = JointTrajectoryPoint()
        point.positions = [yaw, pitch]
        point.time_from_start = Duration(sec=0, nanosec=100000000)
        msg.points = [point]
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = HeadController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
