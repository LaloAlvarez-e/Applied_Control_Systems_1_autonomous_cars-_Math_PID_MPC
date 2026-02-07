"""
Real-Time Animation for Train Tracking Falling Object System
Shows actual physical motion: object falling vertically, train moving horizontally
Enhanced with 7 plots matching Mark Misin's layout: 4×3 grid
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, FFMpegWriter
import pandas as pd
from pathlib import Path
import argparse
import os

class RealtimeSimulationAnimation:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.controller_name = Path(csv_file).stem.replace('_', ' ')
        
        # Extract angle and ball X position from filename
        # Supports both formats:
        #   - New: PID_A30_BallX070_TrainX010.csv
        #   - Old: PID_Controller_Angle_30.csv
        filename = Path(csv_file).stem
        self.angle = 0.0  # Default to flat surface
        self.ball_x_position = None  # Will be extracted from filename or CSV
        self.train_x_initial = None  # Will be extracted from filename or CSV
        
        import re
        
        # Try Random format: Random_S{num}_A{angle}_BallX{x}Y{y}_TrainX{x}
        if filename.startswith('Random_S'):
            try:
                # Extract angle
                match_angle = re.search(r'_A(\d+)', filename)
                if match_angle:
                    self.angle = float(match_angle.group(1))
                    print(f"Detected landing angle: {self.angle}°")
                
                # Extract ball X and Y positions
                match_ball = re.search(r'BallX(\d+)Y(\d+)', filename)
                if match_ball:
                    self.ball_x_position = float(match_ball.group(1))
                    self.ball_y_initial = float(match_ball.group(2))
                    print(f"Detected ball position: X={self.ball_x_position}m, Y={self.ball_y_initial}m")
                
                # Extract train initial X position
                match_train_x = re.search(r'TrainX(\d+)', filename)
                if match_train_x:
                    self.train_x_initial = float(match_train_x.group(1))
                    print(f"Detected train initial X position: {self.train_x_initial}m")
                    
            except Exception as e:
                print(f"Error parsing Random filename: {e}, will use CSV data")
        
        # Try PID format: PID_A{angle}_BallX{ball_x}_TrainX{train_x}
        elif filename.startswith('PID_A'):
            try:
                # Extract angle
                match_angle = re.search(r'PID_A(\d+)', filename)
                if match_angle:
                    self.angle = float(match_angle.group(1))
                    print(f"Detected landing angle: {self.angle}°")
                
                # Extract ball X position
                match_ball_x = re.search(r'BallX(\d+)', filename)
                if match_ball_x:
                    self.ball_x_position = float(match_ball_x.group(1))
                    print(f"Detected ball X position: {self.ball_x_position}m")
                
                # Extract train initial X position
                match_train_x = re.search(r'TrainX(\d+)', filename)
                if match_train_x:
                    self.train_x_initial = float(match_train_x.group(1))
                    print(f"Detected train initial X position: {self.train_x_initial}m")
                    
            except Exception as e:
                print(f"Error parsing PID filename: {e}, will use CSV data")
        # Try old format: PID_Controller_Angle_{angle}
        elif 'Angle' in filename:
            try:
                angle_str = filename.split('Angle_')[-1]
                self.angle = float(angle_str)
                print(f"Detected landing angle: {self.angle}°")
                print(f"Will extract ball and train positions from CSV data (old format)")
            except:
                print("Could not parse angle from filename, using 0°")
        
        # Load data
        df = pd.read_csv(csv_file)
        self.time = df['time'].values
        self.train_pos = df['train_position'].values
        self.obj_pos = df['falling_object_position'].values
        self.force = df['applied_force'].values
        
        # Extract ball X position from CSV if not found in filename
        # The ball X position should be constant throughout simulation (ball falls vertically)
        # For new simulations, train_position represents horizontal X coordinate
        # For ball, we need to determine its X position from the simulation setup
        if self.ball_x_position is None:
            # The setpoint in the simulation is the target X position for the train
            # This corresponds to where the ball lands (ball X position)
            # We can infer it from the final train position or initial data
            # For now, use the maximum train position as an approximation
            self.ball_x_position = self.train_pos.max()
            print(f"Inferred ball X position from CSV: {self.ball_x_position:.1f}m")
        
        # Extract train initial X from CSV if not found in filename
        if self.train_x_initial is None:
            self.train_x_initial = self.train_pos[0]
            print(f"Extracted train initial X from CSV: {self.train_x_initial:.1f}m")
        
        # Store initial ball Y position if not already extracted from filename
        if not hasattr(self, 'ball_y_initial') or self.ball_y_initial is None:
            self.ball_y_initial = self.obj_pos[0]
            print(f"Ball initial Y position: {self.ball_y_initial:.1f}m")
        
        # Load new fields if available
        if 'train_velocity' in df.columns:
            self.velocity = df['train_velocity'].values
        else:
            # Calculate velocity from position
            self.velocity = np.gradient(self.train_pos, self.time)
        
        if 'train_acceleration' in df.columns:
            self.acceleration = df['train_acceleration'].values
        else:
            # Calculate acceleration from velocity
            self.acceleration = np.gradient(self.velocity, self.time)
        
        if 'error_derivative' in df.columns:
            self.error_derivative = df['error_derivative'].values
        else:
            # Calculate error and its derivative
            error = self.obj_pos - self.train_pos
            self.error_derivative = np.gradient(error, self.time)
        
        if 'error_integral' in df.columns:
            self.error_integral = df['error_integral'].values
        else:
            # Calculate cumulative error (trapezoidal integration)
            error = self.obj_pos - self.train_pos
            self.error_integral = np.cumsum((error[:-1] + error[1:]) / 2 * np.diff(self.time))
            self.error_integral = np.insert(self.error_integral, 0, 0.0)
        
        print(f"Loaded {len(self.time)} data points from {csv_file}")
    
    def create_realtime_animation(self, output_file=None, speed=1.0, fps=30):
        """Create real-time animation showing actual physical motion with 7 plots (Mark Misin style)"""
        
        # Setup figure with 4×3 grid (matching Mark Misin's layout)
        fig = plt.figure(figsize=(16, 9), dpi=100, facecolor=(0.8, 0.8, 0.8))
        fig.suptitle(f'Real-Time Simulation: {self.controller_name}', 
                     fontsize=16, fontweight='bold')
        
        # Create gridspec for 4×3 layout
        gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # Main physical animation (large, top-left: rows 0-2, cols 0-1)
        ax_physical = fig.add_subplot(gs[0:3, 0:2], facecolor=(0.9, 0.9, 0.9))
        
        # Right column plots (rows 0-2, col 2)
        ax_velocity = fig.add_subplot(gs[0, 2], facecolor=(0.9, 0.9, 0.9))
        ax_acceleration = fig.add_subplot(gs[1, 2], facecolor=(0.9, 0.9, 0.9))
        ax_force = fig.add_subplot(gs[2, 2], facecolor=(0.9, 0.9, 0.9))
        
        # Bottom row plots (row 3, cols 0-2)
        ax_error = fig.add_subplot(gs[3, 0], facecolor=(0.9, 0.9, 0.9))
        ax_error_derivative = fig.add_subplot(gs[3, 1], facecolor=(0.9, 0.9, 0.9))
        ax_error_integral = fig.add_subplot(gs[3, 2], facecolor=(0.9, 0.9, 0.9))
        
        # ========== Extract Position Data First ==========
        # Ball starting position - from filename or CSV data
        # train_pos contains the train's X position (horizontal)
        # obj_pos contains the ball's Y position (vertical height)
        obj_x_position = self.ball_x_position  # Ball falls at fixed X (extracted from filename or CSV)
        obj_y_initial = self.ball_y_initial  # Ball starts at this height (from CSV)
        
        # Calculate angle and Y position on inclined surface for the ball landing point
        angle_rad = np.deg2rad(self.angle)
        ball_landing_y = obj_x_position * np.tan(angle_rad)
        
        # Train starting and ending positions from actual simulation data
        train_x_initial = self.train_x_initial  # Train starts here (from filename or CSV)
        train_x_final = self.train_pos[-1]  # Train ends here (from CSV)
        
        # ========== Physical Space Setup (Main View) ==========
        # Calculate dynamic axis limits based on actual data
        max_x_data = max(self.train_pos.max(), obj_x_position)
        min_x_data = min(self.train_pos.min(), train_x_initial, 0)
        max_y_data = max(obj_y_initial, ball_landing_y)
        
        # Add margins for better visualization
        x_margin = (max_x_data - min_x_data) * 0.1 + 5
        y_margin = max_y_data * 0.1 + 5
        
        ax_physical.set_xlim(min_x_data - x_margin, max_x_data + x_margin)
        ax_physical.set_ylim(-5, max_y_data + y_margin)
        ax_physical.set_xlabel('Horizontal Position X (m)', fontweight='bold', fontsize=11)
        ax_physical.set_ylabel('Vertical Position Y (m)', fontweight='bold', fontsize=11)
        title_text = f'Physical Space: Train Intercepting Falling Ball (Angle: {self.angle}°)'
        ax_physical.set_title(title_text, fontweight='bold', fontsize=12)
        ax_physical.grid(True, alpha=0.3)
        
        # Create inclined landing surface - extends across the visible area
        x_surface = np.linspace(min_x_data - x_margin, max_x_data + x_margin, 100)
        # At x=0, y=0 (reference point)
        # For positive angle, surface rises to the right: y = x * tan(angle)
        y_surface = x_surface * np.tan(angle_rad)
        
        # Draw the inclined surface
        ax_physical.plot(x_surface, y_surface, color='brown', linewidth=4, 
                        linestyle='-', alpha=0.8, label=f'Landing Surface ({self.angle}°)')
        
        # Fill below surface
        ax_physical.fill_between(x_surface, y_surface - 5, y_surface, 
                                color='tan', alpha=0.3)
        
        # Add angle indicator at the left side
        if self.angle > 0:
            # Draw angle arc
            arc_x = np.linspace(0, 15, 50)
            arc_y_flat = np.zeros_like(arc_x)
            arc_y_incline = arc_x * np.tan(angle_rad)
            ax_physical.plot(arc_x, arc_y_flat, 'k--', linewidth=1, alpha=0.5)
            ax_physical.plot(arc_x, arc_y_incline, 'k--', linewidth=1, alpha=0.5)
            
            # Angle label
            label_x = 8
            label_y = label_x * np.tan(angle_rad) / 2
            ax_physical.text(label_x, label_y, f'{self.angle}°', 
                           fontsize=10, fontweight='bold', color='darkred',
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # Mark initial positions
        # Calculate initial train Y position on incline
        train_y_initial = train_x_initial * np.tan(angle_rad)
        
        ax_physical.scatter([obj_x_position], [obj_y_initial], c='red', s=100, 
                           marker='o', edgecolors='darkred', linewidths=2, 
                           alpha=0.5, label=f'Ball Start (X={obj_x_position:.0f}m, Y={obj_y_initial:.0f}m)', zorder=3)
        ax_physical.scatter([train_x_initial], [train_y_initial], 
                           c='blue', s=150, marker='s', edgecolors='darkblue', 
                           linewidths=2, alpha=0.5, label=f'Train Start (X={train_x_initial:.0f}m)', zorder=3)
        
        # Target marker - where ball will land
        ax_physical.axvline(x=obj_x_position, color='red', linewidth=2, linestyle='--', 
                           alpha=0.3)
        ax_physical.text(obj_x_position, obj_y_initial + 5, f'Ball Landing\nX={obj_x_position:.0f}m', 
                        ha='center', fontsize=9, color='red', fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        # Falling object (red circle falling vertically at fixed X)
        object_marker, = ax_physical.plot([], [], 'ro', markersize=20, 
                                         markeredgecolor='darkred', markeredgewidth=2,
                                         label='Falling Ball', zorder=5)
        object_trail, = ax_physical.plot([], [], 'r--', linewidth=2, alpha=0.4)
        
        # Train (blue square moving horizontally on track)
        train_marker, = ax_physical.plot([], [], 'bs', markersize=25, 
                                        markeredgecolor='darkblue', markeredgewidth=2,
                                        label='Train', zorder=5)
        train_trail, = ax_physical.plot([], [], 'b-', linewidth=3, alpha=0.5)
        
        # Distance line between object and train
        distance_line, = ax_physical.plot([], [], 'g--', linewidth=1.5, alpha=0.6)
        distance_text = ax_physical.text(0, 0, '', fontsize=9, color='green', 
                                        fontweight='bold', zorder=6)
        
        ax_physical.legend(loc='upper left', fontsize=8, ncol=2)
        
        # ========== Velocity vs Time Setup (Right column, top) ==========
        ax_velocity.set_xlim(0, self.time[-1])
        vel_margin = abs(self.velocity).max() * 0.1 + 0.1
        ax_velocity.set_ylim(self.velocity.min() - vel_margin, self.velocity.max() + vel_margin)
        ax_velocity.set_xlabel('Time (s)', fontsize=9)
        ax_velocity.set_ylabel('Velocity (m/s)', fontsize=9)
        ax_velocity.set_title('velocity on rails [m/s]', fontsize=10, fontweight='bold')
        ax_velocity.grid(True, alpha=0.3)
        ax_velocity.tick_params(labelsize=8)
        
        line_velocity, = ax_velocity.plot([], [], 'b-', linewidth=2, alpha=0.7)
        
        # ========== Acceleration vs Time Setup (Right column, middle) ==========
        ax_acceleration.set_xlim(0, self.time[-1])
        acc_margin = abs(self.acceleration).max() * 0.1 + 0.1
        ax_acceleration.set_ylim(self.acceleration.min() - acc_margin, self.acceleration.max() + acc_margin)
        ax_acceleration.set_xlabel('Time (s)', fontsize=9)
        ax_acceleration.set_ylabel('Accel. (m/s²)', fontsize=9)
        ax_acceleration.set_title('accel. on rails [m/s²] = F_net/m', fontsize=10, fontweight='bold')
        ax_acceleration.grid(True, alpha=0.3)
        ax_acceleration.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax_acceleration.tick_params(labelsize=8)
        
        line_acceleration, = ax_acceleration.plot([], [], 'b-', linewidth=2, alpha=0.7)
        
        # ========== Force vs Time Setup (Right column, bottom) ==========
        ax_force.set_xlim(0, self.time[-1])
        force_margin = abs(self.force).max() * 0.1 + 1
        ax_force.set_ylim(self.force.min() - force_margin, self.force.max() + force_margin)
        ax_force.set_xlabel('Time (s)', fontsize=9)
        ax_force.set_ylabel('Force (N)', fontsize=9)
        ax_force.set_title('Applied Control Force [N]', fontsize=10, fontweight='bold')
        ax_force.grid(True, alpha=0.3)
        ax_force.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax_force.tick_params(labelsize=8)
        
        line_force, = ax_force.plot([], [], 'g-', linewidth=2, alpha=0.7)
        
        # ========== Error vs Time Setup (Bottom row, left) ==========
        error = self.obj_pos - self.train_pos
        ax_error.set_xlim(0, self.time[-1])
        error_margin = abs(error).max() * 0.1 + 1
        ax_error.set_ylim(error.min() - error_margin, error.max() + error_margin)
        ax_error.set_xlabel('Time (s)', fontsize=9)
        ax_error.set_ylabel('Error (m)', fontsize=9)
        ax_error.set_title('horizontal error [m]', fontsize=10, fontweight='bold')
        ax_error.grid(True, alpha=0.3)
        ax_error.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax_error.tick_params(labelsize=8)
        
        line_error, = ax_error.plot([], [], 'b-', linewidth=2, alpha=0.7)
        
        # ========== Error Derivative vs Time Setup (Bottom row, middle) ==========
        ax_error_derivative.set_xlim(0, self.time[-1])
        ed_margin = abs(self.error_derivative).max() * 0.1 + 0.1
        ax_error_derivative.set_ylim(self.error_derivative.min() - ed_margin, 
                                     self.error_derivative.max() + ed_margin)
        ax_error_derivative.set_xlabel('Time (s)', fontsize=9)
        ax_error_derivative.set_ylabel('de/dt (m/s)', fontsize=9)
        ax_error_derivative.set_title('change of horiz. error [m/s]', fontsize=10, fontweight='bold')
        ax_error_derivative.grid(True, alpha=0.3)
        ax_error_derivative.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax_error_derivative.tick_params(labelsize=8)
        
        line_error_derivative, = ax_error_derivative.plot([], [], 'b-', linewidth=2, alpha=0.7)
        
        # ========== Error Integral vs Time Setup (Bottom row, right) ==========
        ax_error_integral.set_xlim(0, self.time[-1])
        ei_margin = abs(self.error_integral).max() * 0.1 + 0.1
        ax_error_integral.set_ylim(self.error_integral.min() - ei_margin, 
                                   self.error_integral.max() + ei_margin)
        ax_error_integral.set_xlabel('Time (s)', fontsize=9)
        ax_error_integral.set_ylabel('∫e dt (m·s)', fontsize=9)
        ax_error_integral.set_title('sum of horiz. error [m·s]', fontsize=10, fontweight='bold')
        ax_error_integral.grid(True, alpha=0.3)
        ax_error_integral.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax_error_integral.tick_params(labelsize=8)
        
        line_error_integral, = ax_error_integral.plot([], [], 'b-', linewidth=2, alpha=0.7)
        
        # Time display
        time_display = fig.text(0.5, 0.97, '', ha='center', fontsize=14, 
                               fontweight='bold', bbox=dict(boxstyle='round', 
                               facecolor='lightblue', alpha=0.8))
        
        # Calculate frame skip based on speed
        frame_skip = max(1, int(len(self.time) / (self.time[-1] * fps / speed)))
        frame_indices = list(range(0, len(self.time), frame_skip))
        
        # Find the frame where train reaches target X and ball lands (catches)
        catch_frame = None
        for idx in range(len(self.time)):
            train_x_current = self.train_pos[idx]
            obj_y_current = self.obj_pos[idx]
            
            # Calculate horizontal distance between train and ball landing position
            horizontal_distance = abs(train_x_current - obj_x_position)
            
            # Calculate vertical distance (ball Y position vs surface Y at landing point)
            vertical_distance = abs(obj_y_current - ball_landing_y)
            
            # Check if train is at target X and ball is close to surface
            if horizontal_distance < 2.0 and vertical_distance < 5.0:
                catch_frame = idx
                print(f"Ball caught at frame {idx}, time {self.time[idx]:.2f}s")
                print(f"  Train X: {train_x_current:.2f}m, Ball X: {obj_x_position:.2f}m")
                print(f"  Ball Y: {obj_y_current:.2f}m, Surface Y at X={obj_x_position}: {ball_landing_y:.2f}m")
                break
        
        # Limit frames to catch point if caught
        if catch_frame is not None:
            frame_indices = [f for f in frame_indices if f <= catch_frame]
            if catch_frame not in frame_indices:
                frame_indices.append(catch_frame)
            frame_indices.sort()
        
        print(f"Creating animation with {len(frame_indices)} frames at {fps} fps...")
        if catch_frame is not None:
            print(f"Animation will stop at catch point (t={self.time[catch_frame]:.2f}s)")
        
        def init():
            """Initialize animation"""
            line_velocity.set_data([], [])
            line_acceleration.set_data([], [])
            line_force.set_data([], [])
            line_error.set_data([], [])
            line_error_derivative.set_data([], [])
            line_error_integral.set_data([], [])
            object_marker.set_data([], [])
            train_marker.set_data([], [])
            object_trail.set_data([], [])
            train_trail.set_data([], [])
            distance_line.set_data([], [])
            distance_text.set_text('')
            time_display.set_text('')
        
        # Track if ball has been caught
        ball_caught_at_frame = None
        ball_caught_y = None
        
        def animate(frame_num):
            """Update animation for each frame"""
            nonlocal ball_caught_at_frame, ball_caught_y
            
            idx = frame_indices[frame_num]
            
            # Current values from simulation data
            t_now = self.time[idx]
            train_x_current = self.train_pos[idx]  # Train's actual X position from simulation
            obj_y_current = self.obj_pos[idx]  # Ball's Y height from simulation
            force_now = self.force[idx]
            
            # Calculate train's Y position on inclined surface
            train_y = train_x_current * np.tan(angle_rad)
            
            # Check if ball should be caught (lands on surface where train is)
            # Ball lands when it reaches the inclined surface at X=60m
            surface_y_at_ball_x = obj_x_position * np.tan(angle_rad)
            
            # If ball hasn't been caught yet, check catching conditions
            if ball_caught_at_frame is None:
                # Check if ball has reached the surface level
                if obj_y_current <= surface_y_at_ball_x + 1.0:  # Ball at or below surface
                    # Check if train is close enough to catch it
                    horizontal_dist = abs(train_x_current - obj_x_position)
                    if horizontal_dist < 3.0:  # Train is close enough (within 3m)
                        # CAUGHT! Ball stops at surface
                        ball_caught_at_frame = idx
                        ball_caught_y = surface_y_at_ball_x
                        print(f"✓ Ball CAUGHT at frame {idx}, time {t_now:.2f}s")
                        print(f"  Train position: X={train_x_current:.2f}m, Y={train_y:.2f}m")
                        print(f"  Ball stopped at: X={obj_x_position:.2f}m, Y={ball_caught_y:.2f}m")
                        print(f"  Horizontal distance: {horizontal_dist:.2f}m")
            
            # Determine ball's actual Y position for display
            if ball_caught_at_frame is not None:
                # Ball has been caught - keep it at the caught position
                ball_display_y = ball_caught_y
            else:
                # Ball is still falling
                ball_display_y = obj_y_current
                # If ball goes below surface without being caught, stop it at surface
                if ball_display_y < surface_y_at_ball_x:
                    ball_display_y = surface_y_at_ball_x
                    if ball_caught_at_frame is None:
                        print(f"✗ Ball MISSED - landed at surface without train (frame {idx}, t={t_now:.2f}s)")
                        print(f"  Train position: X={train_x_current:.2f}m (distance: {abs(train_x_current - obj_x_position):.2f}m)")
                        ball_caught_at_frame = idx  # Mark as landed (missed)
                        ball_caught_y = surface_y_at_ball_x
            
            # Error calculation (for time series plots)
            error_now = obj_y_current - train_x_current
            
            # Update time display
            time_display.set_text(f'Time: {t_now:.2f} s')
            
            # ========== Update Physical Space View ==========
            # Ball position: Use corrected Y position (stops when caught or lands)
            object_marker.set_data([obj_x_position], [ball_display_y])
            
            # Ball trail (last 50 points) - show actual path until caught
            trail_len = min(50, idx + 1)
            if trail_len > 1:
                trail_start = max(0, idx - trail_len + 1)
                # Build trail considering caught position
                trail_y_values = []
                for i in range(trail_start, idx + 1):
                    if ball_caught_at_frame is not None and i >= ball_caught_at_frame:
                        trail_y_values.append(ball_caught_y)
                    else:
                        y_val = self.obj_pos[i]
                        # Don't let trail go below surface
                        if y_val < surface_y_at_ball_x:
                            y_val = surface_y_at_ball_x
                        trail_y_values.append(y_val)
                object_trail.set_data([obj_x_position] * len(trail_y_values), trail_y_values)
            
            # Train position: Already calculated above (train_y)
            train_x = train_x_current
            
            train_marker.set_data([train_x], [train_y])
            
            # Train trail (shows movement along inclined surface)
            if trail_len > 1:
                trail_start = max(0, idx - trail_len + 1)
                trail_x = self.train_pos[trail_start:idx + 1]
                trail_y = trail_x * np.tan(angle_rad)
                train_trail.set_data(trail_x, trail_y)
            
            # Distance line between ball and train (use display Y for ball)
            distance_line.set_data([train_x, obj_x_position], [train_y, ball_display_y])
            mid_x = (train_x + obj_x_position) / 2
            mid_y = (train_y + ball_display_y) / 2
            
            # Calculate distances (using display position)
            horizontal_distance = abs(train_x - obj_x_position)
            vertical_distance = abs(ball_display_y - train_y)
            actual_distance = np.sqrt(horizontal_distance**2 + vertical_distance**2)
            
            distance_text.set_position((mid_x, mid_y))
            
            # Update visual feedback based on catching status
            if ball_caught_at_frame is not None and idx >= ball_caught_at_frame:
                # Ball has been caught/landed
                if abs(train_x - obj_x_position) < 3.0:  # Was close enough
                    distance_text.set_color('green')
                    distance_text.set_text(f'CAUGHT!\nH:{horizontal_distance:.1f}m V:{vertical_distance:.1f}m')
                    object_marker.set_markersize(30)
                    train_marker.set_markersize(35)
                else:
                    distance_text.set_color('red')
                    distance_text.set_text(f'MISSED!\nH:{horizontal_distance:.1f}m')
                    object_marker.set_markersize(25)
                    train_marker.set_markersize(25)
            else:
                # Ball still falling
                distance_text.set_color('orange')
                distance_text.set_text(f'H:{horizontal_distance:.1f}m V:{vertical_distance:.1f}m')
                object_marker.set_markersize(20)
                train_marker.set_markersize(25)
            
            # ========== Update Time Series Plots ==========
            # Velocity plot
            line_velocity.set_data(self.time[:idx + 1], self.velocity[:idx + 1])
            
            # Acceleration plot
            line_acceleration.set_data(self.time[:idx + 1], self.acceleration[:idx + 1])
            
            # Force plot
            line_force.set_data(self.time[:idx + 1], self.force[:idx + 1])
            
            # Error plot
            line_error.set_data(self.time[:idx + 1], error[:idx + 1])
            
            # Error derivative plot
            line_error_derivative.set_data(self.time[:idx + 1], self.error_derivative[:idx + 1])
            
            # Error integral plot
            line_error_integral.set_data(self.time[:idx + 1], self.error_integral[:idx + 1])
        
        # Create animation (blit=False for better compatibility with text elements)
        anim = FuncAnimation(fig, animate, init_func=init, 
                           frames=len(frame_indices),
                           interval=1000/fps, blit=False, repeat=False)  # repeat=False to stop at end
        
        # Save or display
        if output_file:
            try:
                writer = FFMpegWriter(fps=fps, bitrate=2000)
                anim.save(output_file, writer=writer)
                print(f"✓ Animation saved to {output_file}")
            except Exception as e:
                print(f"Error saving animation: {e}")
                print("Displaying animation instead (close window to continue)...")
                plt.show()
        else:
            print("Displaying animation (close window to continue)...")
            plt.show()
        
        plt.close()

def main():
    parser = argparse.ArgumentParser(description='Real-time animation for train tracking simulation')
    parser.add_argument('--file', type=str, default=None,
                       help='Specific CSV file to animate')
    parser.add_argument('--csv-dir', type=str, default='csv_data',
                       help='Directory containing CSV files')
    parser.add_argument('--output-dir', type=str, default='animations',
                       help='Output directory for animations')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Animation speed multiplier (default: 1.0)')
    parser.add_argument('--fps', type=int, default=30,
                       help='Frames per second (default: 30)')
    parser.add_argument('--display-only', action='store_true',
                       help='Display animation without saving')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Real-Time Train Tracking Animation")
    print("="*70)
    
    # Get CSV files
    if args.file:
        csv_files = [args.file]
    else:
        import glob
        csv_files = glob.glob(os.path.join(args.csv_dir, '*.csv'))
        if not csv_files:
            print(f"No CSV files found in {args.csv_dir}/")
            return
    
    print(f"\nFound {len(csv_files)} CSV file(s) to animate\n")
    
    for csv_file in sorted(csv_files):
        print(f"\n{'='*70}")
        print(f"Processing: {csv_file}")
        print('='*70)
        
        try:
            animator = RealtimeSimulationAnimation(csv_file)
            
            if args.display_only:
                output_file = None
            else:
                # Get controller type for subdirectory
                filename = Path(csv_file).stem.lower()
                if 'pid' in filename:
                    controller_type = 'PID'
                elif 'pd' in filename:
                    controller_type = 'PD'
                elif 'pi' in filename:
                    controller_type = 'PI'
                else:
                    controller_type = 'P'
                
                type_dir = os.path.join(args.output_dir, controller_type)
                os.makedirs(type_dir, exist_ok=True)
                output_file = os.path.join(type_dir, f"{Path(csv_file).stem}.mp4")
            
            animator.create_realtime_animation(output_file=output_file, 
                                              speed=args.speed, 
                                              fps=args.fps)
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not args.display_only:
        print("\n" + "="*70)
        print("✓ All animations complete!")
        print(f"  Output directory: {args.output_dir}/")
        print("="*70)

if __name__ == '__main__':
    main()
