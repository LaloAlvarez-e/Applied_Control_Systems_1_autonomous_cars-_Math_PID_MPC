# System Diagrams: Train Tracking Falling Object

This directory contains comprehensive technical diagrams illustrating the complete control system with three interacting components.

## Generated Diagrams

### 1. System Overview (`01_system_overview.png`)
**Complete system visualization showing all three components together**

- **Falling Object** (red): Starts at variable height (x₀, y₀) with initial velocity
- **Train** (blue): Moves along inclined track, starts at position s₀
- **Track/Line** (black): Inclined at angle θ from horizontal
- Shows: Object trajectory, train position, interception point, forces, and coordinate system

**Key Features:**
- Object initial position: (x₀, y₀) - configurable
- Train initial position: s₀ along track - configurable  
- Track angle: θ degrees - configurable
- Target interception point visualization
- Force vectors on both systems

---

### 2. Falling Object Physics (`02_falling_object_physics.png`)
**System 1: Detailed physics of object in free fall**

**Equations of Motion:**
```
Position:
  x(t) = x₀ + v_x0·t
  y(t) = y₀ + v_y0·t - ½g·t²

Velocity:
  v_x(t) = v_x0
  v_y(t) = v_y0 - g·t

Forces:
  F_y = -mg - C_d·v_y²·sign(v_y)
  F_x = -C_d·v_x²·sign(v_x)
```

**Variable Initial Conditions:**
- Position (x₀, y₀): Can start anywhere
- Velocity (v_x0, v_y0): Can be dropped (0, 0) or thrown with initial velocity
- Mass: m (kg)
- Drag coefficient: C_d

**Diagram Shows:**
- Gravity force vector (F_g = mg)
- Drag force (F_drag = C_d·v²)
- Velocity vector
- Parabolic trajectory
- Multiple time snapshots

---

### 3. Train on Inclined Track Physics (`03_train_track_physics.png`)
**System 2: Detailed physics of train constrained to angled track**

**Track Parameterization:**
```
x(s) = x₀ + s·cos(θ)
y(s) = y₀ + s·sin(θ)
```

Where:
- (x₀, y₀) = Track origin point (configurable)
- θ = Track angle from horizontal (configurable)
- s = Position parameter along track (meters from origin)

**Equation of Motion (along track):**
```
m·(d²s/dt²) = F_applied - mg·sin(θ) - C_d·v²
```

**Force Components Shown:**
- F_applied: Control force (red) - from PID controller
- mg: Gravity force (blue) - downward
- mg·sin(θ): Tangential component (cyan, dashed) - along track
- mg·cos(θ): Normal component (magenta, dashed) - perpendicular to track
- N: Normal force (lime) - reaction from track
- Tangent direction (t̂): Green arrow - direction of motion
- Normal direction (n̂): Orange arrow - perpendicular to motion

**Variable Parameters:**
- Initial position: s₀ (any value along track)
- Track origin: (x₀, y₀)
- Track angle: θ (0° to 90°)
- Mass: m
- Drag: C_d

---

### 4. Track Geometry (`04_track_geometry.png`)
**System 3: Track configurations and mathematical formulations**

Four subplots showing:

#### a) Horizontal Track (θ = 0°)
- Equation: y = constant
- s = x (position along track equals x coordinate)
- No gravity component along track (mg·sin(0°) = 0)

#### b) Inclined Track (θ = 30°)
- Moderate incline
- Gravity component: mg·sin(30°) ≈ 0.5·mg
- Shows track origin, angle annotation, train position

#### c) Steep Track (θ = 60°)
- Steep incline
- Large gravity component: mg·sin(60°) ≈ 0.87·mg
- More challenging control problem

#### d) General Equations & Transformations
**Complete mathematical reference:**

**Track Parameterization:**
```
Parametric:   x(s) = x₀ + s·cos(θ)
              y(s) = y₀ + s·sin(θ)

Cartesian:    y - y₀ = tan(θ)·(x - x₀)
```

**Coordinate Transformations:**
```
World → Track:  s = √[(x-x₀)² + (y-y₀)²]
Track → World:  Use parametric equations
```

**Velocity & Acceleration:**
```
Along track:     v = ds/dt,  a = d²s/dt²
World frame:     vₓ = v·cos(θ),  vᵧ = v·sin(θ)
```

**Force Balance:**
```
m·a = F_applied - mg·sin(θ) - C_d·v²
```

---

### 5. Interception Geometry (`05_interception_geometry.png`)
**Problem: When and where does the train catch the falling object?**

**Interception Condition:**
```
Object position:  x_obj(t) = x_obj0
                  y_obj(t) = y_obj0 - ½g·t²

Train position:   x_train(t) = x₀ + s(t)·cos(θ)
                  y_train(t) = y₀ + s(t)·sin(θ)

Interception when:
  x_obj(t) = x_train(t)  AND  y_obj(t) = y_train(t)
```

**Control Objective:**
Train must reach position s_target before time t_intercept

