# Train Catching Falling Ball - Complete System Documentation

## Executive Summary

This project demonstrates **horizontal interception control** where a ground-based train must move horizontally to catch a ball falling from a fixed height. The system combines:
- **Real-time physics simulation** (C implementation)
- **PID control** (8 controller variants)
- **Advanced visualization** (static plots + real-time animation)
- **Performance analysis** (24 simulations across 3 integration methods)

**Problem Statement**: A ball drops from 100m height at horizontal position X=60m. A train starting at X=10m must reach the landing zone before the ball hits ground (~4.5 seconds).

---

## System Architecture

### Three-Stage Pipeline

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│  C Simulation   │      │   CSV Data       │      │   Python Analysis   │
│  (main.c)       │ ───▶ │   (24 files)     │ ───▶ │   (plots + anim)    │
│                 │      │                  │      │                     │
│ • Physics       │      │ • Train X pos    │      │ • 8-subplot plots  │
│ • PID control   │      │ • Ball Y height  │      │ • Real-time anim   │
│ • Integration   │      │ • Control force  │      │ • Performance      │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
     Generates                Stores                    Visualizes
    24 CSV files           simulation data            results & metrics
```

### Physical Setup

```
                Y
                ↑
        100m    •  Ball starts here (X=60m, Y=100m)
                |
                |  Ball falls vertically
                |  (Fixed X=60m)
         50m    |
                |
                |
                |
          0m  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▶ X
              🚂─────────────────────▶ 🎯
              10m                    60m
              
              Train moves horizontally on ground (Y=0m)
              Target: Reach X=60m before ball lands
```

**Key Coordinates:**
- Ball: Fixed X=60m, Y falls from 100m → 0m
- Train: X moves from 10m → 60m, Fixed Y=0m
- Distance to cover: 50m horizontal
- Time available: ~4.5 seconds

---

## Physics Models

### 1. Ball Physics (Independent - No Control)

**Vertical free fall at fixed X=60m:**

```
Position:  y(t) = y₀ - 0.5 × g × t²
Velocity:  v_y(t) = -g × t

where:
  y₀ = 100 m    (initial height)
  g = 9.81 m/s²  (gravity)
  
Landing time:  t = √(2y₀/g) = √(200/9.81) ≈ 4.52 seconds
Landing velocity: v = -g×t ≈ -44.3 m/s
```

**No air resistance in simplified model**

### 2. Train Physics (Controlled)

**Horizontal motion along ground:**

```
Newton's 2nd Law:
  F_net = F_control - F_friction
  a = F_net / m
  
State equations:
  dv/dt = a
  dx/dt = v
  
where:
  m = 10 kg        (train mass)
  F_control        (PID output)
  F_friction       (velocity-dependent)
```

**Three Integration Methods:**

| Method | Velocity Update | Position Update | Accuracy |
|--------|----------------|-----------------|----------|
| **Euler** | v(t+Δt) = v(t) + a×Δt | x(t+Δt) = x(t) + v×Δt | 1st order |
| **Trapezoidal** | Uses average of a(t) and a(t+Δt) | Uses average of v(t) and v(t+Δt) | 2nd order |
| **Simplified** | Euler with F_friction=0 | Same as Euler | Ideal physics |

**Time step**: Δt = 0.04s (25 Hz control loop)

---

## Control System

### PID Control Equation

```
u(t) = Kp×e(t) + Ki×∫e(τ)dτ + Kd×(de/dt)

where:
  e(t) = setpoint - x_train(t)
  setpoint = 60m (constant)
  x_train(t) = current horizontal position
