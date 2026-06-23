import math
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class WalkController(Node):
    LEG_JOINTS = [
        'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch',
        'LAnklePitch', 'LAnkleRoll',
        'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch',
        'RAnklePitch', 'RAnkleRoll']

    def __init__(self):
        super().__init__('walk_controller')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.timer = self.create_timer(0.05, self.walk_step)
        self.step_time = 0.0
        self.amplitude = 0.3
        self.forward_swing = 0.4
        self.lateral_tilt = 0.05
        self.walking = False
        self.get_logger().info('Walk controller ready — call start() to begin')

    def start(self):
        self.walking = True
        self.step_time = 0.0
        self.get_logger().info('Started walking')

    def stop(self):
        self.walking = False
        self.get_logger().info('Stopped walking')

    def walk_step(self):
        if not self.walking:
            return

        dt = 0.05
        self.step_time += dt
        t = self.step_time

        left_swing = math.sin(t * 3.0)
        right_swing = math.sin(t * 3.0 + math.pi)

        l_hip_pitch = self.forward_swing * max(0, left_swing)
        r_hip_pitch = self.forward_swing * max(0, right_swing)

        l_knee_pitch = self.amplitude * max(0, left_swing)
        r_knee_pitch = self.amplitude * max(0, right_swing)

        l_ankle_pitch = -l_knee_pitch * 0.5
        r_ankle_pitch = -r_knee_pitch * 0.5

        l_hip_roll = self.lateral_tilt * math.sin(t * 3.0)
        r_hip_roll = -l_hip_roll

        positions = [
            0.0,
            l_hip_roll,
            l_hip_pitch,
            l_knee_pitch,
            l_ankle_pitch,
            0.0,
            0.0,
            r_hip_roll,
            r_hip_pitch,
            r_knee_pitch,
            r_ankle_pitch,
            0.0,
        ]

        msg = JointTrajectory()
        msg.joint_names = self.LEG_JOINTS
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=0, nanosec=50000000)
        msg.points = [point]
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = WalkController()

    node.start()
    for _ in range(100):
        rclpy.spin_once(node, timeout_sec=0.05)
    node.stop()

    for _ in range(20):
        rclpy.spin_once(node, timeout_sec=0.05)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
