C"""
Comprehensive analysis and visualization of random PID control scenarios
Creates plots showing all parameters and performance metrics
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import re

def parse_filename(filename):
    """Extract parameters from Random scenario filename"""
    match = re.search(r'Random_S(\d+)_A(\d+)_BallX(\d+)Y(\d+)_TrainX(\d+)', filename)
    if match:
        return {
            'scenario': int(match.group(1)),
            'angle': int(match.group(2)),
            'ball_x': int(match.group(3)),
            'ball_y': int(match.group(4)),
            'train_x': int(match.group(5))
        }
    return None

def load_scenario_data(csv_file):
    """Load and parse a single scenario CSV file"""
    df = pd.read_csv(csv_file)
    params = parse_filename(csv_file.name)
    
    return {
        'filename': csv_file.name,
        'params': params,
        'data': df,
        'time': df['time'].values,
        'train_pos': df['train_position'].values,
        'ball_pos': df['falling_object_position'].values,
        'force': df['applied_force'].values,
        'velocity': df['train_velocity'].values,
        'acceleration': df['train_acceleration'].values,
        'error_derivative': df['error_derivative'].values,
        'error_integral': df['error_integral'].values
    }

def calculate_metrics(scenario):
    """Calculate performance metrics for a scenario"""
    params = scenario['params']
    angle_rad = np.deg2rad(params['angle'])
    ball_x = params['ball_x']
    ball_landing_y = ball_x * np.tan(angle_rad)
    
    # Find catch point (when ball reaches surface and train is close)
    caught = False
    catch_time = None
    catch_distance = None
    
    for i, (t, train_x, ball_y) in enumerate(zip(scenario['time'], 
                                                   scenario['train_pos'], 
                                                   scenario['ball_pos'])):
        if ball_y <= ball_landing_y + 1.0:  # Ball at or near surface
            distance = abs(train_x - ball_x)
            if distance <= 3.0:  # Within catching range
                caught = True
                catch_time = t
                catch_distance = distance
                break
    
    # Calculate statistics
    max_velocity = np.max(np.abs(scenario['velocity']))
    max_acceleration = np.max(np.abs(scenario['acceleration']))
    max_force = np.max(np.abs(scenario['force']))
    mean_force = np.mean(np.abs(scenario['force']))
    
    return {
        'caught': caught,
        'catch_time': catch_time,
        'catch_distance': catch_distance,
        'max_velocity': max_velocity,
        'max_acceleration': max_acceleration,
        'max_force': max_force,
        'mean_force': mean_force,
        'initial_distance': ball_x - params['train_x']
    }

def create_individual_scenario_plots(scenario, metrics, output_dir):
    """Create detailed plots for a single scenario"""
    params = scenario['params']
    
    # Create 3x3 grid of plots
    fig = plt.figure(figsize=(20, 14))
    fig.suptitle(f"Scenario {params['scenario']}: Angle={params['angle']}°, "
                 f"Ball=({params['ball_x']}m, {params['ball_y']}m), "
                 f"Train Start={params['train_x']}m", 
                 fontsize=16, fontweight='bold')
    
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    time = scenario['time']
    
    # 1. Train Position
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(time, scenario['train_pos'], 'b-', linewidth=2, label='Train X Position')
    ax1.axhline(y=params['ball_x'], color='r', linestyle='--', alpha=0.5, label=f'Ball X ({params["ball_x"]}m)')
    ax1.set_xlabel('Time (s)', fontweight='bold')
    ax1.set_ylabel('Position (m)', fontweight='bold')
    ax1.set_title('Train Horizontal Position', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Ball Height
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(time, scenario['ball_pos'], 'r-', linewidth=2, label='Ball Height')
    angle_rad = np.deg2rad(params['angle'])
    landing_y = params['ball_x'] * np.tan(angle_rad)
    ax2.axhline(y=landing_y, color='brown', linestyle='--', alpha=0.5, label=f'Landing Surface ({landing_y:.1f}m)')
    ax2.set_xlabel('Time (s)', fontweight='bold')
    ax2.set_ylabel('Height (m)', fontweight='bold')
    ax2.set_title('Ball Vertical Position', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Horizontal Error
    ax3 = fig.add_subplot(gs[0, 2])
    error = params['ball_x'] - scenario['train_pos']
    ax3.plot(time, error, 'g-', linewidth=2)
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax3.set_xlabel('Time (s)', fontweight='bold')
    ax3.set_ylabel('Error (m)', fontweight='bold')
    ax3.set_title('Horizontal Position Error', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Velocity
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(time, scenario['velocity'], 'b-', linewidth=2)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax4.set_xlabel('Time (s)', fontweight='bold')
    ax4.set_ylabel('Velocity (m/s)', fontweight='bold')
    ax4.set_title(f'Train Velocity (Max: {metrics["max_velocity"]:.2f} m/s)', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Acceleration
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(time, scenario['acceleration'], 'c-', linewidth=2)
    ax5.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax5.set_xlabel('Time (s)', fontweight='bold')
    ax5.set_ylabel('Acceleration (m/s²)', fontweight='bold')
    ax5.set_title(f'Train Acceleration (Max: {metrics["max_acceleration"]:.2f} m/s²)', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. Applied Force
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(time, scenario['force'], 'm-', linewidth=2)
    ax6.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax6.set_xlabel('Time (s)', fontweight='bold')
    ax6.set_ylabel('Force (N)', fontweight='bold')
    ax6.set_title(f'Control Force (Max: {metrics["max_force"]:.1f} N)', fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. Error Derivative
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(time, scenario['error_derivative'], 'orange', linewidth=2)
    ax7.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax7.set_xlabel('Time (s)', fontweight='bold')
    ax7.set_ylabel('Error Derivative (m/s)', fontweight='bold')
    ax7.set_title('Error Rate of Change', fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    # 8. Error Integral
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(time, scenario['error_integral'], 'brown', linewidth=2)
    ax8.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax8.set_xlabel('Time (s)', fontweight='bold')
    ax8.set_ylabel('Error Integral (m·s)', fontweight='bold')
    ax8.set_title('Accumulated Error', fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    # 9. Performance Summary (text box)
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    
    summary_text = f"""
