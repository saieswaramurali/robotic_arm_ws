#!/usr/bin/env python3

import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


class OdomSpeedMonitor(Node):
    def __init__(self):
        super().__init__("odom_speed_monitor")
        self.create_subscription(Odometry, "odom", self.odom_callback, 10)
        self.last_log_time = self.get_clock().now()

    def odom_callback(self, msg):
        now = self.get_clock().now()
        if (now - self.last_log_time).nanoseconds * 1e-9 < 0.5:
            return
        self.last_log_time = now

        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        wz = msg.twist.twist.angular.z
        speed = math.hypot(vx, vy)
        self.get_logger().info(f"odom speed={speed:.3f} m/s angular={wz:.3f} rad/s")


def main():
    rclpy.init()
    node = OdomSpeedMonitor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
