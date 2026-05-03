#!/usr/bin/env python3
"""
HOVER TEST with Trim (counteracts right drift)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class HoverTest(Node):
    def __init__(self):
        super().__init__('hover_test')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
    
    def send_command(self, vz=0.0, vx=0.0, duration=1.0):
        msg = Twist()
        msg.linear.x = float(vx)
        msg.linear.y = 0.0
        msg.linear.z = float(vz)
        msg.angular.z = 0.0
        
        end = time.time() + float(duration)
        while time.time() < end:
            self.pub.publish(msg)
            time.sleep(0.05)
    
    def run(self):
        input('Press Enter to HOVER for 10 seconds...')
        
        print("HOVERING - Small left trim to counter right drift")
        # Send slight left command (-0.05) to counter right drift
        self.send_command(vz=1.5, vx=-0.05, duration=10.0)
        
        print("Landing")
        self.send_command(vz=0.0, duration=3.0)
        
        print("Test complete!")

def main(args=None):
    rclpy.init(args=args)
    node = HoverTest()
    try:
        node.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()