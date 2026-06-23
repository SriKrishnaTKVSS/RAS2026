import rclpy
from rclpy.node import Node
from rosgraph_msgs.msg import Clock


class SensorMonitor(Node):
    def __init__(self):
        super().__init__('sensor_monitor')
        self.clock_sub = self.create_subscription(
            Clock, '/clock', self.clock_cb, 10)
        self.clock_msg = None
        self.timer = self.create_timer(5.0, self.report)
        self.get_logger().info(
            'Sensor monitor active — reporting every 5s\n'
            'NOTE: The Fuel Nao model has no camera/IMU/laser/odometry topics.\n'
            'Joint states are embedded in /world/nao_world/state (not bridged).\n'
            'Use: gz topic -e -t /world/nao_world/state | grep -A2 "name:.*joint"')

    def clock_cb(self, msg):
        self.clock_msg = msg

    def report(self):
        if self.clock_msg:
            t = self.clock_msg.clock
            self.get_logger().info(
                f'Sim running — sim time: {t.sec:>6}s.{t.nanosec:09d}')
        else:
            self.get_logger().info('Waiting for /clock...')


def main(args=None):
    rclpy.init(args=args)
    node = SensorMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
