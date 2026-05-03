#!/usr/bin/env python3
"""
SIMPLE Square - One square only using dedicated movement functions
Take off -> move forward -> move right -> move backward -> move left -> land

"""


import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class SimpleSquare(Node):
    def __init__(self):
        super().__init__('simple_square')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.speed = 0.5  # Default movement speed
        self.height = 1.5
    
    def takeoff(self, duration=2.5):
        """Takeoff and maintain hover"""
        cmd = Twist()
        cmd.linear.z = self.height
        end = time.time() + duration
        while time.time() < end:
            self.publisher.publish(cmd)
            time.sleep(0.05)
        
        # Hover in place
        cmd.linear.z = 0.0
        for _ in range(5):
            self.publisher.publish(cmd)
            time.sleep(0.05)
    
    def move_forward(self, duration):
        """Move forward for specified duration"""
        cmd = Twist()
        cmd.linear.x = self.speed
        cmd.linear.z = 0.0  # Maintain height
        end = time.time() + duration
        while time.time() < end:
            self.publisher.publish(cmd)
            time.sleep(0.05)
        
        # Stop forward motion
        cmd.linear.x = 0.0
        self.publisher.publish(cmd)
        time.sleep(0.2)
    
    def move_backward(self, duration):
        """Move backward for specified duration"""
        cmd = Twist()
        cmd.linear.x = -self.speed
        cmd.linear.z = 0.0  # Maintain height
        end = time.time() + duration
        while time.time() < end:
            self.publisher.publish(cmd)
            time.sleep(0.05)
        
        # Stop backward motion
        cmd.linear.x = 0.0
        self.publisher.publish(cmd)
        time.sleep(0.2)
    
    def move_right(self, duration):
        """Move right for specified duration"""
        cmd = Twist()
        cmd.linear.y = -self.speed
        cmd.linear.z = 0.0  # Maintain height
        end = time.time() + duration
        while time.time() < end:
            self.publisher.publish(cmd)
            time.sleep(0.05)
        
        # Stop right motion
        cmd.linear.y = 0.0
        self.publisher.publish(cmd)
        time.sleep(0.2)
    
    def move_left(self, duration):
        """Move left for specified duration"""
        cmd = Twist()
        cmd.linear.y = self.speed
        cmd.linear.z = 0.0  # Maintain height
        end = time.time() + duration
        while time.time() < end:
            self.publisher.publish(cmd)
            time.sleep(0.05)
        
        # Stop left motion
        cmd.linear.y = 0.0
        self.publisher.publish(cmd)
        time.sleep(0.2)
    
    """
    Changed function below for drone to go back to initial height (0)
    def land(self):
        #Land the drone
        cmd = Twist()
        cmd.linear.z = -1.5
        #cmd.linear.z = 0.0
        for _ in range(60):
            self.publisher.publish(cmd)
            time.sleep(0.05)
    """

    def land(self, duration=2.5):
        """land and maintain hover"""
        cmd = Twist()
        cmd.linear.z = -self.height
        end = time.time() + duration
        while time.time() < end:
            self.publisher.publish(cmd)
            time.sleep(0.05)
        
        # Hover in place
        cmd.linear.z = 0.0
        for _ in range(5):
            self.publisher.publish(cmd)
            time.sleep(0.05)
    
    def run(self):
        input('Press Enter for ONE SQUARE...')
        
        print('Takeoff')
        self.takeoff(duration=2.5)
        time.sleep(1)
        
        # ONE SQUARE PATTERN (runs once)
        print('Moving Forward')
        self.move_forward(duration=2.5)
        time.sleep(0.5)
        
        print('Moving Right')
        self.move_right(duration=2.5)
        time.sleep(0.5)
        
        print('Moving Backward')
        self.move_backward(duration=2.5)
        time.sleep(0.5)
        
        print('Moving Left')
        self.move_left(duration=2.5)
        time.sleep(0.5)
        
        print('Landing')
        self.land()
        
        print('Square complete!')

def main(args=None):
    rclpy.init(args=args)
    node = SimpleSquare()
    try:
        node.run()
    except KeyboardInterrupt:
        print('\nUser interrupted')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()