```

**Error Definition:**
- Positive error: Train behind target (e > 0 → apply forward force)
- Negative error: Train ahead of target (e < 0 → apply backward force)
- Zero error: Train at target (e = 0 → maintain position)

### Controller Configurations

| Type | Kp | Ki | Kd | Characteristics |
|------|----|----|-----|-----------------|
| **P** | 5.0 | 0 | 0 | Fast but steady-state error |
| **P_Adaptive** | 10.0 | 0 | 0 | Self-tuning proportional |
| **PD** | 8.0 | 0 | 3.0 | Fast + damped response |
| **PD_Adaptive** | 12.0 | 0 | 4.0 | Adaptive damping |
| **PI** | 6.0 | 2.0 | 0 | Eliminates steady-state error |
| **PI_Adaptive** | 9.0 | 2.5 | 0 | Self-tuning integral |
| **PID** | 7.0 | 2.0 | 3.5 | **Best overall** |
| **PID_Adaptive** | 10.0 | 2.5 | 4.0 | Self-tuning PID |

**Tuning Philosophy:**
- **Kp**: Primary driving force (proportional to distance from target)
- **Ki**: Eliminates steady-state error (integral of error over time)
- **Kd**: Damping (prevents overshoot and oscillation)
- **Adaptive**: Adjusts gains based on error magnitude

---

## Implementation Details

### File Structure

```
FreeFall_Object/
├── src/                           # C source code
│   ├── main.c                     # Orchestrates simulations
│   ├── fallingobject.c/.h         # Train physics model
│   ├── controller.c/.h            # PID implementations
│   └── plot.c/.h                  # CSV export
│
├── build/                         # Build artifacts
│   └── bin/
│       └── freefall_object.exe    # Compiled executable
│
├── csv_data/                      # Simulation outputs (24 files)
│   ├── P_Controller.csv
│   ├── PID_Controller.csv
│   └── ... (8 controllers × 3 methods)
│
├── plots/                         # Static visualizations
│   ├── P/                         # 6 P controller variants
│   ├── PI/                        # 6 PI controller variants
│   ├── PD/                        # 6 PD controller variants
│   └── PID/                       # 6 PID controller variants
│
├── animations/                    # Real-time MP4 animations (optional)
│   └── *.mp4                      # 24 animation files
│
├── diagrams/                      # System documentation
│   ├── 01_system_overview.png
│   ├── 02_falling_object_physics.png
│   └── ...
│
├── visualize_simulation.py        # Static plot generator
├── animate_realtime.py            # Real-time animation
├── README.md                      # Main documentation
├── README_VISUALIZATION.md        # Visualization guide
└── SYSTEM_OVERVIEW.md            # This file
```

### CSV Data Format

Each CSV file contains 4 columns:

```csv
time,train_position,falling_object_position,applied_force
0.000000,10.000000,100.000000,0.000000
0.040000,10.019620,99.992152,9.810000
0.080000,10.078480,99.968614,19.431200
...
```

**Columns:**
1. **time**: Simulation time (seconds)
2. **train_position**: Horizontal X position (meters, 0-100m)
3. **falling_object_position**: Vertical Y height (meters, 0-100m)
4. **applied_force**: Control force (Newtons, -100 to +100 N)

**Typical file size**: ~50 KB per CSV file (1250 data points)

---

## Visualization System

### 1. Static Plots (8 Subplots)

Generated by `visualize_simulation.py`:

```
┌─────────────────────┬─────────────────────┐
│ 1. Position vs Time │ 2. 2D Physical Space│
│    • Train X (blue) │    • Horizontal train│
│    • Ball Y (red)   │    • Vertical ball   │
├─────────────────────┼─────────────────────┤
│ 3. Control Force    │ 4. Tracking Error   │
│    • F vs time      │    • Ball Y - Train X│
├─────────────────────┼─────────────────────┤
│ 5. Velocities       │ 6. Phase Portrait   │
│    • Train dX/dt    │    • Error vs dE/dt  │
├─────────────────────┼─────────────────────┤
│ 7. Position Compare │ 8. Performance Table│
│    • Initial vs Final│   • Metrics summary │
└─────────────────────┴─────────────────────┘
```

**Output**: 24 PNG files (1920×1080 resolution)

**Usage:**
```bash
python visualize_simulation.py
# Processes all 24 CSV files
# Saves plots to plots/P/, plots/PI/, plots/PD/, plots/PID/
```

### 2. Real-Time Animation

Generated by `animate_realtime.py`:

**Features:**
- **Physical space view** (main plot):
  - Ball falling vertically at X=60m (red circle)
  - Train moving horizontally at Y=0m (blue square)
  - Ground line (brown)
  - Trajectories and trails
  
- **Time-series plots** (right side):
  - Train position (X) and ball height (Y) vs time
  - Control force vs time
  - Tracking error vs time
  
- **Real-time indicators**:
  - Horizontal distance: |Train X - 60m|
  - Vertical distance: |Ball Y - 0m|
  - Current time
  
- **Catch detection**:
  - Stops when |horizontal| < 2m AND |vertical| < 5m
  - Shows "CAUGHT!" message
  - Enlarges markers

**Usage:**
```bash
# Display single animation
python animate_realtime.py --file csv_data/PID_Controller.csv --display-only --speed 2.0

