#!/usr/bin/env python3
"""
Angle Comparison Visualization
Generates plots comparing train performance across different landing surface angles.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

def load_angle_data():
    """Load simulation data for all angles"""
    angles = [0, 10, 15, 22, 30, 36, 45, 64, 77, 85]
    data_dict = {}
    
    csv_dir = Path(__file__).parent.parent / "csv_data"
    
    for angle in angles:
        filename = csv_dir / f"PID_Controller_Angle_{angle:02d}.csv"
        if filename.exists():
            df = pd.read_csv(filename)
            # Rename columns for consistency
            df.columns = ['time', 'train_x', 'ball_y', 'force']
            data_dict[angle] = df
            print(f"Loaded: {filename.name} ({len(df)} points)")
        else:
            print(f"Warning: {filename.name} not found")
    
    return data_dict, angles

def create_angle_comparison_plot(data_dict, angles):
    """Create comprehensive angle comparison plot"""
    fig = plt.figure(figsize=(20, 12))
    
    # Define colors for different angle ranges
    colors = plt.cm.viridis(np.linspace(0, 1, len(angles)))
    
    # 1. Train Position Trajectories
    ax1 = plt.subplot(3, 3, 1)
    for idx, angle in enumerate(angles):
        if angle in data_dict:
            df = data_dict[angle]
            ax1.plot(df['time'], df['train_x'], 
                    label=f'{angle}°', color=colors[idx], alpha=0.7, linewidth=2)
    ax1.axhline(y=60, color='r', linestyle='--', linewidth=2, label='Target (60m)')
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Train X Position (m)', fontsize=12)
    ax1.set_title('Train Horizontal Position vs Time', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    
    # 2. Control Force Comparison
    ax2 = plt.subplot(3, 3, 2)
    for idx, angle in enumerate(angles):
        if angle in data_dict:
            df = data_dict[angle]
            ax2.plot(df['time'], df['force'], 
                    label=f'{angle}°', color=colors[idx], alpha=0.7, linewidth=2)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Control Force (N)', fontsize=12)
    ax2.set_title('Control Force vs Time', fontsize=14, fontweight='bold')
    ax2.legend(loc='best', fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)
    
    # 3. Final Position vs Angle
    ax3 = plt.subplot(3, 3, 3)
    final_positions = []
    final_errors = []
    for angle in angles:
        if angle in data_dict:
            df = data_dict[angle]
            final_pos = df['train_x'].iloc[-1]
            final_positions.append(final_pos)
            final_errors.append(abs(60 - final_pos))
        else:
            final_positions.append(np.nan)
            final_errors.append(np.nan)
    
    ax3.bar(angles, final_positions, color=colors, alpha=0.7, edgecolor='black')
    ax3.axhline(y=60, color='r', linestyle='--', linewidth=2, label='Target (60m)')
    ax3.set_xlabel('Landing Angle (degrees)', fontsize=12)
    ax3.set_ylabel('Final Train Position (m)', fontsize=12)
    ax3.set_title('Final Position vs Landing Angle', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Tracking Error vs Angle
    ax4 = plt.subplot(3, 3, 4)
    ax4.bar(angles, final_errors, color='red', alpha=0.6, edgecolor='black')
    ax4.set_xlabel('Landing Angle (degrees)', fontsize=12)
    ax4.set_ylabel('Final Position Error (m)', fontsize=12)
    ax4.set_title('Steady-State Error vs Landing Angle', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Response Time (time to reach 95% of target)
    ax5 = plt.subplot(3, 3, 5)
    response_times = []
    target = 60.0
    threshold = 0.95 * target  # 95% of target
    
    for angle in angles:
        if angle in data_dict:
            df = data_dict[angle]
            # Find first time train reaches 95% of target
            idx = np.where(df['train_x'] >= threshold)[0]
            if len(idx) > 0:
                response_time = df['time'].iloc[idx[0]]
                response_times.append(response_time)
            else:
                response_times.append(np.nan)
        else:
            response_times.append(np.nan)
    
    ax5.plot(angles, response_times, 'o-', color='green', markersize=10, linewidth=2)
    ax5.set_xlabel('Landing Angle (degrees)', fontsize=12)
    ax5.set_ylabel('Response Time (s)', fontsize=12)
    ax5.set_title('Time to Reach 95% of Target', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. Maximum Force vs Angle
    ax6 = plt.subplot(3, 3, 6)
    max_forces = []
    for angle in angles:
        if angle in data_dict:
            df = data_dict[angle]
            max_forces.append(df['force'].max())
        else:
            max_forces.append(np.nan)
    
    ax6.bar(angles, max_forces, color='orange', alpha=0.7, edgecolor='black')
    ax6.set_xlabel('Landing Angle (degrees)', fontsize=12)
    ax6.set_ylabel('Max Control Force (N)', fontsize=12)
    ax6.set_title('Peak Force vs Landing Angle', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. 2D Physical Space - Multiple Angles
    ax7 = plt.subplot(3, 3, 7)
    ball_x = 60  # Ball lands at X=60m
    
    # Draw ball trajectory (vertical fall)
    ball_heights = np.linspace(100, 0, 100)
    ax7.plot([ball_x] * len(ball_heights), ball_heights, 'r--', linewidth=3, label='Ball Fall', alpha=0.8)
    ax7.plot(ball_x, 100, 'ro', markersize=12, label='Ball Start')
    ax7.plot(ball_x, 0, 'rv', markersize=12, label='Ball Land')
    
    # Draw train paths for selected angles
    selected_angles = [0, 22, 45, 77, 85]
    selected_colors = plt.cm.plasma(np.linspace(0, 1, len(selected_angles)))
    
    for idx, angle in enumerate(selected_angles):
        if angle in data_dict:
            df = data_dict[angle]
            # Sample every 10th point for clarity
            sample_x = df['train_x'].iloc[::10]
            sample_y = [0] * len(sample_x)  # Train on ground
            ax7.plot(sample_x, sample_y, '-', color=selected_colors[idx], 
                    linewidth=2, alpha=0.7, label=f'Train {angle}°')
            # Mark start and end
            ax7.plot(df['train_x'].iloc[0], 0, 'o', color=selected_colors[idx], markersize=8)
            ax7.plot(df['train_x'].iloc[-1], 0, 's', color=selected_colors[idx], markersize=8)
    
    ax7.axhline(y=0, color='brown', linewidth=3, linestyle='-', alpha=0.5, label='Ground')
    ax7.set_xlabel('Horizontal Position X (m)', fontsize=12)
    ax7.set_ylabel('Vertical Position Y (m)', fontsize=12)
    ax7.set_title('2D Physical Space View', fontsize=14, fontweight='bold')
    ax7.legend(fontsize=8)
    ax7.grid(True, alpha=0.3)
    ax7.set_ylim(-10, 110)
    
    # 8. Velocity Analysis (numerical derivative)
    ax8 = plt.subplot(3, 3, 8)
    for idx, angle in enumerate([0, 22, 45, 77, 85]):
        if angle in data_dict:
            df = data_dict[angle]
            velocity = np.gradient(df['train_x'], df['time'])
            ax8.plot(df['time'], velocity, label=f'{angle}°', 
                    color=selected_colors[idx], alpha=0.7, linewidth=2)
    ax8.set_xlabel('Time (s)', fontsize=12)
    ax8.set_ylabel('Train Velocity (m/s)', fontsize=12)
    ax8.set_title('Horizontal Velocity vs Time', fontsize=14, fontweight='bold')
    ax8.legend(fontsize=8)
    ax8.grid(True, alpha=0.3)
    
    # 9. Performance Metrics Table
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    table_data = []
    table_data.append(['Angle', 'Final Pos', 'Error', 'Response', 'Max Force'])
    table_data.append(['(deg)', '(m)', '(m)', 'Time (s)', '(N)'])
    
    for idx, angle in enumerate(angles):
        if angle in data_dict:
            final_pos = final_positions[idx]
            error = final_errors[idx]
            resp_time = response_times[idx]
            max_force = max_forces[idx]
            
            table_data.append([
                f"{angle}°",
                f"{final_pos:.2f}",
                f"{error:.2f}",
                f"{resp_time:.2f}" if not np.isnan(resp_time) else "N/A",
                f"{max_force:.2f}"
            ])
    
    table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15, 0.15, 0.15, 0.15, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Color header rows
    for i in range(2):
        for j in range(5):
            table[(i, j)].set_facecolor('#40466e')
            table[(i, j)].set_text_props(weight='bold', color='white')
    
    ax9.set_title('Performance Metrics Summary', fontsize=14, fontweight='bold', pad=20)
    
    plt.suptitle('Landing Angle Comparison - PID Controller Performance', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # Save plot
    output_dir = Path("plots/angles")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "angle_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Angle comparison plot saved: {output_file}")
    
    plt.close()

def create_individual_angle_plots(data_dict, angles):
    """Create individual detail plots for each angle"""
    output_dir = Path("plots/angles/individual")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for angle in angles:
        if angle not in data_dict:
            continue
            
        df = data_dict[angle]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Landing Angle: {angle}° - Detailed Analysis', 
                    fontsize=16, fontweight='bold')
        
        # Position
        axes[0, 0].plot(df['time'], df['train_x'], 'b-', linewidth=2, label='Train X')
        axes[0, 0].plot(df['time'], df['ball_y'], 'r--', linewidth=2, label='Ball Y')
        axes[0, 0].axhline(y=60, color='g', linestyle=':', linewidth=2, label='Target X=60m')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Position (m)')
        axes[0, 0].set_title('Position vs Time')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Force
        axes[0, 1].plot(df['time'], df['force'], 'g-', linewidth=2)
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Control Force (N)')
        axes[0, 1].set_title('Control Force vs Time')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Error
        error = 60 - df['train_x']
        axes[1, 0].plot(df['time'], error, 'r-', linewidth=2)
        axes[1, 0].axhline(y=0, color='k', linestyle='--', linewidth=1)
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Position Error (m)')
        axes[1, 0].set_title('Tracking Error (Target - Train X)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 2D Space
        ball_x = 60
        ball_heights = df['ball_y']
        axes[1, 1].plot([ball_x] * len(ball_heights), ball_heights, 'r--', linewidth=2, label='Ball Fall')
        axes[1, 1].plot(df['train_x'], [0] * len(df), 'b-', linewidth=2, label='Train Path')
        axes[1, 1].plot(ball_x, 100, 'ro', markersize=12, label='Ball Start')
        axes[1, 1].plot(ball_x, 0, 'rv', markersize=12, label='Ball Land')
        axes[1, 1].plot(df['train_x'].iloc[0], 0, 'bs', markersize=10, label='Train Start')
        axes[1, 1].plot(df['train_x'].iloc[-1], 0, 'gs', markersize=10, label='Train End')
        
        # Draw landing surface with angle
        angle_rad = np.radians(angle)
        x_range = np.linspace(0, 100, 100)
        
        if angle == 0:
            y_surface = np.zeros_like(x_range)
            surface_label = 'Ground (0°)'
        else:
            y_surface = x_range * np.tan(angle_rad)
            surface_label = f'Surface ({angle:.0f}°)'
        
        axes[1, 1].plot(x_range, y_surface, color='brown', linewidth=3, alpha=0.7, label=surface_label)
        axes[1, 1].fill_between(x_range, y_surface, -10, color='saddlebrown', alpha=0.2)
        
        axes[1, 1].set_xlabel('Horizontal Position X (m)')
        axes[1, 1].set_ylabel('Vertical Position Y (m)')
        axes[1, 1].set_title(f'2D Physical Space (Angle: {angle:.0f}°)')
        axes[1, 1].legend(fontsize=8)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_ylim(-10, max(110, np.max(y_surface) + 10))
        axes[1, 1].set_aspect('equal', adjustable='box')
        
        plt.tight_layout()
        
        output_file = output_dir / f"angle_{angle:02d}_detail.png"
        plt.savefig(output_file, dpi=200, bbox_inches='tight')
        print(f"✓ Saved: {output_file.name}")
        plt.close()

def main():
    """Main function"""
    print("=" * 70)
    print("Landing Angle Comparison Visualization")
    print("=" * 70)
    print()
    
    # Load data
    print("Loading simulation data...")
    data_dict, angles = load_angle_data()
    print(f"\n✓ Loaded data for {len(data_dict)} angles\n")
    
    if not data_dict:
        print("Error: No data found!")
        return
    
    # Create comparison plot
    print("Creating angle comparison plot...")
    create_angle_comparison_plot(data_dict, angles)
    
    # Create individual plots
    print("\nCreating individual angle plots...")
    create_individual_angle_plots(data_dict, angles)
    
    print("\n" + "=" * 70)
    print("✓ All visualizations complete!")
    print("=" * 70)
    print(f"\nOutput locations:")
    print(f"  - Comparison: plots/angles/angle_comparison.png")
    print(f"  - Individual: plots/angles/individual/")
    print()

if __name__ == "__main__":
    main()