**Diagram Shows:**
- Object trajectory (red dashed line) with time markers
- Train initial position (blue square)
- Train target position at interception (blue diamond)
- Interception point (green star)
- Distance train must travel (Δs)
- Time to interception (t_intercept)

**Key Insight:**
The controller must:
1. Calculate where object trajectory intersects track line
2. Determine time when intersection occurs
3. Compute required train velocity to reach that point in time
4. Apply appropriate force to achieve desired velocity profile

---

### 6. Control System Block Diagram (`06_control_system_block_diagram.png`)
**Complete control system architecture**

**Signal Flow:**
```
Falling Object → Calculate → Error → PID → Applied → Train → Position
   Position      Target s   (e=Δs)  Control  Force   Dynamics  Output
                                       ↑                    ↓
                                       └────── Feedback ────┘
```

**Components:**

1. **Falling Object Position**: Calculates (x_obj, y_obj) from free-fall physics
2. **Calculate Target s(t)**: Converts object position to train's track coordinate
3. **Error Calculation**: e = s_target - s_actual
4. **PID Controller**: Generates force command
   - F = Kp·e + Ki·∫e·dt + Kd·(de/dt)
5. **Train Dynamics**: Physical system with disturbances
6. **Position Output**: s(t) fed back to error calculation

**Disturbances:**
- Gravity: mg·sin(θ) (along track)
- Drag: C_d·v² (opposing motion)

---

## System Parameters Summary

### Configurable Parameters

| System | Parameter | Symbol | Description | Typical Range |
|--------|-----------|--------|-------------|---------------|
| **Falling Object** | Initial X Position | x₀ | Horizontal position | 0 - 100 m |
| | Initial Y Position | y₀ | Initial height | 0 - 100 m |
| | Initial X Velocity | v_x0 | Horizontal velocity | -10 to +10 m/s |
| | Initial Y Velocity | v_y0 | Vertical velocity | -10 to +10 m/s |
| | Mass | m_obj | Object mass | 0.1 - 10 kg |
| | Drag Coefficient | C_d_obj | Air resistance | 0 - 1 |
| **Train** | Initial Position | s₀ | Position along track | 0 - 100 m |
| | Mass | m_train | Train mass | 0.5 - 50 kg |
| | Max Force | F_max | Control limit | 10 - 500 N |
| | Drag Coefficient | C_d_train | Rolling resistance | 0 - 1 |
| **Track** | Origin X | x₀ | Track start X | 0 - 100 m |
| | Origin Y | y₀ | Track start Y | 0 - 100 m |
| | Angle | θ | Inclination | 0° - 90° |
| | Length | L | Track length | 50 - 200 m |

### Physical Constants
- Gravity: g = 9.81 m/s²

---

## Usage

### Viewing Diagrams
Open any PNG file to view high-resolution (300 DPI) diagrams.

### Regenerating Diagrams
```bash
python generate_system_diagrams.py
```

### Dependencies
- Python 3.x
- matplotlib
- numpy

### Installation
```bash
pip install matplotlib numpy
```

---

## Physics Summary

### Free Fall Object
- **2D projectile motion** with gravity and optional drag
- **Independent variables**: x, y positions and velocities
- **Can start anywhere** with any initial velocity
- Trajectory determined by classical mechanics

### Train on Track
- **1D constrained motion** along inclined line
- **Position parameter**: s (meters along track)
- **Must stay on track**: geometric constraint
- Affected by gravity component along track: mg·sin(θ)

### Track/Line
- **Geometric constraint** defining allowed train motion
- **Parameterized** by angle θ and origin (x₀, y₀)
- **Transforms** between world coordinates (x, y) and track coordinate s

### Control Problem
Train must intercept falling object by:
1. Predicting object trajectory
2. Computing intersection with track
3. Applying force to reach intersection point in time
4. Accounting for gravity and drag disturbances

---

## Educational Notes

These diagrams are designed for:
- **Control systems education**: PID control, feedback systems
- **Classical mechanics**: Projectile motion, forces on inclined planes
- **Applied mathematics**: Coordinate transformations, parametric equations
- **Engineering design**: System modeling, constraint satisfaction

Each diagram includes:
- ✓ Clear force vectors with labels
- ✓ Mathematical equations in proper notation
- ✓ Color-coded components for easy identification
- ✓ Coordinate systems and reference frames
- ✓ Realistic physical parameters

---

## File Organization

```
diagrams/
├── generate_system_diagrams.py    # Python script to generate all diagrams
├── README.md                      # This file
├── 01_system_overview.png         # Complete system visualization
├── 02_falling_object_physics.png  # Object free fall details
├── 03_train_track_physics.png     # Train on incline details
├── 04_track_geometry.png          # Track configurations
├── 05_interception_geometry.png   # Interception problem
└── 06_control_system_block_diagram.png  # Control architecture
```

---

## Related Files

- `../fallingobject.h` - C header defining data structures
- `../fallingobject.c` - C implementation of physics models
- `../main.c` - Simulation main program
- `../controller.c` - PID controller implementations
- `../README.md` - Project overview and build instructions

---

*Generated for Train Tracking Falling Object Control System*
*Date: January 2026*
