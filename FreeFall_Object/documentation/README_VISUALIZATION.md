# Train Catching Falling Ball - Horizontal Interception System

This project simulates a **train moving horizontally to catch a falling ball**.

## Problem Description

**Scenario:**
- A ball is dropped from height Y=100m at horizontal position X=60m
- A train starts at horizontal position X=10m on the ground (Y=0m)
- The train must move horizontally to reach X=60m before the ball lands

**Physics:**
- **Ball:** Falls vertically according to free-fall: y(t) = 100 - 0.5×g×t²
- **Train:** Moves horizontally (X-axis) controlled by PID controllers
- **Goal:** Train reaches target X=60m in time to catch the falling ball

**Control Challenge:**
Train must calculate optimal horizontal velocity to reach the interception point before the ball hits the ground (~4.5 seconds fall time).

## Workflow Overview

```
┌─────────────────┐         ┌──────────────┐         ┌────────────────┐
│ C Simulation    │  CSV    │  CSV Data    │ Python  │   Plots &      │
│ (freefall_      │──────>  │  Files       │────────>│   Animations   │
│  object.exe)    │ Export  │ (csv_data/)  │  Read   │   (plots/)     │
└─────────────────┘         └──────────────┘         └────────────────┘
```

## System Architecture

**Two-Stage Workflow:**
1. **C Simulation** → Generates CSV data files with train and ball positions
2. **Python Visualization** → Creates plots and animations from CSV data

**Advantages:**
✅ **Separation of Concerns**: Physics simulation (C) separate from visualization (Python)  
✅ **Flexibility**: Re-plot data without re-running simulation  
✅ **Real-time Animation**: Shows train moving horizontally to catch falling ball
✅ **No gnuplot Dependency**: Pure Python visualization  
✅ **Better Analysis**: 8 subplots showing position, force, error, velocities, phase portrait, metrics  

## Step 1: Run C Simulation

The C program runs the physics simulation and saves all data to CSV files.

### Build and Run:
```bash
cd FreeFall_Object/build
cmake --build .
cd ..
./build/bin/freefall_object.exe
```

### What It Does:
- Runs 24 simulations (8 controllers × 3 integration methods)
- Saves data to `csv_data/*.csv` (one file per simulation)
- Each CSV contains: time, train_position, falling_object_position, applied_force

### Output:
```
csv_data/
├── P_Controller.csv
├── P_Adaptive_Controller.csv
├── PI_Controller.csv
├── PD_Controller.csv
├── PID_Controller.csv
├── ... (24 files total)
```

### CSV Format:
```csv
time,train_position,falling_object_position,applied_force
0.000000,10.000000,100.000000,0.000000
0.040000,10.019620,99.992152,9.810000
0.080000,10.078491,99.968608,19.620000
...
```

**Data columns:**
- `time`: Simulation time (seconds)
- `train_position`: Train's horizontal X position (meters)
- `falling_object_position`: Ball's vertical Y height (meters)
- `applied_force`: Control force applied to train (Newtons)

## Step 2: Python Visualization

The Python script reads CSV files and creates high-quality plots.

### Basic Usage:
```bash
python visualize_simulation.py
```

This creates static plots for all CSV files in the `plots/` directory.

### Advanced Options:
```bash
# Create animations (requires FFmpeg)
python visualize_simulation.py --animate

# Control animation speed
python visualize_simulation.py --animate --speed 2.0  # 2x speed

# Process single file
python visualize_simulation.py --file csv_data/PID_Controller.csv

# Custom output directories
python visualize_simulation.py --plot-dir my_plots --anim-dir my_animations
```

### Command-Line Arguments:
| Argument | Default | Description |
|----------|---------|-------------|
| `--csv-dir` | `csv_data` | Directory containing CSV files |
| `--plot-dir` | `plots` | Output directory for static plots |
| `--anim-dir` | `animations` | Output directory for animations |
| `--animate` | False | Create MP4 animations (requires FFmpeg) |
| `--speed` | 1.0 | Animation speed multiplier |
| `--file` | None | Process single CSV file |

## Generated Plots

Each static plot includes **8 comprehensive subplots**:

1. **Position vs Time**: Train horizontal X position (blue) and Ball vertical Y height (red)
2. **2D Physical Space**: Shows train moving horizontally and ball falling vertically
3. **Control Force**: Applied force over time
4. **Tracking Error**: Difference between ball Y and train X positions
5. **Velocities**: Train and ball velocities
6. **Phase Portrait**: Error vs error rate (stability analysis)
7. **Initial vs Final Bar Chart**: Position comparison
8. **Performance Metrics**: Numerical summary (mean/RMS error, max force, distances traveled)

### Real-Time Animations

Use `animate_realtime.py` for dynamic visualization showing:
- **Physical Space (Main View)**: Ball falling vertically at X=60m, train moving horizontally from X=10m
- **Time Series Plots**: Position, force, and error evolution
- **Distance Indicators**: Horizontal and vertical separation between train and ball
- **Catch Detection**: Animation stops when train reaches ball (distance < 2m, height < 5m)
- **Ground and Markers**: Visual indicators for start/end positions

### Creating Animations:
```bash
# Display single controller animation (no save)
python animate_realtime.py --file csv_data/PID_Controller.csv --display-only --speed 2.0

# Save all animations as MP4 (requires FFmpeg)
python animate_realtime.py --speed 1.5

# Save specific controller type
python animate_realtime.py --file csv_data/PID_Controller.csv --speed 2.0
```

