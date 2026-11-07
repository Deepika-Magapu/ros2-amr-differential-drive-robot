#!/usr/bin/env python3
"""Publish 3D RViz markers for room walls and furniture matching Gazebo."""

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from visualization_msgs.msg import Marker, MarkerArray

# Import the exact obstacles from generator
from generate_room_environment import OBSTACLES


class RoomMarkers(Node):
    def __init__(self):
        super().__init__('room_markers')

        latched_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.marker_pub = self.create_publisher(
            MarkerArray, '/room_obstacles_markers', latched_qos
        )

        # Publish periodically to ensure late RViz subscribers receive it
        self.timer = self.create_timer(1.0, self.publish_markers)
        self.published = False
        self.get_logger().info('Room markers node initialized.')

    def publish_markers(self):
        msg = MarkerArray()
        stamp = self.get_clock().now().to_msg()

        for idx, (name, xc, yc, zc, sx, sy, sz, (r, g, b, a)) in enumerate(OBSTACLES):
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = stamp
            marker.ns = 'room_structure'
            marker.id = idx
            marker.type = Marker.CUBE
            marker.action = Marker.ADD

            marker.pose.position.x = float(xc)
            marker.pose.position.y = float(yc)
            marker.pose.position.z = float(zc)
            marker.pose.orientation.w = 1.0

            marker.scale.x = float(sx)
            marker.scale.y = float(sy)
            marker.scale.z = float(sz)

            marker.color.r = float(r)
            marker.color.g = float(g)
            marker.color.b = float(b)
            marker.color.a = float(a)

            msg.markers.append(marker)

        self.marker_pub.publish(msg)
        if not self.published:
            self.get_logger().info(f'Published {len(msg.markers)} room boundary and furniture markers to RViz.')
            self.published = True


def main(args=None):
    rclpy.init(args=args)
    node = RoomMarkers()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

