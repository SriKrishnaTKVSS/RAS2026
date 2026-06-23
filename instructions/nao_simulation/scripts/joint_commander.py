import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class JointCommander(Node):
    def __init__(self):
        super().__init__('joint_commander')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.get_logger().info('Joint commander ready')

    def send_pose(self, joint_names, positions, duration_sec=1.0):
        msg = JointTrajectory()
        msg.joint_names = joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))
        msg.points = [point]
        self.pub.publish(msg)
        names = ', '.join(joint_names)
        self.get_logger().info(
            f'Moved joints [{names}] to positions {positions}')


def main(args=None):
    rclpy.init(args=args)
    node = JointCommander()

    joint_names = [
        'LHipPitch', 'RHipPitch',
        'LKneePitch', 'RKneePitch',
        'LAnklePitch', 'RAnklePitch']

    node.get_logger().info('--- Sit down ---')
    node.send_pose(joint_names, [0.5, 0.5, 1.0, 1.0, 0.3, 0.3], 2.0)
    rclpy.spin_once(node, timeout_sec=2.5)

    node.get_logger().info('--- Stand up ---')
    node.send_pose(joint_names, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 2.0)
    rclpy.spin_once(node, timeout_sec=2.5)

    node.get_logger().info('--- Wave right arm ---')
    arm_joints = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll']
    arm_pose = [-0.5, -0.3, 0.0, 0.5]
    node.send_pose(arm_joints, arm_pose, 1.5)
    rclpy.spin_once(node, timeout_sec=2.0)

    node.send_pose(arm_joints, [0.0, 0.0, 0.0, 0.0], 1.0)
    rclpy.spin_once(node, timeout_sec=1.5)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
