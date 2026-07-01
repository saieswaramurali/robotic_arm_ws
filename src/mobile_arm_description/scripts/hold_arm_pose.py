#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class HoldArmPose(Node):
    def __init__(self):
        super().__init__("hold_arm_pose")
        self.arm_positions = self.declare_parameter(
            "arm_positions", [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
        ).value
        self.gripper_positions = self.declare_parameter("gripper_positions", [0.0] * 11).value

        self.arm_pub = self.create_publisher(
            Float64MultiArray, "/arm_position_controller/commands", 10
        )
        self.gripper_pub = self.create_publisher(
            Float64MultiArray, "/gripper_position_controller/commands", 10
        )
        self.timer = self.create_timer(0.05, self.publish_commands)

    def publish_commands(self):
        arm_msg = Float64MultiArray()
        arm_msg.data = list(self.arm_positions)
        self.arm_pub.publish(arm_msg)

        gripper_msg = Float64MultiArray()
        gripper_msg.data = list(self.gripper_positions)
        self.gripper_pub.publish(gripper_msg)


def main():
    rclpy.init()
    node = HoldArmPose()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
