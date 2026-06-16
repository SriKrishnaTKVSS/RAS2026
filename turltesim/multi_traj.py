#!/usr/bin/env python3

import math
import yaml

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist


def wrap_angle(angle):
    return math.atan2(
        math.sin(angle),
        math.cos(angle)
    )


class TrajectoryTracker(Node):

    def __init__(self):

        super().__init__('trajectory_tracker')

        self.pose = None

        config_file = "config/trajectory_config.yaml"

        with open(config_file, "r") as f:
            self.cfg = yaml.safe_load(f)

        self.kv = self.cfg["gains"]["kv"]
        self.kw = self.cfg["gains"]["kw"]

        rate = self.cfg["controller"]["publish_rate"]

        self.sub = self.create_subscription(
            Pose,
            "/turtle1/pose",
            self.pose_callback,
            10
        )

        self.pub = self.create_publisher(
            Twist,
            "/turtle1/cmd_vel",
            10
        )

        self.timer = self.create_timer(
            1.0 / rate,
            self.control_loop
        )

    def pose_callback(self, msg):
        self.pose = msg

    def reference(self, t):

        traj_type = self.cfg["trajectory"]["type"]

        if traj_type == "circle":

            p = self.cfg["circle"]

            xd = p["xc"] + p["radius"] * math.cos(
                p["omega"] * t
            )

            yd = p["yc"] + p["radius"] * math.sin(
                p["omega"] * t
            )

        elif traj_type == "ellipse":

            p = self.cfg["ellipse"]

            xd = p["xc"] + p["a"] * math.cos(
                p["omega"] * t
            )

            yd = p["yc"] + p["b"] * math.sin(
                p["omega"] * t
            )

        elif traj_type == "figure8":

            p = self.cfg["figure8"]

            xd = p["xc"] + p["ax"] * math.sin(
                p["omega"] * t
            )

            yd = p["yc"] + p["ay"] * math.sin(
                2.0 * p["omega"] * t
            )

        elif traj_type == "spiral":

            p = self.cfg["spiral"]

            r = min(
                p["max_radius"],
                p["growth_rate"] * t
            )

            xd = p["xc"] + r * math.cos(
                p["omega"] * t
            )

            yd = p["yc"] + r * math.sin(
                p["omega"] * t
            )

        else:

            xd = 5.5
            yd = 5.5

        return xd, yd

    def control_loop(self):

        if self.pose is None:
            return

        t = (
            self.get_clock()
            .now()
            .nanoseconds * 1e-9
        )

        xd, yd = self.reference(t)

        dx = xd - self.pose.x
        dy = yd - self.pose.y

        distance = math.hypot(dx, dy)

        theta_d = math.atan2(dy, dx)

        heading_error = wrap_angle(
            theta_d - self.pose.theta
        )

        cmd = Twist()

        cmd.linear.x = self.kv * distance
        cmd.angular.z = self.kw * heading_error

        self.pub.publish(cmd)


def main():

    rclpy.init()

    node = TrajectoryTracker()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()