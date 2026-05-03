#!/usr/bin/env python3
"""
Combined Noise + Filter Node for Crazyflie Simulation
- Adds random noise to X and Y velocity commands
- Applies exponential moving average filter to smooth the noise
- Can toggle filter on/off with 'f' key
- Publishes 3 topics for visualization in PlotJuggler
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import random
import sys
import tty
import termios
import select

class NoiseFilterNode(Node):
    def __init__(self):
        super().__init__('noise_filter_node')
        
        # Subscribe to CLEAN commands from square script
        self.subscription = self.create_subscription(
            Twist, 
            '/clean_cmd_vel', 
            self.process_callback, 
            10
        )
        
        # Publishers for 3 topics
        self.clean_publisher = self.create_publisher(Twist, '/clean_cmd_vel', 10)
        self.noisy_publisher = self.create_publisher(Twist, '/noisy_cmd_vel', 10)
        self.final_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Noise parameters (tunable)
        self.declare_parameter('noise_xy_max', 0.4)
        self.noise_xy_max = self.get_parameter('noise_xy_max').value
        
        # Filter parameters
        self.declare_parameter('filter_alpha', 0.5)
        self.filter_alpha = self.get_parameter('filter_alpha').value
        
        # Filter state (previous filtered values)
        self.filtered_x = 0.0
        self.filtered_y = 0.0
        self.filter_initialized = False
        
        # Filter toggle
        self.filter_enabled = True
        
        # For keyboard input
        self.input_setup_done = False
        
        # Startup logging
        self.get_logger().info('=' * 50)
        self.get_logger().info('Noise + Filter Node Started')
        self.get_logger().info(f'Noise range: ±{self.noise_xy_max} m/s on X and Y axes')
        self.get_logger().info(f'Filter alpha: {self.filter_alpha}')
        self.get_logger().info(f'Filter status: ENABLED')
        self.get_logger().info('')
        self.get_logger().info('Controls:')
        self.get_logger().info('  Press "f" to toggle filter ON/OFF')
        self.get_logger().info('  Press Ctrl+C to exit')
        self.get_logger().info('=' * 50)
        
        # Setup keyboard input in a separate thread
        self.setup_keyboard_input()
    
    def setup_keyboard_input(self):
        """Setup non-blocking keyboard input"""
        # Save terminal settings
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        self.input_setup_done = True
    
    def restore_terminal(self):
        """Restore terminal settings"""
        if self.input_setup_done:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def check_keyboard(self):
        """Check if a key has been pressed without blocking"""
        if select.select([sys.stdin], [], [], 0.0)[0]:
            key = sys.stdin.read(1)
            if key.lower() == 'f':
                self.toggle_filter()
    
    def toggle_filter(self):
        """Toggle filter on/off"""
        self.filter_enabled = not self.filter_enabled
        status = "ENABLED" if self.filter_enabled else "DISABLED"
        self.get_logger().info(f'*** Filter {status} ***')
        
        # Reset filter state when re-enabling to avoid jumps
        if self.filter_enabled:
            self.filter_initialized = False
    
    def apply_low_pass_filter(self, noisy_x, noisy_y):
        """Apply exponential moving average filter"""
        if not self.filter_initialized:
            # First measurement - initialize filter
            self.filtered_x = noisy_x
            self.filtered_y = noisy_y
            self.filter_initialized = True
            return noisy_x, noisy_y
        
        # Apply filter: filtered = α × noisy + (1-α) × previous_filtered
        self.filtered_x = self.filter_alpha * noisy_x + (1 - self.filter_alpha) * self.filtered_x
        self.filtered_y = self.filter_alpha * noisy_y + (1 - self.filter_alpha) * self.filtered_y
        
        return self.filtered_x, self.filtered_y
    
    def process_callback(self, clean_msg):
        """Main callback - receives clean command, adds noise, filters, publishes"""
        
        # Check for keyboard input to toggle filter
        self.check_keyboard()
        
        # 1. Create clean message (pass-through for visualization)
        clean_passthrough = Twist()
        clean_passthrough.linear.x = clean_msg.linear.x
        clean_passthrough.linear.y = clean_msg.linear.y
        clean_passthrough.linear.z = clean_msg.linear.z
        clean_passthrough.angular = clean_msg.angular
        self.clean_publisher.publish(clean_passthrough)
        
        # 2. Create noisy message (add noise to X and Y only)
        noisy_msg = Twist()
        noisy_msg.linear.x = clean_msg.linear.x
        noisy_msg.linear.y = clean_msg.linear.y
        noisy_msg.linear.z = clean_msg.linear.z  # No noise on Z
        noisy_msg.angular = clean_msg.angular
        
        # Add random noise to X and Y
        noise_x = random.uniform(-self.noise_xy_max, self.noise_xy_max)
        noise_y = random.uniform(-self.noise_xy_max, self.noise_xy_max)
        noisy_msg.linear.x += noise_x
        noisy_msg.linear.y += noise_y
        
        # Optional: clamp values to reasonable limits (max 1.0 m/s)
        noisy_msg.linear.x = max(-1.0, min(1.0, noisy_msg.linear.x))
        noisy_msg.linear.y = max(-1.0, min(1.0, noisy_msg.linear.y))
        
        self.noisy_publisher.publish(noisy_msg)
        
        # 3. Create final message (filtered or raw noisy based on toggle)
        final_msg = Twist()
        
        if self.filter_enabled:
            # Apply low-pass filter to X and Y
            filtered_x, filtered_y = self.apply_low_pass_filter(noisy_msg.linear.x, noisy_msg.linear.y)
            final_msg.linear.x = filtered_x
            final_msg.linear.y = filtered_y
        else:
            # Filter disabled - pass through raw noisy commands
            final_msg.linear.x = noisy_msg.linear.x
            final_msg.linear.y = noisy_msg.linear.y
            # Reset filter state when disabled to avoid jumps when re-enabling
            self.filter_initialized = False
        
        # Copy remaining fields unchanged
        final_msg.linear.z = noisy_msg.linear.z  # Z is clean (no noise added)
        final_msg.angular = noisy_msg.angular
        
        # Publish final command to drone
        self.final_publisher.publish(final_msg)
        
        # Optional debug logging (uncomment if needed, but will spam console)
        # self.get_logger().debug(f'Clean: X={clean_msg.linear.x:.2f}, Noisy: X={noisy_msg.linear.x:.2f}, Final: X={final_msg.linear.x:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = NoiseFilterNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\nShutting down noise + filter node...')
    finally:
        node.restore_terminal()  # Restore terminal settings before exiting
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()