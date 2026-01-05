# Controller Tuning Explanation

## Overview
This document explains the mathematical reasoning behind the controller gain values (Kp, Ki, Kd) used in the water tank control system, and how they were derived from the Python reference implementation.

## PID Controller Theory

### What Each Gain Does

#### Proportional Gain (Kp)
- **Purpose**: Responds to the **current error**
- **Formula**: `u_p(t) = Kp × e(t)` where `e(t) = setpoint - measured_value`
- **Effect**: 
  - Higher Kp → Faster response, but more overshoot and oscillation
  - Lower Kp → Slower response, but more stable
  - Can never eliminate steady-state error alone
- **Physical meaning**: How aggressively the controller reacts to the current error

#### Integral Gain (Ki)
- **Purpose**: Responds to the **accumulated error over time**
- **Formula**: `u_i(t) = Ki × ∫e(τ)dτ` (continuous) or `u_i[k] = Ki × Σe[j]×dt` (discrete)
- **Effect**:
  - Eliminates steady-state error
  - Too high Ki → Overshoot and slow settling
  - Too low Ki → Slow error elimination
- **Physical meaning**: How strongly the controller corrects for persistent errors

#### Derivative Gain (Kd)
- **Purpose**: Responds to the **rate of change of error**
- **Formula**: `u_d(t) = Kd × de(t)/dt` (continuous) or `u_d[k] = Kd × (e[k] - e[k-1])/dt` (discrete)
- **Effect**:
  - Dampens oscillations and reduces overshoot
  - Improves stability
  - Sensitive to noise
- **Physical meaning**: How much the controller anticipates future error trends

### Control Signal Calculation
The total control output is:
```
u(t) = Kp×e(t) + Ki×∫e(τ)dτ + Kd×de(t)/dt
```

## Tank System Parameters

### From Python Reference (`calculus_sim_waterTanks_Kp_controller.py`)

```python
# Tank geometry
radius = 5                # Tank radius (m)
area = π × r² ≈ 78.54    # Cross-sectional area (m²)
max_height = 4.507       # Maximum tank height (m)
max_volume = area × height ≈ 354  # Maximum volume (m³)

# Initial conditions (as percentage of max_volume)
vol_o1_i = 30%           # Initial: 30% (106.2 m³ / 354 m³)
vol_r1_i = 70%           # Initial setpoint: 70% (247.8 m³ / 354 m³)

# Control parameters
Kp1 = 1000               # Proportional gain for mass flow (kg/s)
Kp3 = 5000               # Higher proportional gain (kg/s)
density_water = 1000     # Water density (kg/m³)

# Simulation parameters
dt = 0.04                # Time step (s)
t_end = 50               # Simulation duration (s)
```

### Python Control Equation
```python
# Error in volume (m³)
error[i] = vol_r[i] - volume[i]

# Mass flow rate control (kg/s)
m_dot[i] = Kp × error[i]

# Volume integration (trapezoidal rule)
volume[i+1] = volume[i] + (m_dot[i] + m_dot[i+1])/(2×density) × dt
```

## C Implementation Differences

### Percentage-Normalized Control (0-100%)

The C implementation uses **percentage (0-100%)** as the controlled variable, normalized against the maximum tank volume of **354 m³**.

#### Why Percentage Normalization?

**1. User-Friendly Interface:**
```c
// Tank geometry
double tank_area = π × 5.0² ≈ 78.54;  // m²
double max_height = 4.507;             // m
double max_volume = tank_area × max_height;  // ≈ 354 m³

// Initial conditions (as percentage)
tank.level = 30.0;      // 30% → 106.2 m³ (30% of 354 m³)
tank.setpoint = 70.0;   // 70% → 247.8 m³ (70% of 354 m³)
```

**Note**: Despite the variable name `level`, it stores **percentage (0-100%)**. The actual volume is calculated as: `volume = (percentage / 100) × max_volume`.

**2. Mathematical Simplicity:**
Using volume directly means:
- Error is in m³: `error = setpoint_volume - current_volume`
- Controller output is volume flow rate (m³/s)
- No conversion needed between level and volume for control
- Controller gains directly comparable to Python reference

