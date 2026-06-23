import time
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from std_msgs.msg import String


class DemoSequence(Node):
    HEAD_JOINTS = ['HeadYaw', 'HeadPitch']
    ARM_JOINTS = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll']
    LEG_JOINTS = [
        'LHipPitch', 'RHipPitch',
        'LKneePitch', 'RKneePitch',
        'LAnklePitch', 'RAnklePitch']

    def __init__(self):
        super().__init__('demo_sequence')
        self.traj_pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.verbose_pub = self.create_publisher(String, '/demo/status', 10)
        self.get_logger().info('Demo sequence ready')

    def announce(self, text):
        self.get_logger().info(f'[DEMO] {text}')
        self.verbose_pub.publish(String(data=text))

    def send_pose(self, joint_names, positions, duration_sec=1.0):
        msg = JointTrajectory()
        msg.joint_names = joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))
        msg.points = [point]
        self.traj_pub.publish(msg)

    def wait(self, seconds):
        self.get_logger().info(f'Waiting {seconds}s...')
        time.sleep(seconds)

    def run(self):
        self.announce('Starting demo sequence')

        self.announce('Step 1/5 — Looking around')
        self.send_pose(self.HEAD_JOINTS, [0.5, 0.0], 1.0)
        self.wait(1.5)
        self.send_pose(self.HEAD_JOINTS, [-0.5, 0.2], 1.0)
        self.wait(1.5)
        self.send_pose(self.HEAD_JOINTS, [0.0, -0.3], 1.0)
        self.wait(1.5)
        self.send_pose(self.HEAD_JOINTS, [0.0, 0.0], 0.5)
        self.wait(1.0)

        self.announce('Step 2/5 — Waving')
        self.send_pose(self.ARM_JOINTS, [-0.8, -0.2, 0.0, 0.8], 1.0)
        self.wait(1.5)
        for _ in range(3):
            self.send_pose(
                self.ARM_JOINTS, [-0.8, -0.2, 0.0, 0.8], 0.3)
            self.wait(0.4)
            self.send_pose(
                self.ARM_JOINTS, [-0.8, 0.0, 0.0, 0.5], 0.3)
            self.wait(0.4)
        self.send_pose(self.ARM_JOINTS, [0.0, 0.0, 0.0, 0.0], 1.0)
        self.wait(1.5)

        self.announce('Step 3/5 — Sitting down')
        sit_pose = [0.5, 0.5, 1.2, 1.2, 0.3, 0.3]
        self.send_pose(self.LEG_JOINTS, sit_pose, 2.0)
        self.wait(2.5)

        self.announce('Step 4/5 — Standing up')
        stand_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.send_pose(self.LEG_JOINTS, stand_pose, 2.0)
        self.wait(2.5)

        self.announce('Step 5/5 — Demo complete!')
        self.announce('All steps finished successfully.')


def main(args=None):
    rclpy.init(args=args)
    node = DemoSequence()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
