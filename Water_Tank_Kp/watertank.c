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
    
    // Convert volume to height for physics calculation: height = volume / area
    double level_m = tank->volume / tank->model.area;
    
    // Calculate net MASS flow using callback: ṁ = (dvol_w/dt) * ρ_w
    double netMassFlow = calculateTankNetFlow(tank, level_m, tank->inflow);
    
    // Volume change: dvol_w/dt = ṁ / ρ
    double dVolume = (netMassFlow / tank->model.density) * dt;
    
    // Update volume (m³) - INTERNAL STATE
    tank->volume += dVolume;
    
    // Calculate max volume: V_max = area × max_level
    double max_volume = tank->model.area * tank->model.max_level;
    
    // Keep volume within physical limits
    if (tank->volume < 0) tank->volume = 0;
    if (tank->volume > max_volume) tank->volume = max_volume;
    
    // Derive height from volume: height = volume / area
    tank->height = tank->volume / tank->model.area;
    
    // Derive level (percentage) from volume: level% = (volume / V_max) × 100
    tank->level = (tank->volume / max_volume) * 100.0;
    
    // Return the updated water level (percentage) as output
    *output = tank->level;
    return ERROR_SUCCESS;
}

// Calculate net flow for water tank using Torricelli's law
// Returns net MASS flow rate: ṁ = (dvol_w/dt) * ρ_w
// Net volumetric flow = inflow - outflow, where outflow = coeff * sqrt(level)
// Net mass flow = net volumetric flow * density
double calculateTankNetFlow(WaterTank *tank, double level, double inflow) {
    // Outflow proportional to square root of level (Torricelli's law)
    double outflow = tank->model.outflow_coeff * sqrt(fmax(level, 0.0));
    
    // Net volumetric flow rate (m³/s)
    double netVolumetricFlow = inflow - outflow;
    
    // Convert to mass flow rate: ṁ = (dvol_w/dt) * ρ_w
    double netMassFlow = netVolumetricFlow * tank->model.density;
    
    return netMassFlow;
}

// Calculate simplified net flow (no outflow dynamics)
// Matches Python reference implementation where control input is directly mass flow
// No Torricelli's law, no outflow - pure accumulation
double calculateTankNetFlowSimplified(WaterTank *tank, double level, double inflow) {
    (void)level;  // Unused parameter in simplified model
    // In simplified model, inflow is treated as direct mass flow rate
    // No outflow calculation - the controller has perfect control
    // This matches: m_dot = Kp * error (Python implementation)
    return inflow * tank->model.density;  // Convert volumetric inflow to mass flow
}

// Water tank model with trapezoidal integration
// More accurate numerical integration using trapezoidal rule
// Following the generalized algorithm: vol[t_i] = vol[t_{i-1}] + ((ṁ[t_{i-1}] + ṁ[t_i]) / 2) * dt
// Where: ṁ = (dvol_w/dt) * ρ_w  and  dvol_w/dt = ṁ / ρ
ErrorCode tankModelTrapezoidal(void *system, double input, double dt, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank *)system;
    
    // Set inflow from control input
    tank->inflow = input;
    
    // Convert volume to height for physics calculation: height = volume / area
    double level_m = tank->volume / tank->model.area;
    
    // Calculate net MASS flow at current level (this becomes ṁ[t_i])
    // netFlowCallback returns ṁ = (dvol_w/dt) * ρ_w
    double massFlow_current = tank->model.netFlowCallback(tank, level_m, tank->inflow);
    
    // Apply trapezoidal rule: average of previous and current mass flows
    // ṁ_avg = (ṁ[t_{i-1}] + ṁ[t_i]) / 2
    double massFlow_avg = (tank->previousNetFlow + massFlow_current) / 2.0;
    
    // Convert mass flow to volume change: dvol_w/dt = ṁ / ρ
    double volumeChange = (massFlow_avg / tank->model.density) * dt;
    
    // Update volume (m³) - INTERNAL STATE
    tank->volume += volumeChange;
    
    // Calculate max volume: V_max = area × max_level
    double max_volume = tank->model.area * tank->model.max_level;
    
    // Keep volume within physical limits
    if (tank->volume < 0) tank->volume = 0;
    if (tank->volume > max_volume) tank->volume = max_volume;
    
    // Derive level (percentage) from volume: level% = (volume / V_max) × 100
    tank->level = (tank->volume / max_volume) * 100.0;
    
    // Store current mass flow for next iteration (it becomes the previous value)
    tank->previousNetFlow = massFlow_current;
    
    // Return the updated water level as output (percentage)
    *output = tank->level;
    return ERROR_SUCCESS;
}

// Water tank model with trapezoidal integration (Simplified - No Outflow)
// Matches Python reference: volume[i] = volume[i-1] + (m_dot[i-1] + m_dot[i])/(2*density) * dt
// No outflow dynamics - controller directly controls mass accumulation
ErrorCode tankModelTrapezoidalSimplified(void *system, double input, double dt, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank *)system;
    
    // Set inflow from control input
    tank->inflow = input;
    
    // Convert volume to height for physics calculation: height = volume / area
    double level_m = tank->volume / tank->model.area;
    
    // In simplified model: ṁ = input * density (no outflow)
    // This is equivalent to Python: m_dot = Kp * error
    double massFlow_current = tank->model.netFlowCallback(tank, level_m, tank->inflow);
    
    // Apply trapezoidal rule: average of previous and current mass flows
    // Python equation: volume[i] = volume[i-1] + (m_dot[i-1] + m_dot[i])/(2*density) * dt
    // ṁ_avg = (ṁ[t_{i-1}] + ṁ[t_i]) / 2
    double massFlow_avg = (tank->previousNetFlow + massFlow_current) / 2.0;
    
    // Convert mass flow to volume change: dvol_w/dt = ṁ / ρ
    // This matches: (m_dot[i-1] + m_dot[i])/(2*density)
    double volumeChange = (massFlow_avg / tank->model.density) * dt;
    
    // Update volume (m³) - INTERNAL STATE
    tank->volume += volumeChange;
    
    // Calculate max volume: V_max = area × max_level
    double max_volume = tank->model.area * tank->model.max_level;
    
    // Keep volume within physical limits
    if (tank->volume < 0) tank->volume = 0;
    if (tank->volume > max_volume) tank->volume = max_volume;
    
    // Derive height from volume: height = volume / area
    tank->height = tank->volume / tank->model.area;
    
    // Derive level (percentage) from volume: level% = (volume / V_max) × 100
    tank->level = (tank->volume / max_volume) * 100.0;
    
    // Store current mass flow for next iteration (it becomes the previous value)
    tank->previousNetFlow = massFlow_current;
    
    // Return the updated water level (percentage) as output
    *output = tank->level;
    return ERROR_SUCCESS;
}


// Water tank model with trapezoidal integration (Simplified - No Outflow)
