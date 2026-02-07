#ifndef WATERTANK_H
#define WATERTANK_H

#include "controller.h"

// Forward declaration
typedef struct WaterTank WaterTank;

// Net flow calculation callback
// Computes net flow given current level and inflow
// Parameters: tank, level, inflow
// Returns: net flow (inflow - outflow)
typedef double (*NetFlowCallback)(WaterTank *tank, double level, double inflow);

// Model configuration structure
typedef struct {
    double outflow_coeff;      // Outflow coefficient
    double area;               // Tank cross-sectional area (m²)
    double max_inflow;         // Maximum inflow rate (m³/s)
    double density;            // Water density (kg/m³)
    double max_level;          // Maximum tank height (m) for 100% normalization (e.g., 4.507 m)
    SystemModelCallback callback; // System model callback
    NetFlowCallback netFlowCallback; // Net flow calculation callback
} ModelConfig;

// Water tank simulation parameters
typedef struct WaterTank {
    double level;           // Derived water level (0-100%, computed from volume) - OUTPUT
    double volume;          // Current water volume (m³) - INTERNAL STATE
    double height;          // Current water height (m, derived from volume) - INTERNAL TRACKING
    double setpoint;        // Desired water level (0-100%, normalized by max_height)
    double inflow;          // Water inflow rate (m³/s)
    double previousNetFlow; // Net flow from previous iteration (for trapezoidal integration)
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
//   output: pointer to store current water level (percentage 0-100%, derived from volume)
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

// Calculate net flow for water tank (inflow - outflow)
// Uses Torricelli's law: outflow = coeff * sqrt(level)
// Parameters:
//   tank: pointer to WaterTank structure
//   level: water level (m)
//   inflow: inflow rate (m³/s)
// Returns: net flow (m³/s)
double calculateTankNetFlow(WaterTank *tank, double level, double inflow);

// Calculate simplified net flow (no outflow, direct mass control)
// For comparison with Python reference implementation
// Parameters:
//   tank: pointer to WaterTank structure
//   level: water level (m) - not used in this simplified model
//   inflow: inflow rate (m³/s)
// Returns: net mass flow (kg/s)
double calculateTankNetFlowSimplified(WaterTank *tank, double level, double inflow);

// Water tank math model with trapezoidal integration (Torricelli's law)
// This implements the physics of water tank dynamics using trapezoidal rule
// More accurate than Euler's method for numerical integration
// Parameters:
//   system: pointer to WaterTank structure (cast from void*)
//   input: inflow rate (m³/s)
//   dt: time step (seconds)
//   output: pointer to store water level after update
// Returns: ErrorCode
ErrorCode tankModelTrapezoidal(void *system, double input, double dt, double *output);

// Water tank math model with trapezoidal integration (Simplified - No Outflow)
// This matches the Python reference implementation where controller directly controls mass flow
// No outflow dynamics - pure accumulation model
// Parameters:
//   system: pointer to WaterTank structure (cast from void*)
//   input: control input (treated as mass flow rate in kg/s)
//   dt: time step (seconds)
//   output: pointer to store water level after update
// Returns: ErrorCode
ErrorCode tankModelTrapezoidalSimplified(void *system, double input, double dt, double *output);
// Water tank math model with trapezoidal integration (Simplified - No Outflow)
// This matches the Python reference implementation where controller directly controls mass flow
// No outflow dynamics - pure accumulation model
// Parameters:
//   system: pointer to WaterTank structure (cast from void*)
//   input: control input (treated as volumetric flow rate in m³/s, converted to mass)
//   dt: time step (seconds)
//   output: pointer to store water level after update
// Returns: ErrorCode
ErrorCode tankModelTrapezoidalSimplified(void *system, double input, double dt, double *output);
#endif // WATERTANK_H