**3. Controller Gain Consistency:**
With volume-based control:
```
Python: error (m³) × Kp (1/s) = control action (m³/s)
C:      error (m³) × Kp (1/s) = control action (m³/s)
```
Both use the same units and produce identical results!

#### Physics Implementation Detail

For **outflow calculations** using Torricelli's law, we convert percentage to volume to height:
```c
// Step 1: Convert percentage to actual volume
double volume_m3 = (tank.level / 100.0) * tank.model.max_level;
// Example: 30% → (30/100) × 354 = 106.2 m³

// Step 2: Convert volume to height for outflow calculation
double level_m = volume_m3 / tank.model.area;
// Example: 106.2 / 78.54 = 1.352 m

// Step 3: Calculate outflow using Torricelli's law: Q_out = C × √(h)
double outflow = tank->model.outflow_coeff * sqrt(level_m);

// Step 4: Update volume and convert back to percentage
double dVolume = netFlow * dt;  // Volume change in m³
double dLevel_pct = (dVolume / tank.model.max_level) * 100.0;
tank.level += dLevel_pct;  // Update percentage

// Step 5: Clamp to 0-100%
if (tank.level < 0) tank.level = 0;
if (tank.level > 100) tank.level = 100;
```

This hybrid approach:
- **Stores percentage** (0-100%) as the state variable for user-friendly display
- **Converts to volume** (m³) then to **height** (m) for physics calculations
- **Updates percentage** directly from volume flow rates
- **Normalizes against** maximum tank capacity (354 m³)

### No Scaling Needed!

Since we use volume (m³) directly, **no area scaling is required**:

**Python approach:**
```
error_vol = setpoint_vol - current_vol  # Error in m³
m_dot = Kp × error_vol                 # Mass flow (kg/s)
volume_flow = m_dot / density           # Volume flow (m³/s)
```

**C approach (identical):**
```
error_vol = setpoint_vol - current_vol  # Error in m³
volume_flow = Kp × error_vol            # Volume flow (m³/s)
m_dot = volume_flow × density           # Mass flow (kg/s)
```

**Gain conversion:**
```
C_Kp = Python_Kp / density
C_Kp = 1000 / 1000 = 1.0
```

No area term needed!

### Mathematical Derivation

**Python approach:**
```
error_vol = setpoint_vol - current_vol           # Error in m³
m_dot = Kp_python × error_vol                    # Mass flow in kg/s
volume_flow = m_dot / density                     # Volume flow in m³/s
```

**C approach (percentage-normalized):**
```
// Controller works with percentages
error_pct = setpoint_pct - current_pct           # Error in percentage (0-100%)

// Convert to actual volume for control calculation
error_vol = (error_pct / 100.0) × max_volume    # Error in m³
volume_flow = Kp_c × error_vol                   # Volume flow in m³/s

// Convert volume change back to percentage
dVolume = volume_flow × dt                       # m³
dLevel_pct = (dVolume / max_volume) × 100.0     # %
```

**For equivalence:**
```
Python: volume_flow = (Kp_python × error_vol) / density
C:      volume_flow = Kp_c × error_vol

Therefore:
Kp_c × error_vol = (Kp_python × error_vol) / density

Kp_c = Kp_python / density
```

**With Python values:**
```
Kp_python = 1000 kg/s
density = 1000 kg/m³

Kp_c = 1000 / 1000 = 1.0
```

**Simple!** No area scaling because we use volume (m³) directly.

## Controller Gain Values

### Base Scaling Factor
```c
// NO SCALING FACTOR NEEDED!
// We use volume (m³) directly, matching Python implementation
// Kp values are simply: Python_Kp / density
scaling_factor = 1.0  // No area scaling
```

### P Controller (Proportional Only)

**Python reference:** `Kp = 1000 kg/s`

**C implementation:**
```c
Kp = 1.0  // = 1000 / 1000 (Python_Kp / density)
Ki = 0.0
Kd = 0.0
```

**Why this value?**
- Directly matches Python baseline controller
- Simple conversion: Python_Kp / density = 1000 / 1000 = 1.0
- Provides reasonable response for step changes
- **Trade-off**: Will have steady-state error (no integral term)

