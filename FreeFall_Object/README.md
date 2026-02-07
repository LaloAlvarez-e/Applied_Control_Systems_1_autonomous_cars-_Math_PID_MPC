# Train Catching Falling Ball - PID Control System

Comprehensive simulation system for analyzing PID controller performance in a train catching a falling ball scenario on inclined surfaces.

## Quick Start

### One-Command Complete Workflow
```powershell
# Build, run simulation, and generate all analyses
.\run_all.ps1
```

### Manual Steps

#### 1. Build C Simulation
```powershell
# Using build script
.\build.ps1

# Or manually
cd build
cmake ..\code
cmake --build .
cd ..
```

#### 2. Run Simulation
```powershell
# Generates 550+ CSV files in csv_data/
.\build\bin\freefall_object.exe
```

#### 3. Analyze Results
```powershell
# Comprehensive analysis
.\.venv\Scripts\python.exe scripts\analyze_comprehensive.py

# View results
Start-Process plots\comprehensive_analysis.png
Start-Process plots\angle_specific_analysis.png
```

#### 4. Generate Visualizations
```powershell
# Angle comparison plots
.\.venv\Scripts\python.exe scripts\visualize_angles.py

# View angle comparison
Start-Process plots\angles\angle_comparison.png
```

#### 5. View Animations
```powershell
# Animate specific scenario
.\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_A45_BallX060_TrainX010.csv --display-only --speed 2.0
```

---

## Project Structure

```
FreeFall_Object/
├── 📁 build/                    CMake build outputs
│   └── bin/freefall_object.exe  Main executable
├── 📁 csv_data/                 Simulation results (550+ files)
├── 📁 plots/                    Generated visualizations
├── 📁 scripts/                  Python analysis tools
│   ├── analyze_comprehensive.py  Multi-parameter analysis
│   ├── animate_realtime.py       Real-time animations
│   └── compare_gains.py          PID gain comparison
├── 📁 documentation/            Complete documentation
│   ├── BUILD_SUMMARY.md
│   ├── QUICK_COMMANDS.md
│   └── SYSTEM_OVERVIEW.md
├── 📁 diagrams/                 System diagrams
├── 📁 .venv/                    Python virtual environment
├── main.c                       Main simulation loop
├── controller.c                 PID controller implementation
├── fallingobject.c              Train physics model
├── plot.c                       Data logging
├── visualize_angles.py          Angle comparison plots
└── CMakeLists.txt               Build configuration
```

---

## System Overview

### Physics Model
- **Train**: 100 kg mass, 3000 N max force (a_max = 30 m/s²)
- **Ball**: Falls from 100m height at fixed X position
- **Surface**: Inclined at angle θ (0° to 85°)
- **Integration**: Trapezoidal method for velocity and position

### PID Controller
- **Kp = 500**: Proportional gain (scaled for 100kg mass)
- **Ki = 50**: Integral gain (steady-state error elimination)
- **Kd = 200**: Derivative gain (damping at high speeds)

### Simulation Parameters
- **10 Angles**: 0°, 10°, 15°, 22°, 30°, 36°, 45°, 64°, 77°, 85°
- **11 Ball Positions**: 0-100m (step 10m)
- **10 Train Starting Positions**: 0-90m (step 10m)
- **550 Total Simulations**: All valid combinations
- **25 Hz Control Rate**: 0.04s time step

---

## Key Results

### Overall Performance
- **Success Rate**: 67.1% (369/550 catches)
- **Flat Surfaces (0°-22°)**: 100% success
- **Moderate Slopes (30°-36°)**: 90-98% success
- **Steep Slopes (45°)**: 60% success
- **Very Steep (64°-85°)**: 0-16% success

### Distance Impact
| Distance | Success Rate | Avg Time |
|----------|-------------|----------|
| 0-20m    | 75.0%       | 0.89s    |
| 20-40m   | 71.8%       | 1.37s    |
| 40-60m   | 66.2%       | 1.85s    |
| 60-80m   | 61.1%       | 2.24s    |
| 80-100m  | 54.0%       | 2.59s    |

---

## Documentation

Complete documentation available in `documentation/`:

- **[BUILD_SUMMARY.md](documentation/BUILD_SUMMARY.md)** - Build status and file structure
- **[QUICK_COMMANDS.md](documentation/QUICK_COMMANDS.md)** - Common commands reference
- **[SYSTEM_OVERVIEW.md](documentation/SYSTEM_OVERVIEW.md)** - Technical details
- **[ANGLE_STUDY_RESULTS.md](documentation/ANGLE_STUDY_RESULTS.md)** - Analysis results
- **[scripts/README.md](scripts/README.md)** - Python scripts guide

---

## Development

### Prerequisites
- CMake 3.10+
- C compiler (MSVC, GCC, or Clang)
- Python 3.8+ with matplotlib, numpy, pandas

### Building from Source
```powershell
# Create build directory
mkdir build
cd build

# Configure
cmake ..

# Build
cmake --build .

# Run
.\bin\freefall_object.exe
```

### Python Environment Setup
```powershell
# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install matplotlib numpy pandas
```

---

## Usage Examples

### Run Specific Angle Simulations
The C program automatically runs all 550 combinations. To analyze specific scenarios:

```powershell
# Analyze 45° angle scenarios
.\.venv\Scripts\python.exe -c "import pandas as pd; import glob; files = glob.glob('csv_data/PID_A45_*.csv'); print(f'Found {len(files)} files for 45° angle')"
```

### Create Custom Visualizations
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load specific scenario
df = pd.read_csv('csv_data/PID_A45_BallX060_TrainX010.csv')
df.columns = ['time', 'train_x', 'ball_y', 'force']

# Plot train position
plt.plot(df['time'], df['train_x'])
plt.xlabel('Time (s)')
plt.ylabel('Train Position (m)')
plt.show()
```

### Batch Process Animations
```powershell
# See run_all_angle_animations.py for batch processing examples
.\.venv\Scripts\python.exe run_all_angle_animations.py
```

---

## Troubleshooting

### CSV files not found
```powershell
# Run simulation first
.\build\bin\freefall_object.exe
```

### Python script errors
```powershell
# Verify virtual environment
.\.venv\Scripts\python.exe --version

# Reinstall dependencies
.\.venv\Scripts\pip.exe install --upgrade matplotlib numpy pandas
```

### Build errors
```powershell
# Clean build
cd build
cmake --build . --clean-first
```

---

## License

Educational project for control systems study.

## Author

Applied Control Systems - Autonomous Cars Study

