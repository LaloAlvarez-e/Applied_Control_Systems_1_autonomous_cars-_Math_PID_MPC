"""
Generate 10 random PID control scenarios with varied initial conditions
"""
import numpy as np
import pandas as pd
import random
from pathlib import Path

# Constants
g = 9.81  # gravity (m/s^2)
dt = 0.02  # time step (s) - 50Hz
simulation_time = 40.0  # seconds

# PID gains (tuned for the system)
Kp = 45.0
Ki = 0.5
Kd = 25.0

# System parameters
m = 10.0  # train mass (kg)
mu = 0.1  # friction coefficient

def simulate_scenario(angle_deg, ball_x, ball_y_initial, train_x_initial, scenario_num):
    """
    Simulate one PID control scenario
    
    Args:
        angle_deg: Landing surface angle in degrees (0-45)
        ball_x: Ball's fixed X position where it falls (m)
        ball_y_initial: Ball's initial height (m)
        train_x_initial: Train's initial X position on the incline (m)
        scenario_num: Scenario number for filename
    """
    angle_rad = np.deg2rad(angle_deg)
    
    # Calculate train's initial Y position (on the inclined surface)
    train_y_initial = train_x_initial * np.tan(angle_rad)
    
    # Time array
    num_steps = int(simulation_time / dt)
    time_array = np.arange(0, num_steps) * dt
    
    # Initialize arrays
    train_position = np.zeros(num_steps)
    train_velocity = np.zeros(num_steps)
    train_acceleration = np.zeros(num_steps)
    ball_position = np.zeros(num_steps)  # Ball Y position (height)
    applied_force = np.zeros(num_steps)
    error_values = np.zeros(num_steps)
    error_derivative_values = np.zeros(num_steps)
    error_integral_values = np.zeros(num_steps)
    
    # Initial conditions
    train_position[0] = train_x_initial
    train_velocity[0] = 0.0
    ball_position[0] = ball_y_initial
    
    # PID state
    error_integral = 0.0
    previous_error = ball_x - train_position[0]
    
    # Simulation loop
    for i in range(num_steps):
        # Ball falls with gravity
        ball_position[i] = ball_y_initial - 0.5 * g * (time_array[i] ** 2)
        
        # Stop ball if it reaches the ground at its X position
        ball_landing_y = ball_x * np.tan(angle_rad)
        if ball_position[i] <= ball_landing_y:
            ball_position[i] = ball_landing_y
        
        # Calculate error (horizontal distance)
        current_error = ball_x - train_position[i]
        error_values[i] = current_error
        
        # PID control
        error_integral += current_error * dt
        error_derivative = (current_error - previous_error) / dt
        
        error_derivative_values[i] = error_derivative
        error_integral_values[i] = error_integral
        
        # Control force
        F_control = Kp * current_error + Ki * error_integral + Kd * error_derivative
        
        # Physics: Forces on incline
        # Normal force: N = m*g*cos(angle)
        N = m * g * np.cos(angle_rad)
        
        # Friction force (opposes motion)
        if train_velocity[i] > 0.01:
            F_friction = -mu * N
        elif train_velocity[i] < -0.01:
            F_friction = mu * N
        else:
            F_friction = 0.0
        
        # Gravity component along incline (down the slope)
        F_gravity = -m * g * np.sin(angle_rad)
        
        # Net force
        F_net = F_control + F_friction + F_gravity
        applied_force[i] = F_control
        
        # Acceleration
        acceleration = F_net / m
        train_acceleration[i] = acceleration
        
        # Update velocity and position for next step
        if i < num_steps - 1:
            train_velocity[i + 1] = train_velocity[i] + acceleration * dt
            train_position[i + 1] = train_position[i] + train_velocity[i + 1] * dt
            
            # Keep train on the surface (X >= 0)
            if train_position[i + 1] < 0:
                train_position[i + 1] = 0
                train_velocity[i + 1] = 0
        
        previous_error = current_error
    
    # Create DataFrame
    df = pd.DataFrame({
        'time': time_array,
        'train_position': train_position,
        'falling_object_position': ball_position,
        'applied_force': applied_force,
        'train_velocity': train_velocity,
        'train_acceleration': train_acceleration,
        'error_derivative': error_derivative_values,
        'error_integral': error_integral_values
    })
    
    # Save to CSV
    output_dir = Path('csv_data')
    output_dir.mkdir(exist_ok=True)
    
    filename = f'Random_S{scenario_num:02d}_A{int(angle_deg):02d}_BallX{int(ball_x):03d}Y{int(ball_y_initial):03d}_TrainX{int(train_x_initial):03d}.csv'
    output_path = output_dir / filename
    
    df.to_csv(output_path, index=False)
    
    print(f"✓ Generated: {filename}")
    print(f"  Angle: {angle_deg:.1f}°, Ball: ({ball_x:.1f}m, {ball_y_initial:.1f}m), Train start: {train_x_initial:.1f}m")
    
    return output_path

def main():
    """Generate 10 random scenarios"""
    print("="*70)
    print("Generating 10 Random PID Control Scenarios")
    print("="*70)
    print()
    
    random.seed(42)  # For reproducibility
    np.random.seed(42)
    
    scenarios = []
    
    for i in range(10):
        # Random angle: 0° to 45°
        angle = random.uniform(0, 45)
        
        # Random ball X position: 20m to 100m
        ball_x = random.uniform(20, 100)
        
        # Random ball initial height: 30m to 100m
        ball_y_initial = random.uniform(30, 100)
        
        # Random train initial X: 0m to (ball_x - 20m) to ensure some distance
        max_train_x = max(0, ball_x - 20)
        train_x_initial = random.uniform(0, max_train_x)
        
        print(f"\n[Scenario {i+1}/10]")
        output_path = simulate_scenario(angle, ball_x, ball_y_initial, train_x_initial, i+1)
        scenarios.append(output_path)
    
    print()
    print("="*70)
    print(f"✓ Successfully generated {len(scenarios)} scenario files")
    print(f"  Output directory: csv_data/")
    print("="*70)

if __name__ == "__main__":
    main()
