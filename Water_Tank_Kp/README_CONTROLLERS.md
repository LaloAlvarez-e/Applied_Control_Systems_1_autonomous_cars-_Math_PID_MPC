# Water Tank Control System - Controller Examples

This project demonstrates P, PI, PD, and PID controller implementations for a water tank system.

## Controller Types

### 1. Proportional (P) Controller
**File:** `main.c` → Executable: `water_tank_kp.exe`

**Gains:**
- Kp = 0.2 (Proportional gain)

**Control Law:**
```
u(t) = Kp * e(t)
```

**Characteristics:**
- Simple and fast response
- May have steady-state error
- No integral or derivative action

---

### 2. Proportional-Integral (PI) Controller
**File:** `main_pi.c` → Executable: `water_tank_pi.exe`

**Gains:**
- Kp = 0.2 (Proportional gain)
- Ki = 0.05 (Integral gain)

**Control Law:**
```
u(t) = Kp * e(t) + Ki * ∫e(τ)dτ
```

**Characteristics:**
- Eliminates steady-state error
- Integral term accumulates error over time
- Can overshoot if Ki is too large

---

### 3. Proportional-Derivative (PD) Controller
**File:** `main_pd.c` → Executable: `water_tank_pd.exe`

**Gains:**
- Kp = 0.3 (Proportional gain)
- Kd = 0.5 (Derivative gain)

**Control Law:**
```
u(t) = Kp * e(t) + Kd * de(t)/dt
```

**Characteristics:**
- Adds damping to reduce overshoot
- Anticipates future error
- Sensitive to noise in the derivative term
- May have steady-state error (no integral action)

---

### 4. Proportional-Integral-Derivative (PID) Controller
**File:** `main_pid.c` → Executable: `water_tank_pid.exe`

**Gains:**
- Kp = 0.3 (Proportional gain)
- Ki = 0.05 (Integral gain)
- Kd = 0.4 (Derivative gain)

**Control Law:**
```
u(t) = Kp * e(t) + Ki * ∫e(τ)dτ + Kd * de(t)/dt
```

**Characteristics:**
- Combines all three control actions
- Eliminates steady-state error (integral)
- Reduces overshoot (derivative)
- Most versatile but requires careful tuning

---

## Building and Running

### Build all controllers:
```bash
cmake --build build
```

### Run individual controllers:
```bash
# P Controller
echo "" | .\build\bin\water_tank_kp.exe

# PI Controller
echo "" | .\build\bin\water_tank_pi.exe

# PD Controller
echo "" | .\build\bin\water_tank_pd.exe

# PID Controller
echo "" | .\build\bin\water_tank_pid.exe
```

## System Parameters

**Water Tank:**
- Initial level: 0.5 m
- Target setpoint: 2.0 m (changes to 1.5 m at t=25s)
- Tank area: 1.0 m²
- Outflow coefficient: 0.1
- Maximum inflow: 0.5 m³/s

**Simulation:**
- Time step (dt): 0.1 s
- Total time: 50 s
- Number of steps: 500

## Controller Structure

Each controller implementation includes:
- **ControllerParams**: Kp, Ki, Kd gains
- **ControllerState**: integral and previousError for stateful controllers
- **ControllerConfig**: Complete configuration with callbacks and time step

## Error Handling

All functions return `ErrorCode`:
- `ERROR_SUCCESS` (0): Operation completed successfully
- `ERROR_NULL_POINTER`: Null pointer provided
- `ERROR_INVALID_PARAMETER`: Invalid parameter value
- `ERROR_CALLBACK_FAILED`: Callback function failed

## Key Features

- **Modular Design**: Separate error calculation from control law
- **State Management**: Integral and derivative terms maintained in ControllerState
- **Callback Architecture**: Flexible system model and controller callbacks
- **Type Safety**: Strong typing with enums and structures
- **Error Propagation**: Consistent error handling throughout
