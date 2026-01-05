# Water Tank Control System - Architecture

A comprehensive C implementation of PID control systems for water tank management, featuring 8 different controllers with 3 integration methods, generating 24 comparative plots.

## Project Overview

This project demonstrates advanced control system theory applied to a water tank system, implementing:
- **8 Controller Types**: P, P Adaptive, PD, PD Adaptive, PI, PI Adaptive, PID, PID Adaptive
- **3 Integration Methods**: Euler, Trapezoidal, Simplified (no outflow)
- **24 Total Simulations**: Each controller × 3 integration methods
- **Multi-threaded Execution**: Parallel simulation for performance
- **Real-time Plotting**: Gnuplot-based visualization with PNG export

### Key Features

- ✅ **Percentage-normalized control** (0-100%) for user-friendly operation
- ✅ **Python reference matching** - Validates against `calculus_sim_waterTanks_Kp_controller.py`
- ✅ **Adaptive gain scheduling** - Controllers adjust gains based on error magnitude
- ✅ **Multiple integration methods** - Compare accuracy and performance
- ✅ **Modular architecture** - Clean separation of concerns
- ✅ **Cross-platform** - Windows (MSVC/MinGW) and Linux (GCC) support

## Architecture Design

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.c                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Simulation Orchestration (Multi-threaded)          │   │
│  │  - Creates 8 controller configurations              │   │
│  │  - Launches parallel simulations                    │   │
│  │  - Manages 3 integration method phases              │   │
│  └──────────────┬──────────────────────────────────────┘   │
│                 │                                           │
│                 ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Controller Layer (controller.c/h)            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  P / P_A   │  │  PD / PD_A │  │  PI / PI_A │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  │              ┌────────────┐                         │  │
│  │              │ PID / PID_A│                         │  │
│  │              └────────────┘                         │  │
│  │  - Implements control laws                          │  │
│  │  - Manages controller state (integral, derivative)  │  │
│  │  - Adaptive gain scheduling                         │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                           │
│                 ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         System Model Layer (watertank.c/h)           │  │
│  │  ┌──────────┐  ┌────────────┐  ┌──────────────┐    │  │
│  │  │  Euler   │  │Trapezoidal │  │  Simplified  │    │  │
│  │  │Integration│  │Integration │  │  (No Outflow)│    │  │
│  │  └──────────┘  └────────────┘  └──────────────┘    │  │
│  │  - Tank physics (Torricelli's law)                  │  │
│  │  - Percentage ↔ Volume ↔ Height conversion          │  │
│  │  - Flow rate calculations                           │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                           │
│                 ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Visualization Layer (plot.c/h)               │  │
│  │  - Gnuplot interface                                 │  │
│  │  - Real-time data collection                         │  │
│  │  - PNG plot generation                               │  │
│  │  - Multi-window management                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input (Setpoint Profile)
    ↓
┌─────────────────────────────────────┐
│  Percentage (0-100%)                │
│  30% → 70% → 20% → 90% → 50%       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Convert to Volume (m³)             │
│  percentage × max_volume / 100      │
│  30% → 106.2 m³                     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Calculate Error (m³)               │
│  error = setpoint - current         │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Controller (P/PI/PD/PID)           │
│  u = Kp×e + Ki×∫e + Kd×de/dt       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Volume Flow Rate (m³/s)            │
│  Clamped to max_inflow              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Convert to Height for Physics (m)  │
│  height = volume / area             │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Calculate Outflow (Torricelli)     │
│  Q_out = C × √(h)                   │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Net Flow = Inflow - Outflow        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Integrate (Euler/Trapezoidal)      │
│  volume[k+1] = volume[k] + flow×dt  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Convert back to Percentage         │
│  percentage = volume / max_volume × 100 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Display & Plot (0-100%)            │
└─────────────────────────────────────┘
```

## File Structure

```
Water_Tank_Kp/
├── CMakeLists.txt              # CMake build configuration
├── Makefile                    # Legacy makefile (deprecated)
│
├── main.c                      # Main simulation orchestrator
├── controller.c/h              # Controller implementations
├── watertank.c/h               # Tank physics and models
├── plot.c/h                    # Gnuplot visualization
│
├── README.md                   # Architecture documentation (this file)
├── README_CONTROLLERS.md       # Controller guide and comparison
├── CONTROLLER_TUNING_EXPLANATION.md  # Gain tuning theory
│
├── build/                      # CMake build output
│   ├── bin/
│   │   └── water_tank_kp.exe  # Executable
│   └── ...
│
└── results/                    # Generated plots
    ├── P/                      # 6 P controller plots
    ├── PD/                     # 6 PD controller plots
    ├── PI/                     # 6 PI controller plots
    └── PID/                    # 6 PID controller plots
```

## Core Components

### 1. Main Orchestrator (`main.c`)

**Responsibilities:**
- Configure 8 controllers with optimized gains
- Launch multi-threaded simulations
- Manage 3 integration method phases (24 total simulations)
- Handle Ctrl-C gracefully

**Key Functions:**
- `main()` - Entry point, configures all simulations
- `runSimulation()` - Thread function for single controller simulation
- `console_ctrl_handler()` - Graceful shutdown on Ctrl-C

**Threading Model:**
```c
// Phase 1: Euler (8 threads in parallel)
// Phase 2: Trapezoidal (8 threads in parallel)
// Phase 3: Simplified (8 threads in parallel)
// Total: 24 simulations, but only 8 concurrent at a time
```

### 2. Controller Layer (`controller.c/h`)

**Controller Implementations:**

| Function | Type | Description |
|----------|------|-------------|
| `pController()` | P | Basic proportional control |
| `adaptivePController()` | P Adaptive | P with gain scheduling |
| `pdController()` | PD | Proportional + Derivative |
| `adaptivePdController()` | PD Adaptive | PD with gain scheduling |
| `piController()` | PI | Proportional + Integral |
| `adaptivePiController()` | PI Adaptive | PI with gain scheduling |
| `pidController()` | PID | Full PID control |
| `adaptivePidController()` | PID Adaptive | PID with gain scheduling |

**Data Structures:**
```c
typedef struct {
    double Kp;  // Proportional gain
    double Ki;  // Integral gain
    double Kd;  // Derivative gain
} ControllerParams;

typedef struct {
    double integral;        // Accumulated error (for I term)
    double previousError;   // Last error (for D term)
    double adaptiveKp;      // Dynamic Kp for adaptive controllers
    int historyIndex;       // Circular buffer index
    double cumulativeError; // Total error magnitude
} ControllerState;
```

**Adaptive Gain Scheduling:**
```c
// Adjust Kp based on error magnitude
if (|error| > threshold) {
    adaptiveKp = baseKp × gain_multiplier;
} else {
    adaptiveKp = baseKp;
}
```

### 3. Tank Model Layer (`watertank.c/h`)

**Integration Methods:**

| Function | Method | Accuracy | Physics |
|----------|--------|----------|---------|
| `tankModel()` | Euler | Standard | Full (with outflow) |
| `tankModelTrapezoidal()` | Trapezoidal | High | Full (with outflow) |
| `tankModelTrapezoidalSimplified()` | Trapezoidal | High | No outflow |

**Physics Model:**
```c
// Torricelli's Law for outflow
Q_out = C × √(2gh) = C × √(h)  // Simplified with g=2

// Net flow
dV/dt = Q_in - Q_out

// Integration
V[k+1] = V[k] + dV/dt × dt  // Euler
V[k+1] = V[k] + (dV[k] + dV[k+1])/2 × dt  // Trapezoidal
```

**Data Structures:**
```c
typedef struct {
    double outflow_coeff;   // Outflow coefficient C
    double area;            // Tank cross-section (m²)
    double max_inflow;      // Max inflow rate (m³/s)
    double density;         // Water density (kg/m³)
    double max_level;       // Max volume for 100% (m³)
    SystemModelCallback callback;
    NetFlowCallback netFlowCallback;
} ModelConfig;

typedef struct WaterTank {
    double level;           // Current percentage (0-100%)
    double setpoint;        // Target percentage (0-100%)
    double inflow;          // Inflow rate (m³/s)
    double previousNetFlow; // For trapezoidal integration
    ControllerConfig controller;
    ModelConfig model;
} WaterTank;
```

### 4. Visualization Layer (`plot.c/h`)

**Responsibilities:**
- Interface with Gnuplot
- Collect simulation data
- Generate PNG plots with 4 subplots each
- Manage multiple plot windows

**Plot Structure (each PNG):**
```
┌─────────────────────┬─────────────────────┐
│  Level vs Time      │  Setpoint vs Time   │
│  (percentage)       │  (percentage)       │
├─────────────────────┼─────────────────────┤
│  Error vs Time      │  Control Signal     │
│  (percentage)       │  (m³/s)             │
└─────────────────────┴─────────────────────┘
```

**Key Functions:**
- `initRealtimePlot()` - Initialize plot data collection
- `updateRealtimePlot()` - Add simulation data point
- `closeRealtimePlot()` - Generate and save PNG plot

## System Parameters

### Tank Geometry

```c
// Cylindrical tank
radius = 5.0 m
area = π × r² ≈ 78.54 m²
max_height = 4.507 m
max_volume = area × max_height ≈ 354 m³
```

### Initial Conditions

```c
// Percentage representation
initial_level = 30.0%      // → 106.2 m³
initial_setpoint = 70.0%   // → 247.8 m³

// Setpoint profile (changes every 12s)
t ∈ [0, 12):   setpoint = 70%   // 247.8 m³
t ∈ [12, 24):  setpoint = 20%   // 70.8 m³
t ∈ [24, 36):  setpoint = 90%   // 318.6 m³
t ∈ [36, 50]:  setpoint = 50%   // 177.0 m³
```

### Controller Gains

| Controller | Kp | Ki | Kd | Notes |
|------------|-----|-----|-----|-------|
| P | 1.0 | 0.0 | 0.0 | Python Kp=1000 / density=1000 |
| P Adaptive | 5.0 | 0.0 | 0.0 | Python Kp=5000 / density=1000 |
| PD | 0.4 | 0.0 | 0.6 | Tuned for damping |
| PD Adaptive | 2.8 | 0.0 | 0.45 | Aggressive + damping |
| PI | 0.3 | 0.08 | 0.0 | Eliminates steady-state error |
| PI Adaptive | 0.8 | 0.08 | 0.0 | Faster PI response |
| PID | 0.35 | 0.08 | 0.5 | Balanced all terms |
| PID Adaptive | 1.0 | 0.08 | 0.5 | Fast + optimal |

### Simulation Parameters

```c
dt = 0.04 s          // Time step (matches Python)
t_end = 50 s         // Simulation duration
steps = 1250         // Total iterations
```

## Build System

### CMake Configuration

```cmake
# Compiler: MinGW GCC (Windows) or GCC (Linux)
# Standard: C11
# Optimization: -O2 (Release)
# Warnings: -Wall -Wextra

# Output:
# - Executable: build/bin/water_tank_kp.exe
# - Intermediate: build/CMakeFiles/
```

### Build Commands

```bash
# Configure (first time only)
cmake -S . -B build

# Build
cmake --build build

# Run
.\build\bin\water_tank_kp.exe  # Windows
./build/bin/water_tank_kp      # Linux
```

## Mathematical Foundation

### Control Laws

**Proportional (P):**
```
u(t) = Kp × e(t)
```

**Proportional-Integral (PI):**
```
u(t) = Kp × e(t) + Ki × ∫e(τ)dτ
```

**Proportional-Derivative (PD):**
```
u(t) = Kp × e(t) + Kd × de(t)/dt
```

**Proportional-Integral-Derivative (PID):**
```
u(t) = Kp × e(t) + Ki × ∫e(τ)dτ + Kd × de(t)/dt
```

### Discrete-Time Implementation

```c
// Error
e[k] = setpoint[k] - measurement[k]

// Proportional
P[k] = Kp × e[k]

// Integral (cumulative)
I[k] = I[k-1] + Ki × e[k] × dt

// Derivative (finite difference)
D[k] = Kd × (e[k] - e[k-1]) / dt

// Control output
u[k] = P[k] + I[k] + D[k]

// Saturation
if (u[k] > max_inflow) u[k] = max_inflow
if (u[k] < 0) u[k] = 0
```

### Percentage Normalization

```c
// Display and control interface uses percentages
percentage = 0.0 to 100.0

// Internal conversion to volume for physics
volume_m3 = (percentage / 100.0) × max_volume

// Conversion to height for outflow calculation
height_m = volume_m3 / area

// Update back to percentage
delta_volume = net_flow × dt
delta_percentage = (delta_volume / max_volume) × 100.0
new_percentage = old_percentage + delta_percentage

// Clamp to valid range
if (new_percentage < 0.0) new_percentage = 0.0
if (new_percentage > 100.0) new_percentage = 100.0
```

## Python Reference Matching

This implementation validates against `calculus_sim_waterTanks_Kp_controller.py`:

**Matching Elements:**
- Tank geometry: radius=5m, area≈78.54m²
- Time parameters: dt=0.04s, t_end=50s
- Setpoint profile: 70→20→90→50
- Integration method: Trapezoidal rule
- Gain conversion: C_Kp = Python_Kp / density

**C Implementation Advantages:**
- 8 controllers (Python has 2)
- 3 integration methods (Python has 1)
- Multi-threaded execution (Python is serial)
- Real-time plotting (Python plots after simulation)
- Percentage normalization (Python uses absolute volumes)

## Performance Characteristics

### Execution Time

| Phase | Controllers | Integration | Time (typical) |
|-------|-------------|-------------|----------------|
| Phase 1 | 8 | Euler | ~2-3 seconds |
| Phase 2 | 8 | Trapezoidal | ~2-3 seconds |
| Phase 3 | 8 | Simplified | ~2-3 seconds |
| **Total** | **24** | **All** | **~6-10 seconds** |

### Memory Usage

- Per simulation: ~100 KB (data arrays)
- Total: ~2.4 MB (24 simulations)
- Gnuplot interface: Minimal (pipe-based)

### Threading

- 8 threads per phase (one per controller)
- Phases run sequentially (Euler → Trapezoidal → Simplified)
- Thread-safe data structures (independent allocations)

## Error Handling

### Error Codes

```c
typedef enum {
    ERROR_SUCCESS = 0,
    ERROR_NULL_POINTER,
    ERROR_INVALID_PARAMETER,
    ERROR_CALLBACK_FAILED,
    ERROR_FILE_IO,
    ERROR_MEMORY_ALLOCATION
} ErrorCode;
```

### Error Propagation

All functions return `ErrorCode`:
- Errors propagate up the call stack
- `ERROR_SUCCESS` indicates successful operation
- Non-zero codes indicate specific failures

### Graceful Shutdown

```c
// Ctrl-C handler
Ctrl-C → Set keep_running = 0
       → Threads check flag each iteration
       → Threads exit gracefully
       → Plots saved before exit
```

## Testing and Validation

### Validation Strategy

1. **Unit Testing**: Each controller function tested independently
2. **Integration Testing**: Full simulation runs for each controller
3. **Python Matching**: Simplified model matches Python reference
4. **Visual Inspection**: 24 plots reviewed for correct behavior

### Expected Behavior

- **P Controllers**: Fast response, steady-state error present
- **PI Controllers**: Slower convergence, zero steady-state error
- **PD Controllers**: Reduced overshoot, smooth response
- **PID Controllers**: Optimal performance, balanced trade-offs
- **Adaptive Controllers**: Faster than standard variants

## Future Enhancements

- [ ] Add Model Predictive Control (MPC)
- [ ] Implement Kalman filtering for noisy measurements
- [ ] Add disturbance rejection testing
- [ ] Real-time hardware-in-the-loop (HIL) support
- [ ] Web-based visualization dashboard
- [ ] Parameter auto-tuning (Ziegler-Nichols, etc.)
- [ ] Multi-tank cascaded systems

## References

- **Controller Details**: See `README_CONTROLLERS.md`
- **Gain Tuning Theory**: See `CONTROLLER_TUNING_EXPLANATION.md`
- **Python Reference**: `calculus_sim_waterTanks_Kp_controller.py`
- **Control Theory**: Åström & Murray, "Feedback Systems"
- **Numerical Methods**: Press et al., "Numerical Recipes in C"

## License

Educational and research use. See project root for license details.

## Contributing

This is an educational project demonstrating control system implementation. For questions or improvements, please refer to the course materials.

---

**Last Updated**: January 4, 2026  
**Version**: 2.0 (Percentage-normalized, 24 simulations)  
**Maintainer**: Applied Control Systems Course
