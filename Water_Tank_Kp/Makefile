# Makefile for Water Tank Kp project using Cygwin GCC

# Cygwin paths
CYGWIN_BIN = C:/cygwin64/bin/bash.exe
PROJECT_DIR = /cygdrive/c/git/Applied_Control_Systems_1_autonomous_cars-_Math_PID_MPC/Water_Tank_Kp
BUILD_DIR = build
EXECUTABLE = $(BUILD_DIR)/bin/water_tank_kp.exe

# Default target
all: build

# Configure CMake (auto-detect generator)
configure:
	$(CYGWIN_BIN) -l -c "cd '$(PROJECT_DIR)' && cmake -B $(BUILD_DIR)"

# Build the project
build: configure
	$(CYGWIN_BIN) -l -c "cd '$(PROJECT_DIR)' && make -C $(BUILD_DIR)"

# Clean build directory
clean:
	$(CYGWIN_BIN) -l -c "cd '$(PROJECT_DIR)' && rm -rf $(BUILD_DIR)"

# Rebuild from scratch
rebuild: clean build

# Run the executable
run: build
	$(CYGWIN_BIN) -l -c "cd '$(PROJECT_DIR)' && ./$(EXECUTABLE)"

.PHONY: all configure build clean rebuild run