PERFORMANCE METRICS

Initial Setup:
  • Angle: {params['angle']}°
  • Ball Position: ({params['ball_x']}m, {params['ball_y']}m)
  • Train Start: {params['train_x']}m
  • Initial Distance: {metrics['initial_distance']:.1f}m

Results:
  • Status: {'✓ CAUGHT' if metrics['caught'] else '✗ MISSED'}
  • Catch Time: {f"{metrics['catch_time']:.2f}s" if metrics['caught'] else 'N/A'}
  • Final Distance: {f"{metrics['catch_distance']:.2f}m" if metrics['caught'] else 'N/A'}

Control Metrics:
  • Max Velocity: {metrics['max_velocity']:.2f} m/s
  • Max Acceleration: {metrics['max_acceleration']:.2f} m/s²
  • Max Force: {metrics['max_force']:.1f} N
  • Mean Force: {metrics['mean_force']:.1f} N
"""
    
    ax9.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center',
             fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Save figure
    output_file = output_dir / f"Scenario_{params['scenario']:02d}_Analysis.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: {output_file.name}")

def create_comparison_plots(scenarios, all_metrics, output_dir):
    """Create comparison plots across all scenarios"""
    
    # Extract data for comparison
    scenario_nums = [s['params']['scenario'] for s in scenarios]
    angles = [s['params']['angle'] for s in scenarios]
    ball_x = [s['params']['ball_x'] for s in scenarios]
    ball_y = [s['params']['ball_y'] for s in scenarios]
    train_x = [s['params']['train_x'] for s in scenarios]
    
    caught = [m['caught'] for m in all_metrics]
    catch_times = [m['catch_time'] if m['caught'] else None for m in all_metrics]
    max_velocities = [m['max_velocity'] for m in all_metrics]
    max_accelerations = [m['max_acceleration'] for m in all_metrics]
    max_forces = [m['max_force'] for m in all_metrics]
    initial_distances = [m['initial_distance'] for m in all_metrics]
    
    # Create comprehensive comparison figure
    fig = plt.figure(figsize=(22, 14))
    fig.suptitle('Comparison of All Random Scenarios', fontsize=18, fontweight='bold')
    
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3)
    
    # 1. Catch Success Rate
    ax1 = fig.add_subplot(gs[0, 0])
    colors = ['green' if c else 'red' for c in caught]
    bars = ax1.bar(scenario_nums, [1 if c else 0 for c in caught], color=colors, alpha=0.7)
    ax1.set_xlabel('Scenario', fontweight='bold')
    ax1.set_ylabel('Success', fontweight='bold')
    ax1.set_title(f'Catch Success ({sum(caught)}/{len(caught)} successful)', fontweight='bold')
    ax1.set_ylim([0, 1.2])
    ax1.set_xticks(scenario_nums)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. Angle Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    bars = ax2.bar(scenario_nums, angles, color='steelblue', alpha=0.7)
    ax2.set_xlabel('Scenario', fontweight='bold')
    ax2.set_ylabel('Angle (degrees)', fontweight='bold')
    ax2.set_title('Landing Surface Angles', fontweight='bold')
    ax2.set_xticks(scenario_nums)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Initial Distances
    ax3 = fig.add_subplot(gs[0, 2])
    bars = ax3.bar(scenario_nums, initial_distances, color='orange', alpha=0.7)
    ax3.set_xlabel('Scenario', fontweight='bold')
    ax3.set_ylabel('Distance (m)', fontweight='bold')
    ax3.set_title('Initial Train-to-Ball Distance', fontweight='bold')
    ax3.set_xticks(scenario_nums)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Catch Times
    ax4 = fig.add_subplot(gs[0, 3])
    catch_times_plot = [ct if ct is not None else 0 for ct in catch_times]
    colors = ['green' if c else 'lightgray' for c in caught]
    bars = ax4.bar(scenario_nums, catch_times_plot, color=colors, alpha=0.7)
    ax4.set_xlabel('Scenario', fontweight='bold')
    ax4.set_ylabel('Time (s)', fontweight='bold')
    ax4.set_title('Time to Catch', fontweight='bold')
    ax4.set_xticks(scenario_nums)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Max Velocities
    ax5 = fig.add_subplot(gs[1, 0])
    bars = ax5.bar(scenario_nums, max_velocities, color='blue', alpha=0.7)
    ax5.set_xlabel('Scenario', fontweight='bold')
    ax5.set_ylabel('Velocity (m/s)', fontweight='bold')
    ax5.set_title('Maximum Train Velocity', fontweight='bold')
    ax5.set_xticks(scenario_nums)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Max Accelerations
    ax6 = fig.add_subplot(gs[1, 1])
    bars = ax6.bar(scenario_nums, max_accelerations, color='cyan', alpha=0.7)
    ax6.set_xlabel('Scenario', fontweight='bold')
    ax6.set_ylabel('Acceleration (m/s²)', fontweight='bold')
    ax6.set_title('Maximum Train Acceleration', fontweight='bold')
    ax6.set_xticks(scenario_nums)
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. Max Forces
    ax7 = fig.add_subplot(gs[1, 2])
    bars = ax7.bar(scenario_nums, max_forces, color='magenta', alpha=0.7)
    ax7.set_xlabel('Scenario', fontweight='bold')
    ax7.set_ylabel('Force (N)', fontweight='bold')
    ax7.set_title('Maximum Control Force', fontweight='bold')
    ax7.set_xticks(scenario_nums)
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 8. Ball Initial Heights
    ax8 = fig.add_subplot(gs[1, 3])
    bars = ax8.bar(scenario_nums, ball_y, color='red', alpha=0.7)
    ax8.set_xlabel('Scenario', fontweight='bold')
    ax8.set_ylabel('Height (m)', fontweight='bold')
    ax8.set_title('Ball Initial Height', fontweight='bold')
    ax8.set_xticks(scenario_nums)
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 9. Angle vs Catch Success (scatter)
    ax9 = fig.add_subplot(gs[2, 0])
    colors_scatter = ['green' if c else 'red' for c in caught]
    ax9.scatter(angles, initial_distances, c=colors_scatter, s=150, alpha=0.7, edgecolors='black')
    ax9.set_xlabel('Surface Angle (degrees)', fontweight='bold')
    ax9.set_ylabel('Initial Distance (m)', fontweight='bold')
    ax9.set_title('Angle vs Distance (Green=Caught)', fontweight='bold')
    ax9.grid(True, alpha=0.3)
    
    # 10. Ball Height vs X Position
    ax10 = fig.add_subplot(gs[2, 1])
    colors_scatter = ['green' if c else 'red' for c in caught]
    ax10.scatter(ball_x, ball_y, c=colors_scatter, s=150, alpha=0.7, edgecolors='black')
    ax10.set_xlabel('Ball X Position (m)', fontweight='bold')
    ax10.set_ylabel('Ball Initial Height (m)', fontweight='bold')
    ax10.set_title('Ball Position Distribution', fontweight='bold')
    ax10.grid(True, alpha=0.3)
    
    # 11. Force vs Angle
    ax11 = fig.add_subplot(gs[2, 2])
    ax11.scatter(angles, max_forces, c='purple', s=150, alpha=0.7, edgecolors='black')
    ax11.set_xlabel('Surface Angle (degrees)', fontweight='bold')
    ax11.set_ylabel('Max Force (N)', fontweight='bold')
    ax11.set_title('Force Required vs Angle', fontweight='bold')
    ax11.grid(True, alpha=0.3)
    
    # 12. Summary Statistics Table
    ax12 = fig.add_subplot(gs[2, 3])
    ax12.axis('off')
    
    success_rate = sum(caught) / len(caught) * 100
    avg_catch_time = np.mean([ct for ct in catch_times if ct is not None]) if any(caught) else 0
    avg_velocity = np.mean(max_velocities)
    avg_acceleration = np.mean(max_accelerations)
    avg_force = np.mean(max_forces)
    
    summary_text = f"""
