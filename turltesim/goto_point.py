#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist


class GoToPoint(Node):

    def __init__(self):

        super().__init__('goto_point')

        self.pose = None

        self.xd = 8.0
        self.yd = 8.0

        self.sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)

        self.pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10)

        self.timer = self.create_timer(
            0.05,
            self.control_loop)

    def pose_callback(self, msg):
        self.pose = msg

    def wrap(self, angle):
        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    def control_loop(self):

        if self.pose is None:
            return

        dx = self.xd - self.pose.x
        dy = self.yd - self.pose.y

        distance = math.sqrt(dx**2 + dy**2)

        theta_d = math.atan2(dy, dx)

        error_theta = self.wrap(
            theta_d - self.pose.theta
        )

        cmd = Twist()

        cmd.linear.x = 1.5 * distance
        cmd.angular.z = 4.0 * error_theta

        self.pub.publish(cmd)


def main():

    rclpy.init()

    node = GoToPoint()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()