**Animation Features:**
- Stops automatically when train catches ball
- Shows horizontal train movement (X-axis)
- Shows vertical ball fall (Y-axis at X=60m)
- Distance tracking (horizontal and vertical)
- "CAUGHT!" message when interception succeeds
- Customizable speed (1.0 = normal, 2.0 = 2x speed)

### Installing FFmpeg (Windows):
```bash
# Option 1: Chocolatey
choco install ffmpeg

# Option 2: Download from https://ffmpeg.org/download.html
```

## Python Dependencies

Install required packages:
```bash
pip install matplotlib numpy pandas
```

For animations:
```bash
pip install ffmpeg-python  # Optional, for better FFmpeg integration
```

## File Structure

```
FreeFall_Object/
├── build/
│   └── bin/
│       └── freefall_object.exe          # C simulation executable
├── csv_data/                            # CSV data from C (generated)
│   ├── P_Controller.csv
│   ├── PI_Controller.csv
│   ├── PID_Controller.csv
│   └── ... (24 files)
├── plots/                               # Static plots from Python (generated)
│   ├── P_Controller.png
│   ├── PI_Controller.png
│   ├── PID_Controller.png
│   └── ... (24 files)
├── animations/                          # Animated MP4s (optional, generated)
│   ├── P_Controller.mp4
│   ├── PI_Controller.png
│   └── ...
├── diagrams/                            # System diagrams
│   ├── 01_system_overview.png
│   ├── 02_falling_object_physics.png
│   └── ...
├── visualize_simulation.py              # Python visualization script
├── plot.c                               # CSV export (C code)
├── plot.h                               # Plot interface
├── main.c                               # Simulation main
├── fallingobject.c                      # Physics model
├── controller.c                         # PID controllers
└── README.md                            # This file
```

## Workflow Examples

### Example 1: Quick Visualization
```bash
# Run simulation
./build/bin/freefall_object.exe

# Generate all plots
python visualize_simulation.py
```

### Example 2: Analyze Single Controller
```bash
# Run simulation (generates all CSVs)
./build/bin/freefall_object.exe

# View specific controller
python visualize_simulation.py --file csv_data/PID_Controller.csv
```

### Example 3: Create Presentation Materials
```bash
# Run simulation
./build/bin/freefall_object.exe

# Generate high-res plots and animations
python visualize_simulation.py --animate --speed 1.5
```

### Example 4: Custom Analysis
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load any CSV file
df = pd.read_csv('csv_data/PID_Controller.csv')

# Custom analysis
error = df['falling_object_position'] - df['train_position']
print(f"Mean absolute error: {abs(error).mean():.3f} m")
print(f"Max error: {error.max():.3f} m")

# Custom plot
plt.plot(df['time'], error)
plt.xlabel('Time (s)')
plt.ylabel('Error (m)')
plt.title('Custom Error Analysis')
plt.show()
```

## Data Analysis Tips

### Load Data:
```python
import pandas as pd

df = pd.read_csv('csv_data/PID_Controller.csv')
print(df.head())
```

### Common Calculations:
```python
# Tracking error
error = df['falling_object_position'] - df['train_position']

# Velocities (numerical derivative)
dt = df['time'].diff()
train_velocity = df['train_position'].diff() / dt
object_velocity = df['falling_object_position'].diff() / dt

# Statistics
print(f"Mean error: {error.mean():.3f} m")
print(f"RMS error: {(error**2).mean()**0.5:.3f} m")
print(f"Max force: {df['applied_force'].max():.3f} N")
```

### Compare Controllers:
```python
import glob
import pandas as pd

# Load all controllers
files = glob.glob('csv_data/*Controller.csv')

for file in files:
    df = pd.read_csv(file)
    error = df['falling_object_position'] - df['train_position']
    rms_error = (error**2).mean()**0.5
    print(f"{file}: RMS Error = {rms_error:.3f} m")
```

## Performance Metrics

The Python visualization processes:
- **24 CSV files** (1250 points each)
- **Generates 24 high-resolution plots**
- **Typical runtime**: 10-15 seconds
- **With animations**: 2-3 minutes (depends on FFmpeg)

## Troubleshooting

### Issue: "No CSV files found"
**Solution**: Run the C simulation first to generate CSV files

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution**: Install dependencies: `pip install matplotlib numpy pandas`

### Issue: "FFmpeg not found" (for animations)
**Solution**: Install FFmpeg or skip animations

### Issue: Plots look different from before
**Reason**: Python uses matplotlib instead of gnuplot (intentional improvement!)

## Future Enhancements

Possible additions:
- [ ] Real-time plotting during simulation (live updates)
- [ ] Interactive plots with zoom/pan (plotly/bokeh)
- [ ] Web dashboard for results
- [ ] Comparative analysis across controllers
- [ ] Automated report generation
- [ ] Parameter sweep visualization

## Related Files

- **C Simulation**: [fallingobject.c](fallingobject.c), [main.c](main.c), [controller.c](controller.c)
- **System Diagrams**: [diagrams/README.md](diagrams/README.md)
- **Build System**: [CMakeLists.txt](CMakeLists.txt)

---

*Last Updated: January 2026*
