#!/usr/bin/env python3
"""
WORKING Square Path - With continuous thrust maintenance
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import threading

class WorkingSquare(Node):
    def __init__(self):
        super().__init__('working_square')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Flight parameters
        self.turn_duration = 3.0
        self.forward_duration = 3.0
        self.takeoff_thrust = 1.5
        self.cruise_thrust = 1.5
        self.forward_speed = 0.5
        self.turn_rate = 1.2
        
        self.active = False
        self.thrust_thread = None
        
        self.get_logger().info('Working Square Controller Ready')
    
    def maintain_thrust(self):
        """Background thread to keep drone stable"""
        msg = Twist()
        msg.linear.z = float(self.cruise_thrust)
        
        while self.active:
            self.pub.publish(msg)
            time.sleep(0.1)
    
    def cmd(self, vx=0.0, vy=0.0, yaw=0.0, duration=1.0, maintain_z=True):
        """Send command while maintaining altitude"""
        msg = Twist()
        
        end = time.time() + duration
        while time.time() < end and self.active:
            msg.linear.x = float(vx)
            msg.linear.y = float(vy)
            msg.linear.z = float(self.cruise_thrust if maintain_z else 0)
            msg.angular.z = float(yaw)
            self.pub.publish(msg)
            time.sleep(0.05)
        
        # Stop movement but maintain altitude
        if maintain_z:
            msg.linear.x = 0.0
            msg.linear.y = 0.0
            msg.angular.z = 0.0
            for _ in range(10):
                self.pub.publish(msg)
                time.sleep(0.05)
    
    def run(self):
        input('Press Enter for SQUARE PATH...')
        
        self.active = True
        self.thrust_thread = threading.Thread(target=self.maintain_thrust)
        self.thrust_thread.daemon = True
        self.thrust_thread.start()
        
        self.get_logger().info('=== TAKEOFF ===')
        self.cmd(vz=1.5, duration=2.5)
        time.sleep(1)
        
        # Square: Forward, Turn, Forward, Turn, Forward, Turn, Forward
        for side in range(1, 5):
            self.get_logger().info(f'=== SIDE {side}: FORWARD ===')
            self.cmd(vx=self.forward_speed, duration=self.forward_duration)
            time.sleep(0.5)
            
            if side < 4:
                self.get_logger().info(f'=== TURN {side}: LEFT ===')
                self.cmd(yaw=self.turn_rate, duration=self.turn_duration)
                time.sleep(0.5)
        
        self.get_logger().info('=== LANDING ===')
        self.active = False
        self.cmd(vz=0.0, duration=3.0, maintain_z=False)
        
        self.get_logger().info('=== MISSION COMPLETE ===')

def main(args=None):
    rclpy.init(args=args)
    node = WorkingSquare()
    try:
        node.run()
    except KeyboardInterrupt:
        print('\nInterrupted - landing')
        node.active = False
        node.cmd(vz=0.0, duration=2.0, maintain_z=False)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()