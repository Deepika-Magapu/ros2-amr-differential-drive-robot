#!/usr/bin/env python3
"""Render occupancy-grid obstacle cells as RViz POINTS (avoids Map shader)."""

import rclpy
from geometry_msgs.msg import Point
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from visualization_msgs.msg import Marker


class MazeMapMarkers(Node):
    def __init__(self):
        super().__init__('maze_map_markers')
        self.map_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        marker_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.marker_pub = self.create_publisher(
            Marker, '/maze/map_obstacles', marker_qos
        )
        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, self.map_qos
        )

    def map_callback(self, grid):
        marker = Marker()
        marker.header.frame_id = grid.header.frame_id or 'map'
        marker.ns = 'maze_walls'
        marker.id = 0
        marker.type = Marker.POINTS
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = grid.info.resolution
        marker.scale.y = grid.info.resolution
        marker.color.r = 0.12
        marker.color.g = 0.12
        marker.color.b = 0.12
        marker.color.a = 1.0
        origin_x = grid.info.origin.position.x
        origin_y = grid.info.origin.position.y
        width = grid.info.width
        for index, occupancy in enumerate(grid.data):
            if occupancy < 50:
                continue
            x = origin_x + (index % width + 0.5) * grid.info.resolution
            y = origin_y + (index // width + 0.5) * grid.info.resolution
            marker.points.append(Point(x=x, y=y, z=0.02))
        marker.header.stamp = self.get_clock().now().to_msg()
        self.marker_pub.publish(marker)
        self.get_logger().info(f'Loaded {len(marker.points)} maze obstacle cells for RViz')


def main():
    rclpy.init()
    node = MazeMapMarkers()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