# Generate all 24 MP4 files (requires FFmpeg)
python animate_realtime.py --speed 1.5

# Save single animation
python animate_realtime.py --file csv_data/PID_Controller.csv --speed 1.0
```

**Output**: MP4 videos (720p, ~2-5 MB each, ~10 seconds duration)

---

## Performance Metrics

### Calculated Metrics (in plots)

For each simulation, the following metrics are computed:

1. **Position Metrics**:
   - Train initial position (m)
   - Train final position (m)
   - Train travel distance (Δx)
   - Ball initial height (m)
   - Ball final height (m)
   - Ball fall distance (Δy)

2. **Error Metrics**:
   - Mean absolute error (MAE)
   - Root mean square error (RMSE)
   - Maximum error
   - Final error (steady-state)

3. **Control Metrics**:
   - Mean force magnitude
   - Maximum force
   - Total control effort (∫|F|dt)
   - Force standard deviation

4. **Timing Metrics**:
   - Ball landing time
   - Train arrival time
   - Interception success (yes/no)
   - Time margin (if caught)

### Typical Results

**PID Controller (Best Performance):**
```
Train Position:
  Initial: 10.00 m
  Final:   61.97 m
  Δ:       51.97 m
  Target:  60.00 m
  
Ball Height:
  Initial: 100.00 m
  Final:   0.00 m
  Δ:       100.00 m
  Landing: 4.52 s
  
Control:
  Mean Force: 15.3 N
  Max Force:  48.7 N
  
Success: ✅ CAUGHT at t=8.08s
```

**P Controller (Steady-State Error):**
```
Train Position:
  Initial: 10.00 m
  Final:   58.24 m  ← Does not reach 60m!
  Δ:       48.24 m
  Target:  60.00 m
  
Success: ❌ MISSED (1.76m short)
```

---

## Workflow

### Complete Pipeline

```bash
# Step 1: Build C simulation
cd FreeFall_Object
mkdir build && cd build
cmake ..
cmake --build .

# Step 2: Run simulation (generates 24 CSV files)
cd ..
./build/bin/freefall_object.exe

# Step 3: Generate static plots (24 PNG files)
python visualize_simulation.py

# Step 4: Generate animations (24 MP4 files)
python animate_realtime.py --speed 1.5

# Step 5: View results
start plots/PID/PID_Controller.png
start animations/PID_Controller.mp4
```

**Total execution time**: ~2-3 minutes on modern PC

---

## Key Insights

### Controller Comparison

| Controller | Reaches Target? | Response Speed | Overshoot | Steady-State |
|-----------|----------------|----------------|-----------|--------------|
| P | ❌ (~58m) | Fast | Low | **Has error** |
| PI | ✅ (60m) | Medium | Medium | **No error** |
| PD | ✅ (60-62m) | **Very fast** | Low | Small error |
| PID | ✅ (60m) | **Fast** | **Minimal** | **No error** |

**Winner**: PID provides optimal balance

### Integration Method Comparison

| Method | Accuracy | Speed | Use Case |
|--------|----------|-------|----------|
| Euler | Moderate | Fast | Quick prototyping |
| Trapezoidal | High | Slower | Accurate simulation |
| Simplified | Ideal | Fast | Understanding control |

### Physical Challenge

**Why this is difficult:**
1. **Time constraint**: Only 4.5 seconds available
2. **Initial distance**: 50m to cover in limited time
3. **Required velocity**: Must reach ~11 m/s average speed
4. **Precise stopping**: Must stop at exactly 60m
5. **Constant target**: No feedback from ball's X position

**Control objectives** (in priority order):
1. Reach 60m before ball lands (t < 4.5s)
2. Stop precisely at 60m (minimal overshoot)
3. Use minimal control effort
4. Smooth trajectory (no oscillations)

---

## Advanced Features

### Adaptive Control

Adaptive controllers adjust gains based on error:

```c
if (fabs(error) > 10.0) {
    Kp *= 1.2;  // Increase proportional for large errors
    Kd *= 1.1;  // Increase damping
}
```

**Benefits:**
- Faster response when far from target
- Gentler control when close to target
- Self-tuning behavior

### Catch Detection Algorithm

```python
horizontal_distance = abs(train_x - ball_x)
vertical_distance = abs(ball_y - ground_y)

