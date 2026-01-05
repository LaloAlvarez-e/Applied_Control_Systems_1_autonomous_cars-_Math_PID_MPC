# Water Tank Control System - Controller Examples

This project demonstrates **8 different controller implementations** (P, P Adaptive, PD, PD Adaptive, PI, PI Adaptive, PID, PID Adaptive) for a water tank system, with **3 integration methods** (Euler, Trapezoidal, Simplified) generating **24 total plots**.

## System Overview

**Water Tank:**
- **Tank geometry**: Radius = 5.0 m, Area = π×r² ≈ 78.54 m²
- **Maximum capacity**: 354 m³ (calculated from area × max_height: 78.54 × 4.507)
- **State representation**: Percentage (0-100%) normalized to max volume
- **Initial level**: 30% (106.2 m³)
- **Initial setpoint**: 70% (247.8 m³)
- **Setpoint profile**: 70%→20%→90%→50% at 12s intervals
- **Outflow coefficient**: 0.1
- **Maximum inflow**: 50.0 m³/s
- **Water density**: 1000 kg/m³

**Simulation:**
- **Time step (dt)**: 0.04 s (matching Python reference)
- **Total time**: 50 s
- **Integration methods**: Euler, Trapezoidal, Simplified (no outflow)

## Controller Types

### 1. Proportional (P) Controller
**File:** `main.c` → Executable: `water_tank_kp.exe`

**Standard P Controller Gains:**
- Kp = 1.0 (matches Python Kp=1000 kg/s ÷ density 1000)
- Ki = 0.0
- Kd = 0.0

**P Adaptive Controller Gains:**
- Kp = 5.0 (matches Python Kp=5000 kg/s ÷ density 1000)
- Ki = 0.0
- Kd = 0.0

**Control Law:**
```
u(t) = Kp * e(t)
```

**Characteristics:**
- **Standard**: Moderate response, predictable behavior
- **Adaptive**: 5× faster response with gain scheduling
- Both have steady-state error (no integral term)
- Simple and robust
- Direct response to current error only

---

### 2. Proportional-Integral (PI) Controller
**File:** `main.c` → Executable: `water_tank_kp.exe`

**Standard PI Controller Gains:**
- Kp = 0.30
- Ki = 0.08
- Kd = 0.0

**PI Adaptive Controller Gains:**
- Kp = 0.80
- Ki = 0.08
- Kd = 0.0

**Control Law:**
```
u(t) = Kp * e(t) + Ki * ∫e(τ)dτ
```

**Characteristics:**
- **Eliminates steady-state error** via integral term
- **Standard**: Conservative, slower response
- **Adaptive**: 2.7× faster proportional response with gain scheduling
- Integral accumulates error over time
- May overshoot if Ki is too large
- Best for systems requiring zero steady-state error

---

### 3. Proportional-Derivative (PD) Controller
**File:** `main.c` → Executable: `water_tank_kp.exe`

**Standard PD Controller Gains:**
- Kp = 0.40
- Ki = 0.0
- Kd = 0.60

**PD Adaptive Controller Gains:**
- Kp = 2.8
- Ki = 0.0
- Kd = 0.45

**Control Law:**
```
u(t) = Kp * e(t) + Kd * de(t)/dt
```

**Characteristics:**
- **Adds damping** to reduce overshoot and oscillations
- **Standard**: Well-damped, smooth response
- **Adaptive**: 7× faster proportional response with gain scheduling
- Derivative anticipates future error trends
- Sensitive to noise (use filtering in real systems)
- May have steady-state error (no integral action)
- Excellent for systems prone to overshoot

---

### 4. Proportional-Integral-Derivative (PID) Controller
**File:** `main.c` → Executable: `water_tank_kp.exe`

**Standard PID Controller Gains:**
- Kp = 0.35
- Ki = 0.08
- Kd = 0.50

**PID Adaptive Controller Gains:**
- Kp = 1.0
- Ki = 0.08
- Kd = 0.50

**Control Law:**
```
u(t) = Kp * e(t) + Ki * ∫e(τ)dτ + Kd * de(t)/dt
```

**Characteristics:**
- **Combines all three control actions** for optimal performance
- **Standard**: Balanced performance, good for general use
- **Adaptive**: 2.9× faster proportional response with gain scheduling
- **Eliminates steady-state error** (integral term)
- **Reduces overshoot** (derivative term)
- **Fast response** (proportional term)
- Most versatile but requires careful tuning
- Industry standard for complex control applications

## Integration Methods

The simulation runs each controller with **3 different integration methods**:

