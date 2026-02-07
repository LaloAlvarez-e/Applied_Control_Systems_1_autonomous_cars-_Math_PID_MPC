# Quick Start Guide - Train Catching Falling Ball

## 5-Minute Setup

### 1. Build & Run Simulation (C)

```bash
cd FreeFall_Object
mkdir build && cd build
cmake ..
cmake --build .
cd ..
./build/bin/freefall_object.exe
```

**✓ Output**: 24 CSV files in `csv_data/` directory

---

### 2. Generate Plots (Python)

```bash
python visualize_simulation.py
```

**✓ Output**: 24 high-res plots in `plots/` directory

---

### 3. View Animation

```bash
python animate_realtime.py --file csv_data/PID_Controller.csv --display-only --speed 2.0
```

**✓ Output**: Interactive animation showing train catching ball

---

## What You'll See

### Static Plot (8 subplots)
- Train horizontal position (X) vs time
- Ball vertical height (Y) vs time
- 2D physical space view (X-Y)
- Control force, error, velocities
- Performance metrics

### Real-Time Animation
- 🔵 Train moving horizontally (X: 10m → 60m)
- 🔴 Ball falling vertically (Y: 100m → 0m at X=60m)
- Distance indicators
- "CAUGHT!" when train intercepts ball

---

## Key Results

**PID Controller (Best):**
- Train reaches 61.97m at t=8.08s ✅
- Ball lands at X=60m, t=4.52s
- **SUCCESS**: Train catches ball!

**P Controller:**
- Train reaches only 58.24m ❌
- **FAILURE**: Steady-state error (1.76m short)

---

## File Organization

```
csv_data/           ← Simulation data (24 files)
├── P_Controller.csv
├── PID_Controller.csv
└── ...

plots/              ← Static visualizations (24 PNGs)
├── P/              ← P controller variants (6 files)
├── PI/             ← PI controller variants (6 files)
├── PD/             ← PD controller variants (6 files)
└── PID/            ← PID controller variants (6 files)
```

---

## Common Commands

### View Specific Controller
```bash
# Display animation
python animate_realtime.py --file csv_data/PI_Controller.csv --display-only

# Open plot
start plots/PID/PID_Controller.png
```

### Generate All Animations (requires FFmpeg)
```bash
python animate_realtime.py --speed 1.5
# Creates 24 MP4 files in animations/ directory
```

### Compare Controllers
```bash
# Open all PID variants
start plots/PID/PID_Controller.png
start plots/PID/PID_Controller_Adaptive.png
start plots/PID/PID_Controller_Trapezoidal.png
```

---

## Troubleshooting

**CSV files empty or missing?**
```bash
# Rebuild
cd build
cmake --build .
cd ..
./build/bin/freefall_object.exe
```

**Python errors?**
```bash
pip install matplotlib numpy pandas
```

**Animation won't save?**
```bash
# Install FFmpeg
choco install ffmpeg

# Or use display-only mode
python animate_realtime.py --file csv_data/PID_Controller.csv --display-only
```

---

## Next Steps

1. **Explore controllers**: Compare P, PI, PD, PID performance
2. **Adjust gains**: Edit `main.c` controller parameters
3. **Try integration methods**: Euler vs Trapezoidal vs Simplified
4. **Analyze metrics**: Check error, force, timing in plots

---

## Full Documentation

- [README.md](README.md) - Complete project overview
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - Detailed technical documentation
- [README_VISUALIZATION.md](README_VISUALIZATION.md) - Visualization guide

---

**Need help?** Check the main README.md file!