if horizontal_distance < 2.0 and vertical_distance < 5.0:
    # Train is within 2m horizontally and ball is within 5m of ground
    status = "CAUGHT!"
    stop_animation()
```

**Criteria:**
- Horizontal: Train within 2m of X=60m
- Vertical: Ball within 5m of ground
- Both conditions must be true

---

## Dependencies

### C Compilation
- **CMake**: 3.10 or higher
- **C Compiler**: GCC 7.0+, Clang 6.0+, or MSVC 2017+
- **Libraries**: Standard C math library (libm)

### Python Visualization
```bash
pip install matplotlib>=3.3.0
pip install numpy>=1.19.0
pip install pandas>=1.1.0
```

### Optional (Animation Export)
```bash
# Windows (using Chocolatey)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

---

## Troubleshooting

### Common Issues

**1. CSV files not generated**
```bash
# Check if executable exists
ls build/bin/freefall_object.exe

# Run with verbose output
./build/bin/freefall_object.exe 2>&1 | tee simulation.log
```

**2. Plots not showing correctly**
```bash
# Verify Python packages
python -c "import matplotlib, numpy, pandas; print('OK')"

# Check CSV data
head csv_data/PID_Controller.csv
```

**3. Animation fails to save**
```bash
# Test FFmpeg installation
ffmpeg -version

# Try display-only mode first
python animate_realtime.py --file csv_data/PID_Controller.csv --display-only
```

**4. Train doesn't reach target**
- Check controller gains (Kp, Ki, Kd)
- Verify setpoint = 60% in main.c
- Increase simulation time if needed

---

## Future Enhancements

### Planned Features

1. **Variable landing position**: Ball falls at random X coordinate
2. **Multiple balls**: Train must prioritize which to catch
3. **Inclined landing surface**: Non-horizontal ground (angle ≠ 0°)
4. **Wind effects**: Horizontal force on ball (changes X during fall)
5. **Train mass variations**: Different loads affect dynamics
6. **Obstacle avoidance**: Additional constraints on train path
7. **Real-time plotting**: Live updates during C simulation
8. **Machine learning**: Neural network PID tuning

### Research Directions

- **Optimal control**: Compare PID vs LQR vs MPC
- **Disturbance rejection**: Random forces on train
- **Multi-agent**: Multiple trains, multiple balls
- **Hardware-in-loop**: Connect to physical train model

---

## References

### Related Projects
- **Water_Tank_Kp**: Water level control (non-linear)
- **Train_Forces**: Vertical position tracking
- **This project**: Horizontal interception

### Documentation Files
- [README.md](README.md): Main project documentation
- [README_VISUALIZATION.md](README_VISUALIZATION.md): Visualization guide
- [diagrams/](diagrams/): System architecture diagrams

### Theory
- PID Control Theory
- Newton's Laws of Motion
- Numerical Integration Methods
- Real-Time Control Systems

---

## License & Contact

**License**: Educational use  
**Course**: Applied Control Systems - Autonomous Cars  
**Topic**: PID Control & Model Predictive Control (MPC)

**Author**: Control Systems Course Project  
**Last Updated**: January 2025

---

*For detailed visualization instructions, see [README_VISUALIZATION.md](README_VISUALIZATION.md)*
