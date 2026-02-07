# Quick Commands - Angle Study

## Rebuild & Run Everything

### Full Rebuild (C + Python)
```powershell
# 1. Rebuild C simulation
cd build
cmake --build .
cd ..

# 2. Run all angle simulations
.\build\bin\freefall_object.exe

# 3. Generate all visualizations
.\.venv\Scripts\python.exe visualize_angles.py

# 4. View main results
Start-Process "plots\angles\angle_comparison.png"
```

---

## View Specific Angles

### Static Plots
```powershell
# Comparison (all angles)
Start-Process "plots\angles\angle_comparison.png"

# Individual angles
Start-Process "plots\angles\individual\angle_00_detail.png"  # Flat
Start-Process "plots\angles\individual\angle_45_detail.png"  # 45° 
Start-Process "plots\angles\individual\angle_85_detail.png"  # Steep
```

### Animations
```powershell
# Flat surface (0°)
.\scripts\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_Controller_Angle_00.csv --display-only --speed 2.0

# Medium incline (30°)
.\scripts\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_Controller_Angle_30.csv --display-only --speed 2.0

# 45° incline
.\scripts\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_Controller_Angle_45.csv --display-only --speed 2.5

# Steep incline (77°)
.\scripts\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_Controller_Angle_77.csv --display-only --speed 3.0

# Very steep (85°)
.\scripts\.venv\Scripts\python.exe scripts\animate_realtime.py --file csv_data/PID_Controller_Angle_85.csv --display-only --speed 3.0
```

---

## Analysis Tools

### View Simulation Data
```powershell
# Open CSV in Excel or text editor
notepad csv_data\PID_Controller_Angle_45.csv

# Quick stats with Python
.\.venv\Scripts\python.exe -c "import pandas as pd; df=pd.read_csv('csv_data/PID_Controller_Angle_45.csv'); print(df.describe())"
```

### Compare Two Angles
```powershell
# Create custom comparison (edit visualize_angles.py)
# Or view side-by-side
Start-Process "plots\angles\individual\angle_00_detail.png"
Start-Process "plots\angles\individual\angle_85_detail.png"
```

---

## Troubleshooting

### Virtual Environment
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Check installed packages
pip list

# Reinstall if needed
pip install matplotlib numpy pandas
```

### Rebuild from Scratch
```powershell
# Clean build
Remove-Item -Recurse -Force build
mkdir build
cd build
cmake ..
cmake --build .
cd ..
```

### Regenerate CSV Data
```powershell
# Delete old data
Remove-Item csv_data\*.csv

# Run new simulation
.\build\bin\freefall_object.exe
```

---

## File Locations

| Item | Location |
|------|----------|
| C Executable | `build/bin/freefall_object.exe` |
| CSV Data | `csv_data/PID_Controller_Angle_XX.csv` |
| Comparison Plot | `plots/angles/angle_comparison.png` |
| Individual Plots | `plots/angles/individual/` |
| Source Code | `main.c`, `controller.c`, `fallingobject.c` |
| Python Scripts | `*.py` (animate_realtime, visualize_angles) |
| Documentation | `*.md` files |

---

## One-Line Commands

```powershell
# Complete rebuild and visualize
cd build; cmake --build .; cd ..; .\build\bin\freefall_object.exe; .\.venv\Scripts\python.exe visualize_angles.py; Start-Process "plots\angles\angle_comparison.png"

# Quick animation test (0° and 85°)
.\.venv\Scripts\python.exe animate_realtime.py --file csv_data/PID_Controller_Angle_00.csv --display-only --speed 2.0; .\.venv\Scripts\python.exe animate_realtime.py --file csv_data/PID_Controller_Angle_85.csv --display-only --speed 3.0
```

---

## Animation Speed Reference

| Speed | Use Case |
|-------|----------|
| 1.0 | Real-time (slow) |
| 2.0 | Good for viewing details |
| 3.0 | Fast overview |
| 5.0 | Very fast (may skip frames) |

---

## Documentation Files

- **BUILD_SUMMARY.md** - This build's results
- **ANGLE_STUDY_RESULTS.md** - Detailed analysis and findings
- **README.md** - Main project documentation
- **README_VISUALIZATION.md** - Visualization guide
- **QUICK_START.md** - Quick start guide
