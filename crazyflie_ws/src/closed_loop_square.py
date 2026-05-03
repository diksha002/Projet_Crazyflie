#!/usr/bin/env python3
"""
Closed-Loop Square Controller - Reads pose directly from Gazebo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
import time
import math

class ClosedLoopSquare(Node):
    def __init__(self):
        super().__init__('closed_loop_square')
        
        # Publisher for commands
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber for pose (direct from Gazebo via bridge)
        self.pose_sub = self.create_subscription(PoseStamped, '/pose', self.pose_callback, 10)
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.pose_received = False
        
        # Control parameters
        self.takeoff_z = 0.5  # Target altitude
        self.square_size = 1.0  # 1 meter square
        self.tolerance = 0.1  # 10cm tolerance
        
        self.get_logger().info('Closed-Loop Square Controller Ready')
    
    def pose_callback(self, msg):
        self.current_x = msg.pose.position.x
        self.current_y = msg.pose.position.y
        self.current_z = msg.pose.position.z
        self.pose_received = True
    
    def wait_for_pose(self):
        while not self.pose_received and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        self.get_logger().info(f'Initial pose: ({self.current_x}, {self.current_y}, {self.current_z})')
    
    def send_command(self, vx, vy, vz, yaw, duration):
        msg = Twist()
        msg.linear.x = vx
        msg.linear.y = vy
        msg.linear.z = vz
        msg.angular.z = yaw
        
        end = time.time() + duration
        while time.time() < end and rclpy.ok():
            self.cmd_pub.publish(msg)
            time.sleep(0.05)
    
    def takeoff(self):
        self.get_logger().info('Taking off...')
        # Climb until reaching target altitude
        while self.current_z < self.takeoff_z and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            error = self.takeoff_z - self.current_z
            vz = min(0.5, error * 2.0)  # Proportional control
            self.send_command(0, 0, vz, 0, 0.1)
        
        # Hover for 2 seconds
        self.send_command(0, 0, 1.5, 0, 2.0)
        self.get_logger().info('Takeoff complete')
    
    def fly_to_point(self, target_x, target_y):
        self.get_logger().info(f'Flying to ({target_x}, {target_y})')
        
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            
            dx = target_x - self.current_x
            dy = target_y - self.current_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.tolerance:
                break
            
            # Proportional control
            speed = min(0.5, distance)
            angle = math.atan2(dy, dx)
            
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            self.send_command(vx, vy, 1.5, 0, 0.1)
        
        # Stop and hover
        self.send_command(0, 0, 1.5, 0, 1.0)
    
    def land(self):
        self.get_logger().info('Landing...')
        self.send_command(0, 0, 0, 0, 3.0)
        self.get_logger().info('Landed')
    
    def execute_square(self):
        input('Press Enter for CLOSED-LOOP SQUARE...')
        
        # Get starting position
        self.wait_for_pose()
        start_x = self.current_x
        start_y = self.current_y
        
        # Takeoff
        self.takeoff()
        
        # Define waypoints (relative to start)
        waypoints = [
            (start_x + self.square_size, start_y),           # Forward
            (start_x + self.square_size, start_y + self.square_size),  # Right
            (start_x, start_y + self.square_size),           # Back
            (start_x, start_y)                               # Return to start
        ]
        
        # Fly the square
        for i, (wp_x, wp_y) in enumerate(waypoints, 1):
            self.get_logger().info(f'Waypoint {i}: ({wp_x:.2f}, {wp_y:.2f})')
            self.fly_to_point(wp_x, wp_y)
        
        # Land
        self.land()

def main(args=None):
    rclpy.init(args=args)
    node = ClosedLoopSquare()
    try:
        node.execute_square()
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted')
        node.land()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
