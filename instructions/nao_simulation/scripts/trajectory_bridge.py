import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory
from gz.transport13 import Node as GzNode
from gz.msgs10.double_pb2 import Double


NAO_JOINTS = [
    'HeadYaw', 'HeadPitch',
    'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
    'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll',
    'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw',
    'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw',
]


class TrajectoryBridge(Node):
    def __init__(self):
        super().__init__('trajectory_bridge')
        self.gz_node = GzNode()
        self.gz_pubs = {}
        for joint in NAO_JOINTS:
            topic = f'/model/Nao/joint/{joint}/0/cmd_pos'
            pub = self.gz_node.advertise(topic, Double)
            self.gz_pubs[joint] = (topic, pub)
            self.get_logger().info(f'Advertised {topic}')
        self.sub = self.create_subscription(
            JointTrajectory, '/joint_trajectory', self.trajectory_cb, 10)
        self.get_logger().info('Trajectory bridge ready')

    def trajectory_cb(self, msg):
        names = msg.joint_names
        if msg.points:
            positions = msg.points[0].positions
            for name, pos in zip(names, positions):
                if name in self.gz_pubs:
                    d = Double()
                    d.data = float(pos)
                    self.gz_pubs[name][1].publish(d)
                    self.get_logger().debug(f'{name} -> {pos:.3f}')
                else:
                    self.get_logger().warn(f'Unknown joint: {name}')


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
