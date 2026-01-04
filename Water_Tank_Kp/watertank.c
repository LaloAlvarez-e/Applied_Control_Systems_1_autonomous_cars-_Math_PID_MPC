#include "watertank.h"
#include <math.h>

// Get desired water level from tank
ErrorCode getTankSetpoint(void *system, double *setpoint) {
    if (system == NULL || setpoint == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank *)system;
    *setpoint = tank->setpoint;
    return ERROR_SUCCESS;
}

// Get current water level from tank
ErrorCode getTankOutput(void *system, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank *)system;
    *output = tank->level;
    return ERROR_SUCCESS;
}

// Water tank math model callback (implements Torricelli's law)
ErrorCode tankModel(void *system, double input, double dt, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank *)system;
    
    // Set inflow from control input
    tank->inflow = input;
    
    // Outflow proportional to square root of level (Torricelli's law simplified)
    double outflow = tank->model.outflow_coeff * sqrt(fmax(tank->level, 0.0));
    
    // Change in level = (inflow - outflow) / area
    double dLevel = (tank->inflow - outflow) / tank->model.area;
    tank->level += dLevel * dt;
    
    // Keep level non-negative
    if (tank->level < 0) tank->level = 0;
    
    // Return the updated water level as output
    *output = tank->level;
    return ERROR_SUCCESS;
}