### P Adaptive Controller (Higher Gain)

**Python reference:** `Kp = 5000 kg/s`

**C implementation:**
```c
Kp = 5.0  // = 5000 / 1000 (Python_Kp / density)
Ki = 0.0
Kd = 0.0
```

**Why 5x higher?**
- Directly matches Python Kp3 = 5000
- Simple conversion: 5000 / 1000 = 5.0
- Faster response to large errors
- Adaptive: Can adjust gain based on error magnitude
- **Trade-off**: More aggressive, may oscillate

### PD Controller (Proportional-Derivative)

**C implementation:**
```c
Kp = 0.40
Ki = 0.0
Kd = 0.60
```

**Why these values?**
- **Lower Kp (0.40)**: Reduced to prevent overshoot
- **Kd (0.60)**: Dampens oscillations, ratio Kd/Kp = 1.5
  - Higher than Kp to provide strong damping
  - Typical PD ratio: Kd = (1 to 2) × Kp
- **Trade-off**: Faster settling, less overshoot, but still has steady-state error

### PD Adaptive Controller

**C implementation:**
```c
Kp = 2.8
Ki = 0.0
Kd = 0.45
```

**Why these values?**
- **Higher Kp (2.8)**: More aggressive for large errors
- **Kd (0.45)**: Ratio Kd/Kp ≈ 0.16 (less damping than regular PD)
- Adaptive behavior allows gain scheduling based on error

### PI Controller (Proportional-Integral)

**C implementation:**
```c
Kp = 0.30
Ki = 0.08
Kd = 0.0
```

**Why these values?**
- **Lower Kp (0.30)**: Conservative to prevent overshoot
- **Ki (0.08)**: Small integral gain to eliminate steady-state error
  - Ratio Ki/Kp ≈ 0.27
  - Slow integration prevents integral windup
- **Key benefit**: Zero steady-state error
- **Trade-off**: May have some overshoot, slower than PD

### PI Adaptive Controller

**C implementation:**
```c
Kp = 0.80
Ki = 0.08
Kd = 0.0
```

**Why these values?**
- **Higher Kp (0.80)**: Faster response than regular PI
- **Same Ki (0.08)**: Conservative integral to avoid windup
- Ratio Ki/Kp = 0.10 (less aggressive than regular PI)

### PID Controller (All Three Terms)

**C implementation:**
```c
Kp = 0.35
Ki = 0.08
Kd = 0.50
```

**Why these values?**
- **Balanced approach**: All three terms work together
- **Kp (0.35)**: Moderate proportional action
- **Ki (0.08)**: Eliminates steady-state error
- **Kd (0.50)**: Strong damping, ratio Kd/Kp ≈ 1.43
- **Ratios**:
  - Ki/Kp = 0.23 (slow integration)
  - Kd/Kp = 1.43 (strong derivative damping)
- **Benefits**: Fast response, no steady-state error, minimal overshoot

### PID Adaptive Controller

**C implementation:**
```c
Kp = 1.0
Ki = 0.08
Kd = 0.50
```

**Why these values?**
- **Higher Kp (1.0)**: More aggressive response
- **Same Ki and Kd**: Proven integral and derivative values
- **Ratios**:
  - Ki/Kp = 0.08 (very slow integration)
  - Kd/Kp = 0.50 (balanced damping)
- Adaptive: Can adjust Kp based on error magnitude

## Tuning Methodology

### 1. Ziegler-Nichols Method (Not Used Here)
- Find ultimate gain (Ku) and period (Tu)
- Apply formulas:
  - P: Kp = 0.5 × Ku
  - PI: Kp = 0.45 × Ku, Ki = 1.2 × Kp / Tu
  - PID: Kp = 0.6 × Ku, Ki = 2 × Kp / Tu, Kd = Kp × Tu / 8

### 2. Trial and Error Method (Used Here)
1. **Start with P controller**:
   - Increase Kp until oscillation occurs
   - Back off to 50-70% of that value
   - Result: Kp_base = 1.0 (scaled to 78.54)

2. **Add Derivative (PD)**:
   - Start with Kd = 0.5 × Kp
   - Adjust to reduce overshoot
   - Result: Kd = 0.60 × Kp

