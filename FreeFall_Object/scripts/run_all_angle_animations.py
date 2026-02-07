#!/usr/bin/env python3
"""
Run animations for all landing angles sequentially
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run animations for all angle simulations"""
    angles = [0, 10, 15, 22, 30, 36, 45, 64, 77, 85]
    csv_dir = Path("csv_data")
    
    print("=" * 70)
    print("Running Real-Time Animations for All Landing Angles")
    print("=" * 70)
    print("\nPress Ctrl+C to stop the animation and move to next angle")
    print("Close the animation window to automatically proceed to next angle\n")
    
    python_exe = Path(".venv/Scripts/python.exe")
    if not python_exe.exists():
        print("Error: Virtual environment not found!")
        print("Please run: py -3 -m venv .venv")
        print("Then: .venv\\Scripts\\pip install matplotlib numpy pandas")
        return 1
    
    for angle in angles:
        csv_file = csv_dir / f"PID_Controller_Angle_{angle:02d}.csv"
        
        if not csv_file.exists():
            print(f"⚠️  Skipping angle {angle}° - CSV file not found")
            continue
        
        print(f"\n{'=' * 70}")
        print(f"Running animation: Landing Angle = {angle}°")
        print(f"File: {csv_file}")
        print(f"{'=' * 70}\n")
        
        try:
            # Run animation with display-only mode at 2x speed
            result = subprocess.run(
                [str(python_exe), "animate_realtime.py", 
                 "--file", str(csv_file),
                 "--display-only",
                 "--speed", "2.0"],
                check=False
            )
            
            if result.returncode == 0:
                print(f"✓ Completed: {angle}°")
            elif result.returncode == -2:  # Ctrl+C
                print(f"\n⚠️  Interrupted by user")
                break
            else:
                print(f"⚠️  Animation exited with code {result.returncode}")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Stopped by user (Ctrl+C)")
            break
        except Exception as e:
            print(f"❌ Error running animation for {angle}°: {e}")
            continue
    
    print("\n" + "=" * 70)
    print("Animation sequence complete!")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
