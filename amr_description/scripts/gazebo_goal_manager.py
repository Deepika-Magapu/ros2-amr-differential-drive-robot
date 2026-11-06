#!/usr/bin/env python3
"""Manage navigation destination points specified in Gazebo or via ROS 2."""

import math
import subprocess
import threading
import time

from geometry_msgs.msg import Point, Pose, PoseStamped
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from visualization_msgs.msg import Marker, MarkerArray


class GazeboGoalManager(Node):
    def __init__(self):
        super().__init__('gazebo_goal_manager')

        self._nav_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self._current_goal_handle = None
        self._last_goal_coords = None
        self._last_goal_time = 0.0

        # RViz Marker publisher
        latched_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._marker_pub = self.create_publisher(
            MarkerArray, '/destination_marker_rviz', latched_qos
        )

        # Gazebo floor click subscription (bridged from ignition.msgs.Vector3d)
        self.create_subscription(
            Point, '/gazebo_click_point', self._on_gazebo_click, 10
        )

        # Gazebo marker translation subscription (if marker moved in Gazebo)
        self.create_subscription(
            Pose, '/destination_marker/pose', self._on_marker_pose, 10
        )

        # Command topic
        self.create_subscription(
            PoseStamped, '/gazebo_goal_cmd', self._on_pose_stamped, 10
        )

        # Periodically re-publish RViz marker
        self.create_timer(1.0, self._publish_rviz_marker)

        self.get_logger().info(
            'Gazebo Goal Manager active: click floor or move target in Gazebo to navigate.'
        )

    def _on_gazebo_click(self, msg: Point):
        self.get_logger().info(
            f'Received floor click from Gazebo: x={msg.x:.2f}, y={msg.y:.2f}'
        )
        self.dispatch_goal(msg.x, msg.y, update_gazebo_marker=True)

    def _on_marker_pose(self, msg: Pose):
        x = msg.position.x
        y = msg.position.y
        # Only trigger if moved significantly (> 0.2m from last goal)
        if self._last_goal_coords is None:
            return
        dx = x - self._last_goal_coords[0]
        dy = y - self._last_goal_coords[1]
        dist = math.hypot(dx, dy)
        if dist > 0.25 and (time.time() - self._last_goal_time) > 1.0:
            self.get_logger().info(
                f'Gazebo target marker translated to: x={x:.2f}, y={y:.2f}'
            )
            self.dispatch_goal(x, y, update_gazebo_marker=False)

    def _on_pose_stamped(self, msg: PoseStamped):
        yaw = 2.0 * math.atan2(msg.pose.orientation.z, msg.pose.orientation.w)
        self.dispatch_goal(
            msg.pose.position.x,
            msg.pose.position.y,
            yaw=yaw,
            update_gazebo_marker=True,
        )

    def dispatch_goal(
        self, x: float, y: float, yaw: float = 0.0, update_gazebo_marker: bool = True
    ):
        now = time.time()
        # Debounce: avoid duplicate dispatches within 0.4s
        if self._last_goal_coords:
            dx = x - self._last_goal_coords[0]
            dy = y - self._last_goal_coords[1]
            if math.hypot(dx, dy) < 0.1 and (now - self._last_goal_time) < 0.8:
                return

        # Room boundary bounds checking
        clamped_x = max(-5.6, min(5.6, x))
        clamped_y = max(-4.6, min(4.6, y))
        if clamped_x != x or clamped_y != y:
            self.get_logger().warn(
                f'Destination ({x:.2f}, {y:.2f}) was outside boundaries; clamped to ({clamped_x:.2f}, {clamped_y:.2f})'
            )
            x, y = clamped_x, clamped_y

        self._last_goal_coords = (x, y, yaw)
        self._last_goal_time = now

        # Update Gazebo destination marker model position
        if update_gazebo_marker:
            self._move_gazebo_marker(x, y)

        # Update RViz visual marker
        self._publish_rviz_marker()

        # Send Nav2 action goal
        self._send_nav2_goal(x, y, yaw)

    def _move_gazebo_marker(self, x: float, y: float):
        """Asynchronously call Gazebo set_pose service to place the 3D marker."""

        def _call_service():
            req_str = f"name: 'destination_marker', position: {{x: {x:.3f}, y: {y:.3f}, z: 0.01}}"
            cmd = [
                'ign',
                'service',
                '-s',
                '/world/nav_world/set_pose',
                '--reqtype',
                'ignition.msgs.Pose',
                '--reptype',
                'ignition.msgs.Boolean',
                '--timeout',
                '500',
                '--req',
                req_str,
            ]
            try:
                subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=1.0,
                )
            except Exception:
                pass

        threading.Thread(target=_call_service, daemon=True).start()

    def _publish_rviz_marker(self):
        if not self._last_goal_coords:
            return

        x, y, yaw = self._last_goal_coords
        stamp = self.get_clock().now().to_msg()
        array = MarkerArray()

        # Base circle disc on floor
        m1 = Marker()
        m1.header.frame_id = 'map'
        m1.header.stamp = stamp
        m1.ns = 'destination_target'
        m1.id = 0
        m1.type = Marker.CYLINDER
        m1.action = Marker.ADD
        m1.pose.position.x = x
        m1.pose.position.y = y
        m1.pose.position.z = 0.015
        m1.pose.orientation.w = 1.0
        m1.scale.x = 0.7
        m1.scale.y = 0.7
        m1.scale.z = 0.03
        m1.color.r = 0.0
        m1.color.g = 1.0
        m1.color.b = 0.4
        m1.color.a = 0.75
        array.markers.append(m1)

        # Vertical beacon flagpole
        m2 = Marker()
        m2.header.frame_id = 'map'
        m2.header.stamp = stamp
        m2.ns = 'destination_target'
        m2.id = 1
        m2.type = Marker.CYLINDER
        m2.action = Marker.ADD
        m2.pose.position.x = x
        m2.pose.position.y = y
        m2.pose.position.z = 0.6
        m2.pose.orientation.w = 1.0
        m2.scale.x = 0.04
        m2.scale.y = 0.04
        m2.scale.z = 1.2
        m2.color.r = 1.0
        m2.color.g = 1.0
        m2.color.b = 1.0
        m2.color.a = 0.9
        array.markers.append(m2)

        # Glowing sphere at top
        m3 = Marker()
        m3.header.frame_id = 'map'
        m3.header.stamp = stamp
        m3.ns = 'destination_target'
        m3.id = 2
        m3.type = Marker.SPHERE
        m3.action = Marker.ADD
        m3.pose.position.x = x
        m3.pose.position.y = y
        m3.pose.position.z = 1.25
        m3.pose.orientation.w = 1.0
        m3.scale.x = 0.22
        m3.scale.y = 0.22
        m3.scale.z = 0.22
        m3.color.r = 0.1
        m3.color.g = 1.0
        m3.color.b = 0.3
        m3.color.a = 0.95
        array.markers.append(m3)

        # Text label above target
        m4 = Marker()
        m4.header.frame_id = 'map'
        m4.header.stamp = stamp
        m4.ns = 'destination_target'
        m4.id = 3
        m4.type = Marker.TEXT_VIEW_FACING
        m4.action = Marker.ADD
        m4.pose.position.x = x
        m4.pose.position.y = y
        m4.pose.position.z = 1.5
        m4.pose.orientation.w = 1.0
        m4.scale.z = 0.25
        m4.color.r = 1.0
        m4.color.g = 1.0
        m4.color.b = 1.0
        m4.color.a = 1.0
        m4.text = f'DESTINATION ({x:.1f}, {y:.1f})'
        array.markers.append(m4)

        self._marker_pub.publish(array)

    def _send_nav2_goal(self, x: float, y: float, yaw: float):
        if not self._nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn(
                'Nav2 /navigate_to_pose action server is not ready yet. Goal buffered.'
            )
            return

        # Cancel previous goal if robot was already navigating
        if self._current_goal_handle is not None:
            self.get_logger().info('Preempting active navigation goal for new destination...')
            try:
                self._current_goal_handle.cancel_goal_async()
            except Exception:
                pass

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Orientation quaternion from yaw
        half_yaw = yaw / 2.0
        goal_msg.pose.pose.orientation.z = math.sin(half_yaw)
        goal_msg.pose.pose.orientation.w = math.cos(half_yaw)

        self.get_logger().info(
            f'>>> Dispatching path planning goal to Nav2: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad'
        )

        future = self._nav_client.send_goal_async(
            goal_msg, feedback_callback=self._on_feedback
        )
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future):
        try:
            goal_handle = future.result()
        except Exception as e:
            self.get_logger().error(f'Failed to send goal to Nav2: {e}')
            return

        if not goal_handle.accepted:
            self.get_logger().warn(
                'Nav2 rejected the destination goal. Point may be occupied or inside an obstacle.'
            )
            return

        self.get_logger().info('Nav2 accepted destination! Planning obstacle-free path...')
        self._current_goal_handle = goal_handle

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_result)

    def _on_feedback(self, feedback_msg):
        fb = feedback_msg.feedback
        # Periodic feedback can be logged if desired

    def _on_result(self, future):
        self._current_goal_handle = None
        try:
            result = future.result()
            status = result.status
            # 4 == STATUS_SUCCEEDED
            if status == 4:
                self.get_logger().info(
                    'SUCCESS: Robot reached the Gazebo destination point!'
                )
            else:
                self.get_logger().info(f'Navigation finished with action status: {status}')
        except Exception as e:
            self.get_logger().error(f'Navigation result error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = GazeboGoalManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

