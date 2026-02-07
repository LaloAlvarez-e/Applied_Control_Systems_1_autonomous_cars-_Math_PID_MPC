"""
Generate comprehensive system diagrams for Train-Falling Object tracking system
Shows: 1) Object in free fall, 2) Train on inclined track, 3) Track/line geometry
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, FancyBboxPatch
from matplotlib.patches import Arc

# Set up the plotting style
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def create_system_overview():
    """
    Diagram 1: Complete System Overview
    Shows all three components: falling object, train on inclined track, and track line
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Horizontal Position (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Vertical Position (m)', fontsize=12, fontweight='bold')
    ax.set_title('System Overview: Train Tracking Falling Object on Inclined Track', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Define track angle and parameters
    track_angle_deg = 30  # degrees from horizontal
    track_angle_rad = np.radians(track_angle_deg)
    track_length = 120
    
    # Track line (inclined)
    track_start_x = 0
    track_start_y = 10
    track_end_x = track_start_x + track_length * np.cos(track_angle_rad)
    track_end_y = track_start_y + track_length * np.sin(track_angle_rad)
    
    ax.plot([track_start_x, track_end_x], [track_start_y, track_end_y], 
            'k-', linewidth=4, label='Track/Line (angle θ)', zorder=1)
    
    # Add track angle annotation
    arc_radius = 15
    arc = Arc((track_start_x, track_start_y), 2*arc_radius, 2*arc_radius, 
              angle=0, theta1=0, theta2=track_angle_deg, color='green', linewidth=2)
    ax.add_patch(arc)
    ax.text(track_start_x + 12, track_start_y + 3, f'θ = {track_angle_deg}°', 
            fontsize=11, color='green', fontweight='bold')
    
    # Train initial position on track
    train_distance_along_track = 30  # meters along track
    train_x = track_start_x + train_distance_along_track * np.cos(track_angle_rad)
    train_y = track_start_y + train_distance_along_track * np.sin(track_angle_rad)
    
    # Draw train
    train_width = 8
    train_height = 4
    train_rect = Rectangle((train_x - train_width/2, train_y - train_height/2), 
                           train_width, train_height, 
                           angle=track_angle_deg, 
                           facecolor='blue', edgecolor='darkblue', 
                           linewidth=2, alpha=0.7, label='Train (Controlled System)')
    ax.add_patch(train_rect)
    
    # Train position marker
    ax.plot(train_x, train_y, 'bo', markersize=12, zorder=5)
    ax.text(train_x - 8, train_y - 8, f'Train Initial Position\n(s₀ = {train_distance_along_track}m along track)', 
            fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Falling object initial position
    object_x0 = 60  # Initial horizontal position
    object_y0 = 90  # Initial height
    
    # Draw falling object
    ax.plot(object_x0, object_y0, 'ro', markersize=15, label='Falling Object (Initial)', zorder=5)
    ax.text(object_x0 + 3, object_y0 + 3, f'Object Initial Position\n(x₀={object_x0}m, y₀={object_y0}m)', 
            fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    
    # Draw trajectory of falling object (parabolic path)
    g = 9.81
    v_x0 = 0  # Initial horizontal velocity
    v_y0 = 0  # Released from rest
    t_values = np.linspace(0, 4, 50)
    
    traj_x = object_x0 + v_x0 * t_values
    traj_y = object_y0 + v_y0 * t_values - 0.5 * g * t_values**2
    
    # Only plot trajectory above the track
    valid_traj = traj_y >= 0
    ax.plot(traj_x[valid_traj], traj_y[valid_traj], 'r--', linewidth=2, 
            alpha=0.6, label='Object Trajectory (free fall)')
    
    # Calculate intersection point with track
    # Parametric: track point = (x_t, y_t) = track_start + s*(cos(θ), sin(θ))
    # Object: (x_o, y_o) = (x0, y0 - 0.5*g*t²)
    # Find where object trajectory intersects track line
    
    # Simplified: show approximate intersection
    intersection_s = 50  # meters along track
    intersection_x = track_start_x + intersection_s * np.cos(track_angle_rad)
    intersection_y = track_start_y + intersection_s * np.sin(track_angle_rad)
    
    ax.plot(intersection_x, intersection_y, 'g*', markersize=20, 
            label='Target Interception Point', zorder=6)
    ax.text(intersection_x + 3, intersection_y - 5, 'Interception\nPoint', 
            fontsize=10, color='green', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Draw force vectors on train
    force_scale = 8
    force_x = train_x + force_scale * np.cos(track_angle_rad)
    force_y = train_y + force_scale * np.sin(track_angle_rad)
    ax.arrow(train_x, train_y, force_x - train_x, force_y - train_y,
             head_width=2, head_length=1.5, fc='purple', ec='purple', 
             linewidth=2, zorder=7, alpha=0.8)
    ax.text(force_x + 2, force_y + 2, 'F_applied', fontsize=11, 
            color='purple', fontweight='bold')
    
    # Draw gravity on object
    gravity_arrow_length = 10
    ax.arrow(object_x0, object_y0, 0, -gravity_arrow_length,
             head_width=2, head_length=1.5, fc='orange', ec='orange', 
             linewidth=2, zorder=7)
    ax.text(object_x0 + 3, object_y0 - gravity_arrow_length/2, 'g', 
            fontsize=12, color='orange', fontweight='bold')
    
    # Add coordinate system axes
    ax.arrow(5, 5, 10, 0, head_width=1, head_length=1, fc='black', ec='black', linewidth=1.5)
    ax.arrow(5, 5, 0, 10, head_width=1, head_length=1, fc='black', ec='black', linewidth=1.5)
    ax.text(16, 4, 'x', fontsize=12, fontweight='bold')
    ax.text(4, 16, 'y', fontsize=12, fontweight='bold')
    
    # Add legend
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('01_system_overview.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 01_system_overview.png")
    plt.close()


def create_falling_object_physics():
    """
    Diagram 2: Falling Object Physics Details
    Shows forces, coordinate system, and equations
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(-10, 110)
    ax.set_ylim(-10, 110)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Horizontal Position x (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Vertical Position y (m)', fontsize=12, fontweight='bold')
    ax.set_title('System 1: Falling Object Physics (2D Projectile Motion)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Object at initial position
    x0, y0 = 50, 80
    
    # Draw object
    object_circle = Circle((x0, y0), 3, facecolor='red', edgecolor='darkred', linewidth=2, zorder=5)
    ax.add_patch(object_circle)
    ax.text(x0 + 5, y0, 'Object\n(mass m)', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.9))
    
    # Draw forces
    # Gravity force
    F_g_scale = 15
    ax.arrow(x0, y0, 0, -F_g_scale, head_width=2, head_length=2, 
             fc='blue', ec='blue', linewidth=3, zorder=6)
    ax.text(x0 + 3, y0 - F_g_scale/2, r'$\vec{F_g} = mg$', fontsize=12, 
            color='blue', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Drag force (if moving)
    v_scale = 12
    F_drag_scale = 8
    # Velocity vector
    ax.arrow(x0, y0, v_scale*0.5, -v_scale, head_width=2, head_length=2,
             fc='green', ec='green', linewidth=2, zorder=6, linestyle='--', alpha=0.7)
    ax.text(x0 + v_scale*0.5 + 3, y0 - v_scale/2, r'$\vec{v}$', fontsize=12, 
            color='green', fontweight='bold')
    
    # Drag force (opposite to velocity)
    ax.arrow(x0, y0, -F_drag_scale*0.3, F_drag_scale*0.6, head_width=1.5, head_length=1.5,
             fc='orange', ec='orange', linewidth=2, zorder=6, alpha=0.7)
    ax.text(x0 - F_drag_scale*0.3 - 8, y0 + F_drag_scale*0.6, r'$\vec{F_{drag}} = C_d v^2$', 
            fontsize=11, color='orange', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Trajectory
    g = 9.81
    t_vals = np.linspace(0, 4, 100)
    traj_x = x0 + 0 * t_vals  # No initial horizontal velocity
    traj_y = y0 - 0.5 * g * t_vals**2
    
    valid = traj_y >= 0
    ax.plot(traj_x[valid], traj_y[valid], 'r--', linewidth=2, alpha=0.6, label='Trajectory')
    
    # Show multiple positions along trajectory
    sample_times = [0, 1, 2, 3]
    for t in sample_times:
        if y0 - 0.5 * g * t**2 >= 0:
            pos_x = x0
            pos_y = y0 - 0.5 * g * t**2
            ax.plot(pos_x, pos_y, 'ro', markersize=6, alpha=0.5)
            if t > 0:
                ax.text(pos_x + 3, pos_y, f't={t}s', fontsize=9, alpha=0.7)
    
    # Equations box
    eq_text = (
        "Equations of Motion:\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Position:\n"
        "  x(t) = x₀ + v_x0·t\n"
        "  y(t) = y₀ + v_y0·t - ½g·t²\n\n"
        "Velocity:\n"
        "  v_x(t) = v_x0\n"
        "  v_y(t) = v_y0 - g·t\n\n"
        "Forces:\n"
        "  F_y = -mg - C_d·v_y²·sign(v_y)\n"
        "  F_x = -C_d·v_x²·sign(v_x)\n\n"
        "Parameters:\n"
        "  g = 9.81 m/s²\n"
        "  m = object mass (kg)\n"
        "  C_d = drag coefficient"
    )
    
    ax.text(5, 65, eq_text, fontsize=10, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, pad=1),
            verticalalignment='top')
    
    # Initial conditions box
    ic_text = (
        "Initial Conditions:\n"
        "━━━━━━━━━━━━━━━━━\n"
        "Position: (x₀, y₀)\n"
        "  x₀ = variable\n"
        "  y₀ = variable\n\n"
        "Velocity: (v_x0, v_y0)\n"
        "  v_x0 = 0 or ≠ 0\n"
        "  v_y0 = 0 (dropped)\n"
        "        or ≠ 0 (thrown)"
    )
    
    ax.text(75, 95, ic_text, fontsize=9, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.9, pad=1),
            verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('02_falling_object_physics.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 02_falling_object_physics.png")
    plt.close()


def create_train_track_physics():
    """
    Diagram 3: Train on Inclined Track Physics
    Shows train constrained to move along angled line
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 85)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('x - Horizontal Position (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('y - Vertical Position (m)', fontsize=12, fontweight='bold')
    ax.set_title('System 2: Train on Inclined Track (Constrained Motion)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Track parameters
    theta_deg = 35
    theta_rad = np.radians(theta_deg)
    track_x0, track_y0 = 5, 10  # Track starting point
    track_length = 100
    
    # Draw track
    track_x_end = track_x0 + track_length * np.cos(theta_rad)
    track_y_end = track_y0 + track_length * np.sin(theta_rad)
    ax.plot([track_x0, track_x_end], [track_y0, track_y_end], 
            'k-', linewidth=5, label='Track/Rail', zorder=1)
    
    # Track angle annotation
    arc_r = 12
    arc = Arc((track_x0, track_y0), 2*arc_r, 2*arc_r, 
              angle=0, theta1=0, theta2=theta_deg, color='purple', linewidth=2.5)
    ax.add_patch(arc)
    ax.text(track_x0 + 10, track_y0 + 2, f'θ = {theta_deg}°', 
            fontsize=12, color='purple', fontweight='bold')
    
    # Train position along track
    s = 40  # Position parameter (meters along track from start)
    train_x = track_x0 + s * np.cos(theta_rad)
    train_y = track_y0 + s * np.sin(theta_rad)
    
    # Draw train (using Rectangle which supports rotation)
    train_width = 10
    train_height = 5
    train_rect = Rectangle((train_x - train_width/2, train_y - train_height/2), 
                            train_width, train_height,
                            angle=theta_deg,
                            facecolor='blue', edgecolor='darkblue', 
                            linewidth=2.5, alpha=0.8, zorder=5)
    ax.add_patch(train_rect)
    
    # Train center marker
    ax.plot(train_x, train_y, 'wo', markersize=8, zorder=6, markeredgecolor='black', markeredgewidth=2)
    
    # Coordinate system along track
    # Tangent direction (along track)
    tangent_scale = 12
    tangent_x = train_x + tangent_scale * np.cos(theta_rad)
    tangent_y = train_y + tangent_scale * np.sin(theta_rad)
    ax.arrow(train_x, train_y, tangent_x - train_x, tangent_y - train_y,
             head_width=2, head_length=2, fc='green', ec='green', 
             linewidth=2.5, zorder=7)
    ax.text(tangent_x + 2, tangent_y + 2, r'$\hat{t}$ (tangent)', 
            fontsize=11, color='green', fontweight='bold')
    
    # Normal direction (perpendicular to track)
    normal_scale = 12
    normal_x = train_x + normal_scale * np.cos(theta_rad + np.pi/2)
    normal_y = train_y + normal_scale * np.sin(theta_rad + np.pi/2)
    ax.arrow(train_x, train_y, normal_x - train_x, normal_y - train_y,
             head_width=2, head_length=2, fc='orange', ec='orange', 
             linewidth=2.5, zorder=7)
    ax.text(normal_x + 2, normal_y, r'$\hat{n}$ (normal)', 
            fontsize=11, color='orange', fontweight='bold')
    
    # Forces on train
    # Applied force (along track)
    F_app_scale = 15
    F_app_x = train_x + F_app_scale * np.cos(theta_rad)
    F_app_y = train_y + F_app_scale * np.sin(theta_rad)
    ax.arrow(train_x, train_y, F_app_x - train_x, F_app_y - train_y,
             head_width=2.5, head_length=2, fc='red', ec='darkred', 
             linewidth=3, zorder=8)
    ax.text(F_app_x + 2, F_app_y + 3, r'$F_{applied}$', 
            fontsize=12, color='darkred', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.9))
    
    # Gravity force
    F_g_scale = 15
    ax.arrow(train_x, train_y, 0, -F_g_scale,
             head_width=2.5, head_length=2, fc='blue', ec='darkblue', 
             linewidth=3, zorder=8)
    ax.text(train_x + 3, train_y - F_g_scale/2, r'$mg$', 
            fontsize=12, color='darkblue', fontweight='bold')
    
    # Gravity components
    # Tangential component (along track, downward)
    F_g_tangent_scale = F_g_scale * np.sin(theta_rad)
    F_g_t_x = train_x - F_g_tangent_scale * np.cos(theta_rad)
    F_g_t_y = train_y - F_g_tangent_scale * np.sin(theta_rad)
    ax.arrow(train_x, train_y, F_g_t_x - train_x, F_g_t_y - train_y,
             head_width=1.5, head_length=1.5, fc='cyan', ec='cyan', 
             linewidth=2, zorder=8, linestyle='--', alpha=0.8)
    ax.text(F_g_t_x - 5, F_g_t_y - 3, r'$mg\sin\theta$', 
            fontsize=10, color='cyan', fontweight='bold')
    
    # Normal component (perpendicular to track)
    F_g_normal_scale = F_g_scale * np.cos(theta_rad)
    F_g_n_x = train_x - F_g_normal_scale * np.cos(theta_rad + np.pi/2)
    F_g_n_y = train_y - F_g_normal_scale * np.sin(theta_rad + np.pi/2)
    ax.arrow(train_x, train_y, F_g_n_x - train_x, F_g_n_y - train_y,
             head_width=1.5, head_length=1.5, fc='magenta', ec='magenta', 
             linewidth=2, zorder=8, linestyle='--', alpha=0.8)
    ax.text(F_g_n_x - 12, F_g_n_y + 2, r'$mg\cos\theta$', 
            fontsize=10, color='magenta', fontweight='bold')
    
    # Normal force from track (reaction)
    ax.arrow(train_x, train_y, -F_g_n_x + train_x, -F_g_n_y + train_y,
             head_width=1.5, head_length=1.5, fc='lime', ec='darkgreen', 
             linewidth=2, zorder=8, alpha=0.8)
    ax.text(train_x - F_g_n_x + train_x + 2, train_y - F_g_n_y + train_y - 3, 
            r'$N$ (normal force)', fontsize=10, color='darkgreen', fontweight='bold')
    
    # Position parameter
    ax.plot([track_x0, train_x], [track_y0, train_y], 'g--', linewidth=2, alpha=0.5)
    ax.text((track_x0 + train_x)/2 - 3, (track_y0 + train_y)/2 + 5, f's = {s}m', 
            fontsize=11, color='green', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))
    
    # Equations box
    eq_text = (
        "Train Motion Along Track:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Position on track:\n"
        "  x(s) = x₀ + s·cos(θ)\n"
        "  y(s) = y₀ + s·sin(θ)\n\n"
        "Equation of motion:\n"
        "  m·(d²s/dt²) = F_applied - mg·sin(θ) - C_d·v²\n\n"
        "Where:\n"
        "  s = position along track (m)\n"
        "  v = ds/dt = velocity along track\n"
        "  θ = track angle from horizontal\n"
        "  (x₀, y₀) = track origin\n\n"
        "Constraints:\n"
        "  Train can only move along track\n"
        "  N = mg·cos(θ) (normal force)"
    )
    
    ax.text(5, 75, eq_text, fontsize=9.5, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.95, pad=1),
            verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('03_train_track_physics.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 03_train_track_physics.png")
    plt.close()


def create_track_geometry():
    """
    Diagram 4: Track/Line Geometry Details
    Shows different track configurations and coordinate transformations
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))
    
    # Subplot 1: Horizontal track (θ = 0°)
    ax1.set_xlim(-5, 105)
    ax1.set_ylim(-5, 35)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('System 3a: Horizontal Track (θ = 0°)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('y (m)')
    
    ax1.plot([0, 100], [10, 10], 'k-', linewidth=4, label='Track')
    ax1.plot(30, 10, 'bs', markersize=12, label='Train')
    ax1.text(30, 5, 's = 30m', fontsize=10, ha='center')
    ax1.arrow(30, 10, 15, 0, head_width=1.5, head_length=2, fc='red', ec='red', linewidth=2)
    ax1.text(48, 11, r'$F_{applied}$', fontsize=11, color='red', fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.text(5, 25, 'Equation: y = 10m (constant)\ns = x', 
             fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Subplot 2: Inclined track (θ = 30°)
    ax2.set_xlim(-5, 105)
    ax2.set_ylim(-5, 55)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.set_title('System 3b: Inclined Track (θ = 30°)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('x (m)')
    ax2.set_ylabel('y (m)')
    
    theta = np.radians(30)
    x0, y0 = 5, 5
    s_max = 100
    x_end = x0 + s_max * np.cos(theta)
    y_end = y0 + s_max * np.sin(theta)
    
    ax2.plot([x0, x_end], [y0, y_end], 'k-', linewidth=4, label='Track')
    
    s_train = 40
    train_x = x0 + s_train * np.cos(theta)
    train_y = y0 + s_train * np.sin(theta)
    ax2.plot(train_x, train_y, 'bs', markersize=12, label='Train')
    ax2.text(train_x - 5, train_y - 5, f's = {s_train}m', fontsize=10)
    
    arc = Arc((x0, y0), 20, 20, angle=0, theta1=0, theta2=30, color='purple', linewidth=2)
    ax2.add_patch(arc)
    ax2.text(x0 + 12, y0 + 2, 'θ=30°', fontsize=10, color='purple', fontweight='bold')
    
    ax2.arrow(train_x, train_y, 12*np.cos(theta), 12*np.sin(theta),
              head_width=1.5, head_length=2, fc='red', ec='red', linewidth=2)
    ax2.legend(loc='upper right')
    
    eq_text = f'Track origin: ({x0}, {y0})\nx(s) = {x0} + s·cos(30°)\ny(s) = {y0} + s·sin(30°)'
    ax2.text(10, 45, eq_text, fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Subplot 3: Steep track (θ = 60°)
    ax3.set_xlim(-5, 65)
    ax3.set_ylim(-5, 95)
    ax3.set_aspect('equal')
    ax3.grid(True, alpha=0.3)
    ax3.set_title('System 3c: Steep Track (θ = 60°)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('x (m)')
    ax3.set_ylabel('y (m)')
    
    theta = np.radians(60)
    x0, y0 = 5, 10
    s_max = 80
    x_end = x0 + s_max * np.cos(theta)
    y_end = y0 + s_max * np.sin(theta)
    
    ax3.plot([x0, x_end], [y0, y_end], 'k-', linewidth=4, label='Track')
    
    s_train = 35
    train_x = x0 + s_train * np.cos(theta)
    train_y = y0 + s_train * np.sin(theta)
    ax3.plot(train_x, train_y, 'bs', markersize=12, label='Train')
    ax3.text(train_x + 3, train_y, f's = {s_train}m', fontsize=10)
    
    arc = Arc((x0, y0), 15, 15, angle=0, theta1=0, theta2=60, color='purple', linewidth=2)
    ax3.add_patch(arc)
    ax3.text(x0 + 8, y0 + 3, 'θ=60°', fontsize=10, color='purple', fontweight='bold')
    
    ax3.arrow(train_x, train_y, 12*np.cos(theta), 12*np.sin(theta),
              head_width=1.5, head_length=2, fc='red', ec='red', linewidth=2)
    ax3.legend(loc='upper right')
    
    ax3.text(5, 80, 'Steep incline:\nHigh gravity component\nmg·sin(60°) ≈ 0.87mg', 
             fontsize=10, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Subplot 4: General track formula and transformations
    ax4.axis('off')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    ax4.set_title('System 3d: General Track Equations & Transformations', 
                  fontsize=12, fontweight='bold')
    
    formulas = """
    TRACK PARAMETERIZATION
    ══════════════════════════════════════════
    
    Given:
    • Track origin: (x₀, y₀)
    • Track angle: θ (measured from horizontal)
    • Position parameter: s (distance along track from origin)
    
    Track Equation (Parametric):
    ┌─────────────────────────────────────┐
    │  x(s) = x₀ + s · cos(θ)             │
    │  y(s) = y₀ + s · sin(θ)             │
    └─────────────────────────────────────┘
    
    Track Equation (Cartesian):
    ┌─────────────────────────────────────┐
    │  y - y₀ = tan(θ) · (x - x₀)        │
    └─────────────────────────────────────┘
    
    COORDINATE TRANSFORMATIONS
    ══════════════════════════════════════════
    
    World → Track coordinates:
    Given point (x, y) in world frame
    Position along track: s = √[(x-x₀)² + (y-y₀)²]
    
    Track → World coordinates:
    Given s, compute (x, y) using parametric equations above
    
    VELOCITY & ACCELERATION
    ══════════════════════════════════════════
    
    Velocity along track:   v = ds/dt
    Acceleration:           a = dv/dt = d²s/dt²
    
    World frame velocity:
    ┌─────────────────────────────────────┐
    │  vₓ = v · cos(θ)                    │
    │  vᵧ = v · sin(θ)                    │
    └─────────────────────────────────────┘
    
    FORCE BALANCE (along track direction)
    ══════════════════════════════════════════
    ┌─────────────────────────────────────────────────┐
    │  m · a = F_applied - mg·sin(θ) - C_d·v²        │
    └─────────────────────────────────────────────────┘
    
    Where:
    • F_applied = control force (from PID controller)
    • mg·sin(θ) = tangential gravity component
    • C_d·v² = drag force (air resistance)
    """
    
    ax4.text(0.5, 9.5, formulas, fontsize=9.5, family='monospace',
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.95, pad=1))
    
    plt.tight_layout()
    plt.savefig('04_track_geometry.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 04_track_geometry.png")
    plt.close()


def create_interception_geometry():
    """
    Diagram 5: Interception Problem Geometry
    Shows how to calculate when train catches falling object
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 11))
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('x - Horizontal Position (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('y - Vertical Position (m)', fontsize=12, fontweight='bold')
    ax.set_title('Interception Problem: When Does Train Catch Falling Object?', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Track
    theta_deg = 40
    theta_rad = np.radians(theta_deg)
    track_x0, track_y0 = 0, 5
    track_length = 110
    track_x_end = track_x0 + track_length * np.cos(theta_rad)
    track_y_end = track_y0 + track_length * np.sin(theta_rad)
    
    ax.plot([track_x0, track_x_end], [track_y0, track_y_end], 
            'k-', linewidth=5, label='Track', zorder=1)
    
    # Falling object trajectory
    obj_x0, obj_y0 = 45, 95
    g = 9.81
    t_vals = np.linspace(0, 4.5, 100)
    obj_x = obj_x0 + 0 * t_vals
    obj_y = obj_y0 - 0.5 * g * t_vals**2
    
    valid = obj_y >= 0
    ax.plot(obj_x[valid], obj_y[valid], 'r--', linewidth=3, 
            label='Object Trajectory', zorder=2, alpha=0.7)
    
    # Object initial position
    ax.plot(obj_x0, obj_y0, 'ro', markersize=15, zorder=5, label='Object (t=0)')
    ax.text(obj_x0 + 3, obj_y0 + 2, f'Object Start\n({obj_x0}, {obj_y0})', 
            fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.9))
    
    # Find intersection point (where object trajectory crosses track line)
    # Track line equation: y = track_y0 + tan(theta) * (x - track_x0)
    # Object trajectory: x = obj_x0 (vertical fall), y = obj_y0 - 0.5*g*t²
    
    # At intersection: track_y0 + tan(theta)*(obj_x0 - track_x0) = obj_y0 - 0.5*g*t²
    # Solve for t:
    y_intersection_on_track = track_y0 + np.tan(theta_rad) * (obj_x0 - track_x0)
    
    if y_intersection_on_track < obj_y0:
        t_intersection = np.sqrt(2 * (obj_y0 - y_intersection_on_track) / g)
        x_intersection = obj_x0
        y_intersection = y_intersection_on_track
        
        # Calculate s (position along track)
        s_intersection = ((x_intersection - track_x0) / np.cos(theta_rad))
        
        # Mark intersection point
        ax.plot(x_intersection, y_intersection, 'g*', markersize=25, 
                zorder=10, label='Interception Point')
        ax.text(x_intersection + 5, y_intersection + 3, 
                f'Interception Point\nt = {t_intersection:.2f}s\ns = {s_intersection:.1f}m', 
                fontsize=11, fontweight='bold', color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.95))
        
        # Show object at several time points
        time_points = [0, 1, 2, t_intersection]
        for i, t in enumerate(time_points):
            if obj_y0 - 0.5 * g * t**2 >= 0:
                x_t = obj_x0
                y_t = obj_y0 - 0.5 * g * t**2
                if i < len(time_points) - 1:
                    ax.plot(x_t, y_t, 'ro', markersize=8, alpha=0.5, zorder=4)
                    ax.text(x_t - 8, y_t, f't={t:.1f}s', fontsize=9, alpha=0.7)
        
        # Train positions
        # Initial position
        s_train_0 = 20
        train_x0_pos = track_x0 + s_train_0 * np.cos(theta_rad)
        train_y0_pos = track_y0 + s_train_0 * np.sin(theta_rad)
        ax.plot(train_x0_pos, train_y0_pos, 'bs', markersize=12, 
                zorder=5, label='Train (t=0)')
        ax.text(train_x0_pos - 10, train_y0_pos - 5, 
                f'Train Start\ns₀ = {s_train_0}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
        
        # Train at interception
        train_x_final = track_x0 + s_intersection * np.cos(theta_rad)
        train_y_final = track_y0 + s_intersection * np.sin(theta_rad)
        ax.plot(train_x_final, train_y_final, 'bd', markersize=12, zorder=5)
        ax.text(train_x_final - 12, train_y_final + 5, 
                f'Train at interception\ns = {s_intersection:.1f}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.9))
        
        # Distance train must travel
        delta_s = s_intersection - s_train_0
        ax.plot([train_x0_pos, train_x_final], [train_y0_pos, train_y_final],
                'b-', linewidth=2, linestyle=':', alpha=0.7)
        mid_x = (train_x0_pos + train_x_final) / 2
        mid_y = (train_y0_pos + train_y_final) / 2
        ax.text(mid_x - 8, mid_y - 5, f'Δs = {delta_s:.1f}m', 
                fontsize=10, color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Equations box
    eq_text = (
        "Interception Condition:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Object position at time t:\n"
        "  x_obj(t) = x_obj0\n"
        "  y_obj(t) = y_obj0 - ½gt²\n\n"
        "Train position at time t:\n"
        "  x_train(t) = x₀ + s(t)·cos(θ)\n"
        "  y_train(t) = y₀ + s(t)·sin(θ)\n\n"
        "Interception when:\n"
        "  x_obj(t) = x_train(t)\n"
        "  y_obj(t) = y_train(t)\n\n"
        "Solve for t and s(t)\n\n"
        "Control objective:\n"
        "  Train must reach s_target\n"
        "  before time t_intercept"
    )
    
    ax.text(5, 35, eq_text, fontsize=9, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.95, pad=1),
            verticalalignment='top')
    
    ax.legend(loc='upper right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('05_interception_geometry.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 05_interception_geometry.png")
    plt.close()


def create_control_system_block_diagram():
    """
    Diagram 6: Control System Block Diagram
    Shows how the controller processes information
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Complete Control System Block Diagram', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Helper function to draw boxes
    def draw_box(ax, x, y, width, height, text, color='lightblue'):
        rect = FancyBboxPatch((x, y), width, height, 
                              boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + width/2, y + height/2, text, 
                ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Draw blocks
    # Setpoint (falling object position)
    draw_box(ax, 0.5, 7, 2, 1.2, 'Falling Object\nPosition\nx_obj(t), y_obj(t)', 'lightcoral')
    
    # Calculated setpoint for train
    draw_box(ax, 3, 7, 2, 1.2, 'Calculate\nTarget s(t)\non track', 'lightyellow')
    
    # Error calculation
    draw_box(ax, 5.5, 7, 1.5, 1.2, 'Error\ne = s_target - s', 'lightgreen')
    
    # PID Controller
    draw_box(ax, 7.5, 6.5, 2, 2, 'PID Controller\nKp, Ki, Kd', 'lightblue')
    
    # Force output
    draw_box(ax, 10, 7, 2, 1.2, 'Applied Force\nF_applied', 'plum')
    
    # Train dynamics
    draw_box(ax, 12.5, 6.5, 3, 2, 'Train Dynamics\nm·a = F - mg·sin(θ) - C_d·v²', 'lightcyan')
    
    # Position output
    draw_box(ax, 13.5, 4, 1.5, 1, 'Train Position\ns(t)', 'lightyellow')
    
    # Arrows
    def draw_arrow(ax, x1, y1, x2, y2, label=''):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y + 0.2, label, fontsize=9, ha='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Forward path
    draw_arrow(ax, 2.5, 7.6, 3, 7.6, 'x_obj, y_obj')
    draw_arrow(ax, 5, 7.6, 5.5, 7.6, 's_target')
    draw_arrow(ax, 7, 7.6, 7.5, 7.6, 'e(t)')
    draw_arrow(ax, 9.5, 7.5, 10, 7.6, 'F(t)')
    draw_arrow(ax, 12, 7.5, 12.5, 7.5)
    
    # Position to output
    ax.plot([14.25, 14.25], [6.5, 4.9], 'k-', linewidth=2)
    ax.plot([14.25, 14.25], [4.9, 4.9], 'k-', linewidth=2)
    ax.plot([13.5, 14.25], [4.5, 4.5], 'k-', linewidth=2)
    draw_arrow(ax, 14.25, 4.9, 14.25, 4.95)
    
    # Feedback path
    ax.plot([13.5, 6.5], [4.5, 4.5], 'k-', linewidth=2)
    ax.plot([6.5, 6.5], [4.5, 6.4], 'k-', linewidth=2)
    draw_arrow(ax, 6.5, 6.4, 6.5, 7, 's(t)')
    
    # Add disturbance
    ax.text(13.5, 9, 'Disturbances:', fontsize=10, fontweight='bold')
    ax.text(13.5, 8.5, '• Gravity: mg·sin(θ)', fontsize=9)
    ax.text(13.5, 8.1, '• Drag: C_d·v²', fontsize=9)
    ax.annotate('', xy=(14, 8), xytext=(14, 8.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Add legend box
    legend_text = (
        "Control Variables:\n"
        "• s = position along track (m)\n"
        "• v = velocity along track (m/s)\n"
        "• F_applied = control force (N)\n"
        "• e = error = s_target - s_actual\n\n"
        "PID Control Law:\n"
        "F = Kp·e + Ki·∫e·dt + Kd·(de/dt)"
    )
    ax.text(1, 2, legend_text, fontsize=9, family='monospace',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, pad=0.8),
           verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('06_control_system_block_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 06_control_system_block_diagram.png")
    plt.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Generating System Diagrams")
    print("="*60 + "\n")
    
    print("Creating comprehensive system diagrams...\n")
    
    create_system_overview()
    create_falling_object_physics()
    create_train_track_physics()
    create_track_geometry()
    create_interception_geometry()
    create_control_system_block_diagram()
    
    print("\n" + "="*60)
    print("✓ All diagrams generated successfully!")
    print("="*60)
    print("\nGenerated files:")
    print("  1. 01_system_overview.png - Complete system with all components")
    print("  2. 02_falling_object_physics.png - Object in free fall physics")
    print("  3. 03_train_track_physics.png - Train on inclined track")
    print("  4. 04_track_geometry.png - Track geometry and equations")
    print("  5. 05_interception_geometry.png - Interception problem")
    print("  6. 06_control_system_block_diagram.png - Control system overview")
    print("\n")
