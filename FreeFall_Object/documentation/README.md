# Train Catching Falling Ball - Horizontal Interception System

## Overview
This project implements a **horizontal interception control system** where a train must move horizontally to catch a ball falling from a fixed height. Unlike vertical tracking, the train moves along the ground (X-axis) to reach a target horizontal position where the ball will land, creating a time-critical interception challenge.

**Physical Scenario:**
- 🔴 **Ball**: Dropped from height Y=100m at fixed horizontal position X=60m
- 🔵 **Train**: Starts at horizontal position X=10m, moves along ground level (Y=0m)
- 🎯 **Objective**: Train must reach X=60m before ball hits ground (~4.5 seconds)
- ⚙️ **Control Challenge**: Apply horizontal force to train to intercept falling ball in time

**Physical Interpretation:**
- **Falling Ball**: Target position (setpoint) is the ball's landing X-coordinate (60m)
- **Train**: Controlled system that moves horizontally from X=10m → X=60m
- **Controller**: Adjusts applied force to position train at interception point before ball lands

## Physics Model

The system implements two independent physics models:

### 1. Ball Physics (Vertical Free Fall)

**Fixed Horizontal Position**: X = 60m  
**Initial Height**: Y = 100m  
**Motion**: Vertical downward only

```
y(t) = y₀ - 0.5 × g × t²
v_y(t) = -g × t

where:
- g = 9.81 m/s²
- y₀ = 100 m
- Fall time ≈ 4.52 seconds
```

### 2. Train Physics (Horizontal Motion)

**Initial Position**: X = 10m  
**Target Position**: X = 60m  
**Motion**: Horizontal along ground (Y = 0m)

**Double Integration System:**
```
F_control(t) → 1/m → dv/dt=a → ∫ → v(t) → dx/dt=v(t) → ∫ → x(t)
```

**Euler Integration:**
```c
F_net = F_control - F_friction
a = F_net / m
v(t) = v(t-1) + a × dt
x(t) = x(t-1) + v × dt
```

**Trapezoidal Integration (improved accuracy):**
```c
v(t_j) = v(t_{j-1}) + (F_net(t_{j-1}) + F_net(t_j))/(2m) × Δt
x(t_j) = x(t_{j-1}) + (v(t_{j-1}) + v(t_j))/2 × Δt
```

**Force Balance:**
```
F_net = F_control - F_friction
```

**Key Parameters:**
- Train mass: m = 10.0 kg
- Friction coefficient: C_d (varies by model)
- Time step: dt = 0.04 s (25 Hz control loop)

## System Architecture

### Structure
```c
typedef struct FallingObject {
    double position_pct;       // OUTPUT: Train horizontal position 0-100% (X: 0-100m)
    double velocity;           // INTERNAL STATE: Horizontal velocity in m/s
    double position;           // INTERNAL TRACKING: Horizontal position in m
    double setpoint;           // Desired horizontal position (60% = 60m landing point)
    double applied_force;      // Control force (N) - horizontal thrust
    double previousNetForce;   // For trapezoidal integration
    ControllerConfig controller;
    ObjectModelConfig model;
} FallingObject;
```

### System Parameters

**Train:**
- **Mass**: 10 kg
- **Initial Position**: 10m (horizontal X)
- **Target Position**: 60m (horizontal X where ball lands)
- **Max Force**: 100 N (controller limit)
- **Friction**: Varies by model (Euler/Trapezoidal/Simplified)

**Ball:**
- **Initial Height**: 100m (vertical Y)
- **Landing Position**: X=60m (fixed horizontal coordinate)
- **Gravity**: g = 9.81 m/s²
- **Fall Time**: ~4.52 seconds

**Control Loop:**
- **Time Step**: dt = 0.04 s (25 Hz)
- **Max Simulation**: 50 seconds
- **Position Range**: 0-100m (normalized to 0-100%)

### Initial Conditions
- **Train Position**: 10m (10% of 100m range)
- **Train Velocity**: 0 m/s (starts from rest)
- **Ball Height**: 100m (starts falling immediately)
- **Setpoint**: 60% (60m) - constant train target position

**Note**: Unlike tracking scenarios, the setpoint is **constant** throughout the simulation. The train must reach X=60m and maintain that position while the ball falls.

## Controller Tuning

Controllers are tuned for horizontal train motion (10 kg mass, friction forces):

| Controller | Kp | Ki | Kd | Purpose |
|-----------|----|----|-----|---------|
| P | 5.0 | 0.0 | 0.0 | Basic proportional control |
| P Adaptive | 10.0 | 0.0 | 0.0 | Self-tuning proportional |
| PD | 8.0 | 0.0 | 3.0 | Fast response with damping |
| PD Adaptive | 12.0 | 0.0 | 4.0 | Adaptive damping |
| PI | 6.0 | 2.0 | 0.0 | Eliminates steady-state error |
| PI Adaptive | 9.0 | 2.5 | 0.0 | Adaptive integral action |
| PID | 7.0 | 2.0 | 3.5 | Full three-term control |
| PID Adaptive | 10.0 | 2.5 | 4.0 | Self-tuning PID |

