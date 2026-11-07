#!/usr/bin/env python3
"""Publish the odom-to-base transform carried by Gazebo's odometry topic."""

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class OdomTfBroadcaster(Node):
    def __init__(self):
        super().__init__('odom_tf_broadcaster')
        self.declare_parameter('base_link_height', 0.433)
        self._base_link_height = self.get_parameter('base_link_height').value
        self._broadcaster = TransformBroadcaster(self)
        self.create_subscription(Odometry, '/odom', self._on_odom, 10)

    def _on_odom(self, odometry):
        transform = TransformStamped()
        transform.header = odometry.header
        transform.child_frame_id = odometry.child_frame_id
        transform.transform.translation.x = odometry.pose.pose.position.x
        transform.transform.translation.y = odometry.pose.pose.position.y
        # Gazebo's planar DiffDrive odometry reports z=0 even though the
        # chassis link is spawned above the ground. Keep URDF and odom TF aligned.
        transform.transform.translation.z = (
            odometry.pose.pose.position.z + self._base_link_height
        )
        transform.transform.rotation = odometry.pose.pose.orientation
        self._broadcaster.sendTransform(transform)


def main():
    rclpy.init()
    node = OdomTfBroadcaster()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