### 1. Euler Integration (Standard)
- Simple forward integration: `x[k+1] = x[k] + dx/dt * dt`
- Fast but less accurate
- Includes outflow dynamics (Torricelli's law)

### 2. Trapezoidal Integration (Improved Accuracy)
- Averages current and next derivatives: `x[k+1] = x[k] + (dx[k] + dx[k+1])/2 * dt`
- More accurate than Euler
- Matches Python reference implementation
- Includes outflow dynamics

### 3. Simplified Model (No Outflow)
- Pure accumulation: `volume[k+1] = volume[k] + flow * dt`
- Matches Python reference exactly (no outflow term)
- Best for validating controller behavior without physics complexity

---

## Building and Running

### Build the project:
```bash
cmake --build build
```

### Run simulation (generates 24 plots):
```bash
.\build\bin\water_tank_kp.exe
```

### Output:
- **24 PNG plots** saved to `results/` directory:
  - 8 plots with Euler integration (P, P_Adaptive, PD, PD_Adaptive, PI, PI_Adaptive, PID, PID_Adaptive)
  - 8 plots with Trapezoidal integration (same controllers)
  - 8 plots with Simplified model (same controllers)

### Plot Organization:
```
results/
├── P/
│   ├── plot_P_Controller.png
│   ├── plot_P_Controller_Trapezoidal.png
│   ├── plot_P_Controller_Simplified.png
│   ├── plot_P_Adaptive_Controller.png
│   ├── plot_P_Adaptive_Controller_Trapezoidal.png
│   └── plot_P_Adaptive_Controller_Simplified.png
├── PD/ (6 plots)
├── PI/ (6 plots)
└── PID/ (6 plots)
```

## Implementation Details

### Percentage Normalization

The system uses **percentage (0-100%)** for user-friendly display:
```c
// Tank geometry
double tank_area = π × 5.0² ≈ 78.54 m²
double max_height = 4.507 m
double max_volume = tank_area × max_height ≈ 354 m³

// State representation (percentage)
tank.level = 30.0;      // 30% → 106.2 m³
tank.setpoint = 70.0;   // 70% → 247.8 m³
```

### Physics Conversion

Internally converts percentage to volume to height for physics:
```c
// Step 1: Percentage → Volume
volume_m3 = (level_pct / 100.0) × max_volume

// Step 2: Volume → Height (for outflow calculation)
level_m = volume_m3 / area

// Step 3: Calculate physics (Torricelli's law)
outflow = coeff × √(level_m)

// Step 4: Update and convert back to percentage
dVolume = netFlow × dt
dLevel_pct = (dVolume / max_volume) × 100.0
level += dLevel_pct
```

### Gain Conversion from Python Reference

```c
// Python: Kp = 1000 kg/s (mass flow rate)
// C: Kp = 1000 / 1000 = 1.0 (volume flow rate)
// No area scaling needed - we use volume directly!
```

## Controller Structure

Each controller implementation includes:
- **ControllerParams**: Kp, Ki, Kd gains (tuned for optimal performance)
- **ControllerState**: integral, previousError, adaptiveKp for stateful controllers
- **ControllerConfig**: Complete configuration with callbacks and time step
- **WaterTank**: System state with model parameters and controller integration

## Adaptive Controllers

**Adaptive controllers** use **gain scheduling** to adjust Kp based on error magnitude:

```c
// Gain scheduling based on error
if (absError > large_error_threshold) {
    adaptiveKp = base_Kp × gain_multiplier;  // Higher gain for large errors
} else {
    adaptiveKp = base_Kp;  // Normal gain for small errors
}
```

**Benefits:**
- Faster response to large errors
- Smoother behavior near setpoint
- Better performance across different operating conditions

## Comparison Summary

| Controller | Kp | Ki | Kd | Response Speed | Steady-State Error | Overshoot | Complexity |
|------------|-----|-----|-----|----------------|-------------------|-----------|------------|
| P          | 1.0 | 0   | 0   | Moderate       | Yes               | Low       | Simple     |
| P Adaptive | 5.0 | 0   | 0   | Fast           | Yes               | Moderate  | Simple     |
| PD         | 0.4 | 0   | 0.6 | Moderate       | Yes               | Very Low  | Moderate   |
| PD Adaptive| 2.8 | 0   | 0.45| Fast           | Yes               | Low       | Moderate   |
| PI         | 0.3 | 0.08| 0   | Slow           | No                | Moderate  | Moderate   |
| PI Adaptive| 0.8 | 0.08| 0   | Moderate       | No                | Moderate  | Moderate   |
| PID        | 0.35| 0.08| 0.5 | Moderate       | No                | Low       | Complex    |
| PID Adaptive|1.0 | 0.08| 0.5 | Fast           | No                | Low       | Complex    |

## References

- Python reference: `calculus_sim_waterTanks_Kp_controller.py`
- Documentation: `CONTROLLER_TUNING_EXPLANATION.md`
- Architecture: `README.md`

- **Multi-threaded Execution**: All 8 controllers run in parallel for each integration method
- **Modular Design**: Separate error calculation from control law
- **State Management**: Integral, derivative, and adaptive terms maintained in ControllerState
- **Callback Architecture**: Flexible system model and controller callbacks
- **Three Integration Methods**: Euler, Trapezoidal, and Simplified for comparison
- **Type Safety**: Strong typing with enums and structures
- **Error Propagation**: Consistent error handling throughout
- **Percentage Normalization**: User-friendly 0-100% display
- **Python Reference Match**: Matches calculus_sim_waterTanks_Kp_controller.py