**Tuning Strategy:**
- Higher gains needed than Water Tank (moving 10kg mass vs water level)
- Derivative term critical for preventing overshoot
- Integral term ensures train reaches exact target position (60m)

## Integration Methods

Three numerical integration methods are implemented:

1. **Euler Integration** (`objectModel`):
   - Simple first-order method
   - Faster computation
   - Less accurate for large time steps

2. **Trapezoidal Integration** (`objectModelTrapezoidal`):
   - Second-order method
   - More accurate
   - Uses average of forces/velocities

3. **Simplified Model** (`objectModelTrapezoidalSimplified`):
   - No air resistance (drag_coeff = 0)
   - Pure gravity vs control force
   - Ideal physics for comparison

## Building and Running

### Prerequisites
- CMake 3.10+
- C compiler (GCC, Clang, MSVC)
- Python 3.7+ (for visualization)

### Python Environment Setup

**Create and activate virtual environment:**
```bash
# Create virtual environment
py -3 -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\.venv\Scripts\activate.bat

# Activate (Linux/Mac)
source .venv/bin/activate

# Install required packages
pip install matplotlib numpy pandas
```

**Note**: All Python commands below assume `.venv` is activated, or use `.\.venv\Scripts\python.exe` on Windows.

### Build
```bash
cd FreeFall_Object
mkdir build && cd build
cmake ..
cmake --build .
```

### Run Simulation
```bash
# Windows
cd ..
.\build\bin\freefall_object.exe

# Linux/Mac
./build/bin/freefall_object
```

**Output**: 24 CSV files in `csv_data/` directory containing:
- Train horizontal position (X in meters)
- Ball vertical height (Y in meters)
- Applied control force (Newtons)

### Generate Visualizations

**Static Plots (8 subplots per controller):**
```bash
python visualize_simulation.py
```
Output: 24 PNG files in `plots/` directory organized by controller type

**Angle Comparison Study:**
```bash
python visualize_angles.py
```
Output: Comprehensive angle analysis in `plots/angles/`

**Real-Time Animation:**
```bash
# Display single controller
python animate_realtime.py --file csv_data/PID_Controller.csv --display-only --speed 2.0

# Generate all animations as MP4 (requires FFmpeg)
python animate_realtime.py --speed 1.5
```
Output: MP4 animations showing train catching ball

## Output Structure

```
FreeFall_Object/
├── csv_data/                      # Generated by C simulation
│   ├── P_Controller.csv
│   ├── PID_Controller.csv
│   └── ... (24 files total)
├── plots/                         # Generated by Python
│   ├── P/                         # P controller plots
│   │   ├── P_Controller.png
│   │   ├── P_Controller_Adaptive.png
│   │   └── ... (6 plots)
│   ├── PI/                        # PI controller plots
│   ├── PD/                        # PD controller plots
│   └── PID/                       # PID controller plots
└── animations/                    # Optional MP4 files
    ├── P_Controller.mp4
    └── ... (24 animations)
```

## Key Differences from Other Projects

| Aspect | Water Tank | Train Forces | This Project |
|--------|-----------|--------------|--------------|
| **Control Variable** | Water level (m) | Vertical position (m) | Horizontal position (m) |
| **Physics** | Torricelli (√h) | Gravity + friction | Horizontal motion + ball fall |
| **Disturbances** | Outflow rate | Gravity (constant) | Time deadline (ball falling) |
| **Challenge** | Non-linear √h | Counter gravity | Time-critical interception |
| **Setpoint** | Variable levels | Vertical positions | Constant target (60m) |
| **Unique Feature** | Flow dynamics | Vertical tracking | **Horizontal interception** |

## Visualization Features

**Static Plots (8 subplots):**
1. Position vs Time (train X, ball Y)
2. 2D Physical Space (X-Y coordinates)
3. Control Force time series
4. Tracking Error (Ball Y - Train X)
5. Velocities (numerical derivatives)
6. Phase Portrait (error vs error rate)
7. Initial vs Final bar chart
8. Performance Metrics table

**Real-Time Animation:**
- Ball falling vertically at X=60m
- Train moving horizontally from X=10m → X=60m
- Ground level visualization (Y=0m)
- Distance indicators (horizontal and vertical)
- Stops automatically when train catches ball
- "CAUGHT!" message on successful interception

## Files

- **fallingobject.h/c**: Physics model and equations
- **controller.h/c**: PID controllers (shared)
- **plot.h/c**: Gnuplot interface (shared)
- **main.c**: Simulation orchestration
- **CMakeLists.txt**: Build configuration

## Physics Validation

To verify the controller is working correctly:
1. Without control (F_a = 0), object should fall due to gravity
2. At equilibrium, F_a ≈ m*g = 9.81 N to hover
3. To move up, F_a > m*g
4. To move down, F_a < m*g (let gravity help)