OVERALL STATISTICS

Success Rate: {success_rate:.1f}%
  ({sum(caught)} out of {len(caught)} caught)

Average Metrics (Successful):
  • Catch Time: {avg_catch_time:.2f}s
  • Max Velocity: {avg_velocity:.2f} m/s
  • Max Accel: {avg_acceleration:.2f} m/s²
  • Max Force: {avg_force:.1f} N

Angle Range: {min(angles)}° - {max(angles)}°
Distance Range: {min(initial_distances):.1f}m - {max(initial_distances):.1f}m
Ball Height Range: {min(ball_y)}m - {max(ball_y)}m
"""
    
    ax12.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
             fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    # Save comparison figure
    output_file = output_dir / "All_Scenarios_Comparison.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✓ Created comprehensive comparison: {output_file.name}")

def create_trajectory_overlay(scenarios, output_dir):
    """Create overlaid trajectories for all scenarios"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    fig.suptitle('Trajectory Overlay - All Scenarios', fontsize=16, fontweight='bold')
    
    # Color map for scenarios
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    # Plot 1: Train positions over time
    for i, scenario in enumerate(scenarios):
        params = scenario['params']
        ax1.plot(scenario['time'], scenario['train_pos'], 
                linewidth=2, alpha=0.7, color=colors[i],
                label=f"S{params['scenario']}: {params['angle']}°")
    
    ax1.set_xlabel('Time (s)', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Train Position (m)', fontweight='bold', fontsize=12)
    ax1.set_title('Train Position Trajectories', fontweight='bold', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=9)
    
    # Plot 2: Ball heights over time
    for i, scenario in enumerate(scenarios):
        params = scenario['params']
        ax2.plot(scenario['time'], scenario['ball_pos'], 
                linewidth=2, alpha=0.7, color=colors[i],
                label=f"S{params['scenario']}: Y₀={params['ball_y']}m")
    
    ax2.set_xlabel('Time (s)', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Ball Height (m)', fontweight='bold', fontsize=12)
    ax2.set_title('Ball Height Trajectories', fontweight='bold', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=9)
    
    # Save overlay figure
    output_file = output_dir / "Trajectories_Overlay.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created trajectory overlay: {output_file.name}")

def main():
    """Main analysis workflow"""
    print("="*80)
    print("COMPREHENSIVE ANALYSIS OF RANDOM PID SCENARIOS")
    print("="*80)
    print()
    
    # Find all random scenario CSV files
    csv_dir = Path('csv_data')
    csv_files = sorted(csv_dir.glob('Random_*.csv'))
    
    if not csv_files:
        print("❌ No random scenario CSV files found!")
        return
    
    print(f"Found {len(csv_files)} random scenario files\n")
    
    # Create output directory
    output_dir = Path('analysis_plots')
    output_dir.mkdir(exist_ok=True)
    
    # Load all scenarios
    print("Loading scenarios...")
    scenarios = []
    all_metrics = []
    
    for csv_file in csv_files:
        scenario = load_scenario_data(csv_file)
        metrics = calculate_metrics(scenario)
        scenarios.append(scenario)
        all_metrics.append(metrics)
        
        status = "✓ CAUGHT" if metrics['caught'] else "✗ MISSED"
        print(f"  Scenario {scenario['params']['scenario']:2d}: "
              f"Angle={scenario['params']['angle']:2d}°, "
              f"Ball=({scenario['params']['ball_x']:3d}m, {scenario['params']['ball_y']:3d}m), "
              f"Train={scenario['params']['train_x']:3d}m → {status}")
    
    # Create individual scenario plots
    print(f"\n{'='*80}")
    print("Creating individual scenario plots...")
    print('='*80)
    for scenario, metrics in zip(scenarios, all_metrics):
        create_individual_scenario_plots(scenario, metrics, output_dir)
    
    # Create comparison plots
    print(f"\n{'='*80}")
    print("Creating comparison plots...")
    print('='*80)
    create_comparison_plots(scenarios, all_metrics, output_dir)
    
    # Create trajectory overlays
    print(f"\n{'='*80}")
    print("Creating trajectory overlays...")
    print('='*80)
    create_trajectory_overlay(scenarios, output_dir)
    
    # Print summary
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print('='*80)
    print(f"✓ Generated {len(csv_files) + 2} plot files")
    print(f"  - {len(csv_files)} individual scenario analyses")
    print(f"  - 1 comprehensive comparison")
    print(f"  - 1 trajectory overlay")
    print(f"\nOutput directory: {output_dir}/")
    print('='*80)

if __name__ == "__main__":
    main()
