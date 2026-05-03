#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import random
import sys

class NoiseNode(Node):
    def __init__(self):
        super().__init__('cmd_vel_noise_node')
        
        # Subscribe to CLEAN commands
        self.subscription = self.create_subscription(
            Twist, 
            '/clean_cmd_vel', 
            self.add_noise_callback, 
            10
        )
        
        # Publish NOISY commands
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Noise parameters
        self.noise_xy_max = 0.1  # ±0.1 m/s noise
        
        self.get_logger().info('Noise Node Started!')
        self.get_logger().info(f'Noise range: ±{self.noise_xy_max} m/s on X and Y axes')
        self.get_logger().info('Subscribed to /clean_cmd_vel')
        self.get_logger().info('Publishing to /cmd_vel')
    
    def add_noise_callback(self, clean_msg):
        # Create noisy message
        noisy_msg = Twist()
        
        # Copy all values
        noisy_msg.linear.x = clean_msg.linear.x
        noisy_msg.linear.y = clean_msg.linear.y
        noisy_msg.linear.z = clean_msg.linear.z  # No noise on Z
        noisy_msg.angular = clean_msg.angular
        
        # Add noise to X and Y only
        noisy_msg.linear.x += random.uniform(-self.noise_xy_max, self.noise_xy_max)
        noisy_msg.linear.y += random.uniform(-self.noise_xy_max, self.noise_xy_max)
        
        # Optional: Log when significant noise is added
        if abs(noisy_msg.linear.x - clean_msg.linear.x) > 0.05:
            self.get_logger().debug(f'Added X noise: {noisy_msg.linear.x - clean_msg.linear.x:.3f}')
        
        # Publish the noisy command
        self.publisher.publish(noisy_msg)

def main(args=None):
    rclpy.init(args=args)
    node = NoiseNode()
    
    try:
        # Keep the node running and processing callbacks
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\nShutting down noise node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()