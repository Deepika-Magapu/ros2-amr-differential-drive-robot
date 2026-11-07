#!/usr/bin/env python3
"""Send a destination point to the robot and update both Gazebo and RViz."""

import argparse
import sys
from geometry_msgs.msg import Point
import rclpy
from rclpy.node import Node


def main():
    parser = argparse.ArgumentParser(description='Send navigation goal for Gazebo & RViz')
    parser.add_argument('--x', type=float, help='Target X coordinate in meters')
    parser.add_argument('--y', type=float, help='Target Y coordinate in meters')
    parser.add_argument('--room', type=str, choices=['corridor', 'office', 'conference', 'lounge', 'storage'],
                        help='Quick preset room locations')
    args, unknown = parser.parse_known_args()

    presets = {
        'corridor': (0.0, 1.5),
        'office': (-3.6, 2.0),
        'conference': (3.2, 1.8),
        'lounge': (3.2, -2.0),
        'storage': (-3.0, -2.0),
    }

    if args.room:
        x, y = presets[args.room]
        print(f"Using preset '{args.room}': ({x}, {y})")
    elif args.x is not None and args.y is not None:
        x, y = args.x, args.y
    else:
        print("--- Room Navigation Goal Dispatcher ---")
        print("Available room presets: corridor, office, conference, lounge, storage")
        choice = input("Enter room name or coordinates (e.g. 'conference' or '3.0 2.5'): ").strip()
        if choice in presets:
            x, y = presets[choice]
        else:
            try:
                parts = choice.split()
                x, y = float(parts[0]), float(parts[1])
            except Exception:
                print("Invalid input. Defaulting to corridor (0.0, 2.0)")
                x, y = 0.0, 2.0

    rclpy.init()
    node = Node('send_goal_client')
    pub = node.create_publisher(Point, '/gazebo_click_point', 10)

    # Allow publisher connection
    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.1)

    pt = Point()
    pt.x = float(x)
    pt.y = float(y)
    pt.z = 0.0
    pub.publish(pt)
    print(f"Published destination goal: x={x:.2f}, y={y:.2f} to /gazebo_click_point")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.1)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

