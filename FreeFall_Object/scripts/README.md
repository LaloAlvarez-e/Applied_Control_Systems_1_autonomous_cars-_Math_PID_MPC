# Analysis Scripts

Python tools for analyzing and visualizing the FreeFall_Object simulation results.

---

## Available Scripts (4 total)

### 1. analyze_comprehensive.py ⭐
**Purpose**: Statistical analysis of multi-parameter simulation results

**Features**:
- Analyzes 550+ simulations across angles, ball positions, and train positions
- Calculates catch rates by angle, distance, and initial conditions
- Generates comprehensive statistics and visualizations
- Creates heatmaps showing performance across parameter space

**Usage**:
```powershell
# From FreeFall_Object root
.\.venv\Scripts\python.exe scripts\analyze_comprehensive.py
```

**Outputs**:
- `plots/comprehensive_analysis.png` - 4-subplot summary
- `plots/angle_specific_analysis.png` - Detailed angle analysis
- `analysis_results.csv` - Raw statistics

---

### 2. animate_realtime.py ⭐
**Purpose**: Create 7-plot animated visualizations (Mark Misin style)

**Features**:
- **4×3 grid layout** with physical animation + 6 time-series plots
- Shows: velocity, acceleration, force, error, error derivative, error integral
- Real-time catch detection with visual feedback
- Supports both display-only and video export modes
- Backward compatible with old CSV format

**Usage**:
```powershell
# Display specific file
.\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_A30_BallX060_TrainX010.csv --display-only --speed 2.0

# Generate video
.\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_A45_BallX080_TrainX020.csv --fps 30
```

**Arguments**:
- `--file`: Specific CSV file to animate
- `--csv-dir`: Directory containing CSV files (default: `csv_data`)
- `--output-dir`: Output directory for videos (default: `animations`)
- `--speed`: Animation speed multiplier (default: 1.0)
- `--fps`: Frames per second (default: 30)
- `--display-only`: Show animation without saving

---

### 3. visualize_angles.py
**Purpose**: Generate angle comparison plots

**Features**:
- Creates summary comparison across all angles
- Generates detailed plots for each angle
- Shows position, velocity, force, and error over time

**Usage**:
```powershell
.\.venv\Scripts\python.exe scripts\visualize_angles.py
```

**Outputs**:
- `plots/angles/angle_comparison.png` - Overview of all angles
- `plots/angles/angle_XX_detail.png` - Detailed plots for each angle

---

### 4. run_all_angle_animations.py
**Purpose**: Batch generate animations for all angle scenarios

**Usage**:
```powershell
.\.venv\Scripts\python.exe scripts\run_all_angle_animations.py
```

---

## Removed Scripts

The following scripts have been removed as they're no longer needed:
- ❌ `compare_gains.py` - Obsolete (was for old single-angle simulations)
- ❌ `visualize_simulation.py` - Superseded by `animate_realtime.py`
- ❌ `animate_angle.ps1` - Obsolete (was for old file naming)
- ❌ `animate_angle.bat` - Obsolete (was for old file naming)
- ❌ `verify_paths.ps1` - Temporary testing script

---

## Quick Start Workflow

```powershell
# 1. Build and run simulation
.\build.ps1
.\build\bin\freefall_object.exe

# 2. Analyze results
.\.venv\Scripts\python.exe scripts\analyze_comprehensive.py

# 3. View sample animation (7 plots)
.\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_A30_BallX060_TrainX010.csv --display-only --speed 2.0

# 4. Generate angle comparisons
.\.venv\Scripts\python.exe scripts\visualize_angles.py
```

---

## Data Format

### NEW: 8-column CSV format
```csv
time,train_position,falling_object_position,applied_force,train_velocity,train_acceleration,error_derivative,error_integral
0.000000,10.000000,100.000000,0.000000,0.000000,0.000000,0.000000,0.000000
```

**New columns**:
- `train_velocity` - Train velocity (m/s)
- `train_acceleration` - Train acceleration (m/s²)
- `error_derivative` - Error rate of change de/dt (m/s)
- `error_integral` - Accumulated error ∫e dt (m·s)

### Legacy: 4-column format (still supported)
```csv
time,train_position,falling_object_position,applied_force
```

Scripts auto-detect and handle both formats.

---

## Path Handling

All scripts use **root-relative paths** via `Path(__file__).parent.parent`:

```python
from pathlib import Path
root_dir = Path(__file__).parent.parent  # FreeFall_Object/
csv_dir = root_dir / "csv_data"
output_dir = root_dir / "plots"
```

**Always run from FreeFall_Object root**:
```powershell
.\.venv\Scripts\python.exe scripts\<script_name>.py  # ✅ Correct
```

---

## Dependencies

Required packages:
- Python 3.9+
- pandas
- numpy
- matplotlib

Install via:
```powershell
.\.venv\Scripts\pip.exe install pandas numpy matplotlib
```

---

## Troubleshooting

### "No CSV files found"
**Solution**: Run simulation first
```powershell
.\build\bin\freefall_object.exe
```

### "Module not found"
**Solution**: Install dependencies
```powershell
.\.venv\Scripts\python.exe -m pip install pandas numpy matplotlib
```

### Animation doesn't display
**Solution**: Use `--display-only` flag
```powershell
.\.venv\Scripts\python.exe scripts\animate_realtime.py --file <file> --display-only
```

---

## Performance

- **analyze_comprehensive.py**: ~5-10 seconds for 550 files
- **animate_realtime.py**: ~10-30 seconds per animation
- **visualize_angles.py**: ~30-60 seconds for all angles
- **run_all_angle_animations.py**: ~10-20 minutes total
