#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class WheelJointStatePublisher(Node):
    def __init__(self):
        super().__init__("wheel_joint_state_publisher")
        self.joints = [
            "front_left_wheel_joint",
            "front_right_wheel_joint",
            "rear_left_wheel_joint",
            "rear_right_wheel_joint",
        ]
        self.position = 0.0
        self.pub = self.create_publisher(JointState, "joint_states", 10)
        self.timer = self.create_timer(0.02, self.publish_state)

    def publish_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joints
        msg.position = [self.position] * len(self.joints)
        msg.velocity = [0.0] * len(self.joints)
        msg.effort = [0.0] * len(self.joints)
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = WheelJointStatePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
