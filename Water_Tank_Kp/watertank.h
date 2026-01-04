#ifndef WATERTANK_H
#define WATERTANK_H

#include "controller.h"

// Model configuration structure
typedef struct {
    double outflow_coeff;      // Outflow coefficient
    double area;               // Tank cross-sectional area (m²)
    double max_inflow;         // Maximum inflow rate (m³/s)
    SystemModelCallback callback; // System model callback
} ModelConfig;

// Water tank simulation parameters
typedef struct {
    double level;           // Current water level (m)
    double setpoint;        // Desired water level (m)
    double inflow;          // Water inflow rate (m³/s)
    ControllerConfig controller; // Controller configuration with callbacks
    ModelConfig model;      // Model configuration with parameters
} WaterTank;

// Get desired water level from tank (GetSetpointCallback compatible)
// Parameters:
//   system: pointer to WaterTank structure (cast from void*)
//   setpoint: pointer to store desired water level (m)
// Returns: ErrorCode
ErrorCode getTankSetpoint(void *system, double *setpoint);

// Get current water level from tank (GetOutputCallback compatible)
// Parameters:
//   system: pointer to WaterTank structure (cast from void*)
//   output: pointer to store current water level (m)
// Returns: ErrorCode
ErrorCode getTankOutput(void *system, double *output);

// Water tank math model callback (Torricelli's law)
// This implements the physics of water tank dynamics
// Parameters:
//   system: pointer to WaterTank structure (cast from void*)
//   input: inflow rate (m³/s)
//   dt: time step (seconds)
//   output: pointer to store water level after update
// Returns: ErrorCode
ErrorCode tankModel(void *system, double input, double dt, double *output);

#endif // WATERTANK_H
