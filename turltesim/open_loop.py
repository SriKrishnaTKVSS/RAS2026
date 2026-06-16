#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist


class OpenLoop(Node):

    def __init__(self):
        super().__init__('open_loop')

        self.pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10)

        self.timer = self.create_timer(
            0.1,
            self.control_loop)

    def control_loop(self):

        cmd = Twist()

        cmd.linear.x = 2.0
        cmd.angular.z = 0.5

        self.pub.publish(cmd)


def main():

    rclpy.init()

    node = OpenLoop()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()