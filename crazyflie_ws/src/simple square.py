#!/usr/bin/env python3
"""
SIMPLE Square - One command at a time with pauses
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class SimpleSquare(Node):
    def __init__(self):
        super().__init__('simple_square')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
    
    def cmd(self, vx=0.0, yaw=0.0, duration=1.0):
        msg = Twist()
        msg.linear.z = 1.5  # Constant thrust
        msg.linear.x = vx
        msg.angular.z = yaw
        
        end = time.time() + duration
        while time.time() < end:
            self.pub.publish(msg)
            time.sleep(0.05)
        
        # Hover in place
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        for _ in range(5):
            self.pub.publish(msg)
            time.sleep(0.05)
    
    def run(self):
        input('Press Enter for SQUARE...')
        
        print('Takeoff')
        self.cmd(duration=2.5)
        time.sleep(1)
        
        # Square pattern
        for side in range(4):
            print(f'Forward {side+1}')
            # self.cmd(vx=0.5, duration=2.5)
            # Stop before turning
            self.cmd(vx=0, duration=1.0)  # Stop moving
            time.sleep(0.5)
            
            if side < 3:
                print(f'Turn {side+1}')
                # self.cmd(yaw=1.2, duration=2.5)
                self.cmd(yaw=0.5, duration=6.0)
                # time.sleep(0.5)
                time.sleep(3.0)
        
        print('Landing')
        msg = Twist()
        msg.linear.z = 0.0
        for _ in range(60):
            self.pub.publish(msg)
            time.sleep(0.05)
        
        print('Done!')

def main(args=None):
    rclpy.init(args=args)
    node = SimpleSquare()
    try:
        node.run()
    except:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()