3. **Add Integral (PI)**:
   - Start with Ki = 0.1 × Kp
   - Reduce if oscillation or overshoot occurs
   - Result: Ki = 0.08 × Kp

4. **Combine all three (PID)**:
   - Use balanced values from PD and PI tuning
   - Fine-tune for optimal performance

### 3. Gain Scheduling (Adaptive Controllers)
- Monitor error magnitude
- Adjust Kp based on error:
  ```c
  if (|error| > threshold) {
      Kp_effective = Kp_base × scale_factor  // Higher gain for large errors
  } else {
      Kp_effective = Kp_base                  // Normal gain for small errors
  }
  ```

## Time Step Considerations

### Discrete Control with dt = 0.04s

The discrete-time implementation affects gain selection:

**Derivative term:**
```c
derivative = (error - previous_error) / dt
derivative = (error - previous_error) / 0.04
derivative = 25 × (error - previous_error)
```
- Smaller dt → Larger derivative values
- Kd must be tuned accordingly

**Integral term:**
```c
integral += error × dt
integral += error × 0.04
```
- Smaller dt → Slower accumulation
- Ki must be larger for same effect

**Stability condition:**
```
For stability: dt < 2 / (Kp × max_process_gain)
With Kp = 78.54, dt = 0.04s is well within stable region
```

## Physical Interpretation

### Water Tank Dynamics

The tank system has natural characteristics:

1. **Time constant (τ)**:
   ```
   τ = Area / (outflow_coefficient × √(2gh))
   ```
   For this system: τ ≈ 10-20 seconds

2. **Desired settling time**: ~20-30 seconds
   ```
   Settling time ≈ 4τ_closed_loop
   Target: τ_closed_loop ≈ 5-7 seconds
   ```

3. **Gain selection**:
   ```
   Kp should make: τ_closed_loop = τ_open_loop / (1 + Kp)
   
   For τ_open_loop ≈ 15s and target τ_closed_loop ≈ 2s:
   2 = 15 / (1 + Kp)
   Kp ≈ 6.5 (unscaled) → 6.5 × 78.54 ≈ 510
   
   But we use Kp = 78.54 (more conservative) to avoid overshoot
   ```

## Summary Table

| Controller Type | Kp | Ki | Kd | Characteristics |
|----------------|-----|-----|-----|-----------------|
| P              | 1.0         | 0           | 0           | Fast, steady-state error |
| P Adaptive     | 5.0         | 0           | 0           | Very fast, may oscillate |
| PD             | 0.40        | 0           | 0.60        | Fast, damped, steady-state error |
| PD Adaptive    | 2.8         | 0           | 0.45        | Aggressive, damped |
| PI             | 0.30        | 0.08        | 0           | Slow, no steady-state error |
| PI Adaptive    | 0.80        | 0.08        | 0           | Moderate, no steady-state error |
| PID            | 0.35        | 0.08        | 0.50        | Balanced, optimal performance |
| PID Adaptive   | 1.0         | 0.08        | 0.50        | Fast, optimal performance |

## Key Takeaways

1. **Percentage normalization provides clarity**: Level/setpoint displayed as 0-100%, internally converted to volume (m³) for physics. Maximum volume: **354 m³** (calculated from area × height: 78.54 m² × 4.507 m)

2. **Simple gain conversion**: No area scaling needed, just divide Python gains by density (Kp_c = Kp_python / 1000)

3. **Trade-offs exist**:
   - Higher Kp → Faster response but more overshoot
   - Ki eliminates steady-state error but adds overshoot
   - Kd reduces overshoot but is sensitive to noise

3. **Typical ratios** (unscaled):
   - PD: Kd/Kp ≈ 1-2
   - PI: Ki/Kp ≈ 0.1-0.3
   - PID: Balanced combination

4. **Time step matters**: With dt = 0.04s, derivative and integral gains must be tuned for discrete-time implementation

5. **Adaptive controllers**: Use gain scheduling to adjust Kp based on error magnitude for better performance across different operating conditions

## References

- Python reference: `calculus_sim_waterTanks_Kp_controller.py`
- Ziegler-Nichols tuning method
- PID controller theory and applications
