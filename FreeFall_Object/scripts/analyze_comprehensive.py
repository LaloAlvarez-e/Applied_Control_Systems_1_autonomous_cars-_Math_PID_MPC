"""
Comprehensive Analysis of Multi-Parameter PID Simulation
Analyzes 550+ simulations across angles, ball positions, and train starting positions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path

print("=" * 70)
print("Comprehensive PID Performance Analysis")
print("=" * 70)
print("\nAnalyzing multi-parameter simulation results...")
print("Parameters: Angles × Ball X positions × Train initial X positions\n")

# Get all CSV files (from FreeFall_Object root)
csv_dir = Path(__file__).parent.parent / "csv_data"
csv_files = list(csv_dir.glob("PID_A*.csv"))

print(f"Found {len(csv_files)} simulation files\n")

# Physics constants
g = 9.81  # Gravity
ball_y_initial = 100.0  # Ball starts at 100m height

# Parse all simulation data
results = []

print("Processing files...")
for i, csv_file in enumerate(csv_files):
    # Show progress
    if (i + 1) % 50 == 0:
        print(f"  Processed {i + 1}/{len(csv_files)} files...", end='\r')
    
    # Parse filename: PID_A{angle}_BallX{ball_x}_TrainX{train_x}.csv
    match = re.match(r'PID_A(\d+)_BallX(\d+)_TrainX(\d+)\.csv', csv_file.name)
    if not match:
        continue
    
    angle = float(match.group(1))
    ball_x = float(match.group(2))
    train_x_initial = float(match.group(3))
    
    # Load data
    try:
        df = pd.read_csv(csv_file)
        # Handle both old (4 columns) and new (8 columns) CSV formats
        if len(df.columns) == 4:
            df.columns = ['time', 'train_x', 'ball_y', 'force']
        else:
            # New format with 8 columns - only use the ones we need
            df = df[['time', 'train_position', 'falling_object_position', 'applied_force']]
            df.columns = ['time', 'train_x', 'ball_y', 'force']
        
        # Calculate ball landing position on inclined surface
        angle_rad = np.radians(angle)
        ball_landing_y = ball_x * np.tan(angle_rad)
        
        # Find when ball lands (ball_y <= ball_landing_y)
        ball_landed_idx = np.where(df['ball_y'].values <= ball_landing_y)[0]
        if len(ball_landed_idx) > 0:
            ball_landing_time = df['time'].values[ball_landed_idx[0]]
        else:
            ball_landing_time = None
        
        # Find when train reaches target (within 2m)
        train_at_target = df[np.abs(df['train_x'] - ball_x) <= 2.0]
        if len(train_at_target) > 0:
            train_arrival_time = train_at_target['time'].values[0]
        else:
            train_arrival_time = None
        
        # Calculate metrics
        distance_to_travel = ball_x - train_x_initial
        max_train_x = df['train_x'].max()
        max_force = df['force'].abs().max()
        
        # Determine if catch occurred
        if train_arrival_time is not None and ball_landing_time is not None:
            caught = train_arrival_time <= ball_landing_time
            time_margin = ball_landing_time - train_arrival_time if caught else None
        else:
            caught = False
            time_margin = None
        
        results.append({
            'angle': angle,
            'ball_x': ball_x,
            'train_x_initial': train_x_initial,
            'distance_to_travel': distance_to_travel,
            'train_arrival_time': train_arrival_time,
            'ball_landing_time': ball_landing_time,
            'caught': caught,
            'time_margin': time_margin,
            'max_train_x': max_train_x,
            'max_force': max_force
        })
        
    except Exception as e:
        print(f"\nError processing {csv_file.name}: {e}")
        continue

print(f"\nProcessed {len(results)} simulations successfully!")

# Convert to DataFrame for analysis
df_results = pd.DataFrame(results)

# Check if we have any data
if len(df_results) == 0:
    print("\n" + "=" * 70)
    print("ERROR: No simulation data found!")
    print("=" * 70)
    print("\nPossible reasons:")
    print("  1. No CSV files in csv_data/ directory")
    print("  2. Simulation hasn't been run yet")
    print("  3. CSV filename pattern doesn't match PID_A{angle}_BallX{x}_TrainX{x}.csv")
    print("\nTo fix:")
    print("  1. Run the simulation: .\\build\\bin\\freefall_object.exe")
    print("  2. Wait for CSV files to be generated in csv_data/")
    print("  3. Then run this analysis script again")
    print("\n" + "=" * 70)
    exit(1)

# Summary statistics
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)

print(f"\nTotal simulations: {len(df_results)}")
print(f"Successful catches: {df_results['caught'].sum()} ({100*df_results['caught'].mean():.1f}%)")
print(f"Failed catches: {(~df_results['caught']).sum()} ({100*(~df_results['caught']).mean():.1f}%)")

print("\n--- Performance by Angle ---")
for angle in sorted(df_results['angle'].unique()):
    angle_data = df_results[df_results['angle'] == angle]
    catch_rate = 100 * angle_data['caught'].mean()
    avg_time = angle_data[angle_data['caught']]['train_arrival_time'].mean()
    print(f"  {angle:>5.0f}°: {catch_rate:>5.1f}% catch rate, avg arrival: {avg_time:>5.2f}s")

print("\n--- Performance by Distance ---")
distance_bins = [0, 20, 40, 60, 80, 100]
for i in range(len(distance_bins)-1):
    bin_data = df_results[(df_results['distance_to_travel'] >= distance_bins[i]) & 
                          (df_results['distance_to_travel'] < distance_bins[i+1])]
    if len(bin_data) > 0:
        catch_rate = 100 * bin_data['caught'].mean()
        avg_time = bin_data[bin_data['caught']]['train_arrival_time'].mean()
        print(f"  {distance_bins[i]:>3.0f}-{distance_bins[i+1]:>3.0f}m: {catch_rate:>5.1f}% catch rate, " +
              f"avg time: {avg_time:>5.2f}s, n={len(bin_data)}")

# Save results to CSV
output_file = "analysis_results.csv"
df_results.to_csv(output_file, index=False)
print(f"\n✓ Detailed results saved to: {output_file}")

# Create summary visualizations
print("\nGenerating visualizations...")

# 1. Catch Rate Heatmap by Angle and Distance
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Heatmap: Catch Rate vs Angle and Distance
angles = sorted(df_results['angle'].unique())
distances = sorted(df_results['distance_to_travel'].unique())

catch_rate_matrix = np.zeros((len(distances), len(angles)))
for i, dist in enumerate(distances):
    for j, ang in enumerate(angles):
        subset = df_results[(df_results['angle'] == ang) & 
                           (df_results['distance_to_travel'] == dist)]
        if len(subset) > 0:
            catch_rate_matrix[i, j] = 100 * subset['caught'].mean()
        else:
            catch_rate_matrix[i, j] = np.nan

im = axes[0, 0].imshow(catch_rate_matrix, aspect='auto', cmap='RdYlGn', vmin=0, vmax=100)
axes[0, 0].set_xticks(range(len(angles)))
axes[0, 0].set_xticklabels([f'{int(a)}°' for a in angles])
axes[0, 0].set_yticks(range(0, len(distances), 2))
axes[0, 0].set_yticklabels([f'{int(distances[i])}m' for i in range(0, len(distances), 2)])
axes[0, 0].set_xlabel('Landing Angle')
axes[0, 0].set_ylabel('Distance to Travel (m)')
axes[0, 0].set_title('Catch Success Rate (%)')
plt.colorbar(im, ax=axes[0, 0], label='Success Rate (%)')

# Catch rate by angle
angle_stats = df_results.groupby('angle')['caught'].agg(['mean', 'count']).reset_index()
axes[0, 1].bar(angle_stats['angle'], 100 * angle_stats['mean'], 
               color=['green' if x > 50 else 'red' for x in 100 * angle_stats['mean']])
axes[0, 1].set_xlabel('Landing Angle (degrees)')
axes[0, 1].set_ylabel('Catch Success Rate (%)')
axes[0, 1].set_title('Success Rate by Landing Angle')
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].set_ylim([0, 105])

# Average arrival time by distance (for successful catches)
caught_data = df_results[df_results['caught']].copy()
dist_time = caught_data.groupby('distance_to_travel')['train_arrival_time'].agg(['mean', 'std']).reset_index()
axes[1, 0].errorbar(dist_time['distance_to_travel'], dist_time['mean'], 
                     yerr=dist_time['std'], marker='o', capsize=5, linewidth=2)
axes[1, 0].set_xlabel('Distance to Travel (m)')
axes[1, 0].set_ylabel('Train Arrival Time (s)')
axes[1, 0].set_title('Average Arrival Time vs Distance (Successful Catches Only)')
axes[1, 0].grid(True, alpha=0.3)

# Max force distribution
axes[1, 1].hist(df_results['max_force'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
axes[1, 1].axvline(df_results['max_force'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f"Mean: {df_results['max_force'].mean():.1f}N")
axes[1, 1].set_xlabel('Maximum Applied Force (N)')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].set_title('Distribution of Maximum Forces')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
output_dir = Path(__file__).parent.parent / "plots"
output_dir.mkdir(exist_ok=True)
plt.savefig(output_dir / 'comprehensive_analysis.png', dpi=150, bbox_inches='tight')
print("✓ Saved: plots/comprehensive_analysis.png")

# 2. Detailed angle-specific analysis
fig2, axes2 = plt.subplots(2, 5, figsize=(20, 8))
axes2 = axes2.flatten()

for idx, angle in enumerate(sorted(df_results['angle'].unique())):
    angle_data = df_results[df_results['angle'] == angle]
    
    # Scatter: Distance vs Success
    caught = angle_data[angle_data['caught']]
    missed = angle_data[~angle_data['caught']]
    
    axes2[idx].scatter(caught['distance_to_travel'], caught['train_x_initial'], 
                       c='green', marker='o', s=20, alpha=0.6, label='Caught')
    axes2[idx].scatter(missed['distance_to_travel'], missed['train_x_initial'], 
                       c='red', marker='x', s=20, alpha=0.6, label='Missed')
    
    catch_rate = 100 * angle_data['caught'].mean()
    axes2[idx].set_title(f'{int(angle)}° ({catch_rate:.0f}% success)', fontsize=10)
    axes2[idx].set_xlabel('Distance (m)', fontsize=8)
    axes2[idx].set_ylabel('Train Start X (m)', fontsize=8)
    axes2[idx].grid(True, alpha=0.3)
    axes2[idx].legend(fontsize=7)

plt.tight_layout()
plt.savefig(output_dir / 'angle_specific_analysis.png', dpi=150, bbox_inches='tight')
print("✓ Saved: plots/angle_specific_analysis.png")

plt.close('all')

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE!")
print("=" * 70)
print(f"\nFiles generated:")
print(f"  - analysis_results.csv (detailed metrics)")
print(f"  - plots/comprehensive_analysis.png (summary visualizations)")
print(f"  - plots/angle_specific_analysis.png (per-angle success patterns)")
