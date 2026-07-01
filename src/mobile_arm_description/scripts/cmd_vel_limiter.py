#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CmdVelLimiter(Node):
    def __init__(self):
        super().__init__("cmd_vel_limiter")

        self.max_linear = self.declare_parameter("max_linear_velocity", 0.8).value
        self.max_angular = self.declare_parameter("max_angular_velocity", 0.8).value
        self.max_linear_accel = self.declare_parameter("max_linear_acceleration", 10.0).value
        self.max_angular_accel = self.declare_parameter("max_angular_acceleration", 10.0).value
        self.cmd_timeout = self.declare_parameter("cmd_timeout", 2.0).value
        self.publish_rate = self.declare_parameter("publish_rate", 50.0).value

        self.target = Twist()
        self.current = Twist()
        self.last_cmd_time = self.get_clock().now()
        self.last_update_time = self.last_cmd_time

        self.pub = self.create_publisher(Twist, "cmd_vel_limited", 10)
        self.sub = self.create_subscription(Twist, "cmd_vel", self.cmd_callback, 10)
        self.timer = self.create_timer(1.0 / self.publish_rate, self.update)

    def cmd_callback(self, msg):
        self.target.linear.x = self.clamp_finite(
            msg.linear.x, -0.5 * self.max_linear, self.max_linear
        )
        self.target.linear.y = 0.0
        self.target.linear.z = 0.0
        self.target.angular.x = 0.0
        self.target.angular.y = 0.0
        self.target.angular.z = self.clamp_finite(
            msg.angular.z, -self.max_angular, self.max_angular
        )
        self.last_cmd_time = self.get_clock().now()

    def update(self):
        now = self.get_clock().now()
        dt = max((now - self.last_update_time).nanoseconds * 1e-9, 0.0)
        self.last_update_time = now

        if (now - self.last_cmd_time).nanoseconds * 1e-9 > self.cmd_timeout:
            self.target = Twist()

        self.current.linear.x = self.step_toward(
            self.current.linear.x,
            self.target.linear.x,
            self.max_linear_accel * dt,
        )
        self.current.angular.z = self.step_toward(
            self.current.angular.z,
            self.target.angular.z,
            self.max_angular_accel * dt,
        )

        self.pub.publish(self.current)

    @staticmethod
    def clamp_finite(value, low, high):
        if not math.isfinite(value):
            return 0.0
        return min(max(value, low), high)

    @staticmethod
    def step_toward(current, target, max_step):
        if max_step <= 0.0:
            return target
        error = target - current
        if abs(error) <= max_step:
            return target
        return current + math.copysign(max_step, error)


def main():
    rclpy.init()
    node = CmdVelLimiter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
