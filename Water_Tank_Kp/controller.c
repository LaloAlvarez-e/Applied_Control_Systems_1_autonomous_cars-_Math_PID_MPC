#include "controller.h"
#include "watertank.h"
#include <stddef.h>
#include <math.h>

// Error calculation function
ErrorCode calculateError(double setpoint, double currentOutput, double *error) {
    if (error == NULL) return ERROR_NULL_POINTER;
    
    *error = setpoint - currentOutput;
    return ERROR_SUCCESS;
}

// Simple Proportional controller (non-adaptive)
ErrorCode pController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL) return ERROR_NULL_POINTER;
    
    // Apply proportional control: control signal = Kp * error
    *controlSignal = config->params->Kp * error;
    return ERROR_SUCCESS;
}

// Adaptive Proportional controller with gain scheduling
ErrorCode adaptivePController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Initialize adaptive Kp on first call
    if (config->state->adaptiveKp == 0.0) {
        config->state->adaptiveKp = config->params->Kp;
        config->state->historyIndex = 0;
        for (int i = 0; i < 10; i++) {
            config->state->errorHistory[i] = 0.0;
        }
    }
    
    // Store error in history buffer
    config->state->errorHistory[config->state->historyIndex] = error;
    config->state->historyIndex = (config->state->historyIndex + 1) % 10;
    
    // Calculate error magnitude and rate of change
    double absError = error > 0 ? error : -error;
    double errorRate = (error - config->state->previousError) / config->dt;
    double absErrorRate = errorRate > 0 ? errorRate : -errorRate;
    
    // Update cumulative error (with decay to prevent unbounded growth)
    config->state->cumulativeError = config->state->cumulativeError * 0.98 + absError * config->dt;
    
    // Adaptive gain scheduling with extremely aggressive tuning:
    // - Very high gain when error is large (ultra-fast response)
    // - Maintain strong gain even near setpoint (minimize steady-state error)
    // - Dynamic adjustment based on error rate
    // - Boost gain based on cumulative error to overcome steady-state error
    double baseKp = config->params->Kp;
    
    if (absError > 1.0) {
        // Extremely large error: maximum gain for immediate action
        config->state->adaptiveKp = baseKp * 3.5;
    } else if (absError > 0.6) {
        // Very large error: very aggressive gain
        config->state->adaptiveKp = baseKp * 2.5;
    } else if (absError > 0.3) {
        // Large error: aggressive gain for fast response
        config->state->adaptiveKp = baseKp * 2.0;
    } else if (absError > 0.15) {
        // Medium error: high gain
        config->state->adaptiveKp = baseKp * 1.5;
    } else if (absError > 0.05) {
        // Small error: maintain good gain to reach setpoint
        config->state->adaptiveKp = baseKp * 1.15;
    } else if (absError > 0.02) {
        // Very small error: still use full base gain
        config->state->adaptiveKp = baseKp * 1.0;
    } else {
        // Near setpoint: maintain significant gain to eliminate steady-state error
        config->state->adaptiveKp = baseKp * 0.85;
    }
    
    // Boost gain based on cumulative error (persistent error needs more action)
    // More aggressive thresholds for P controller to overcome steady-state error
    if (config->state->cumulativeError > 3.0) {
        config->state->adaptiveKp *= 2.0;  // 100% boost for large cumulative error
    } else if (config->state->cumulativeError > 1.0) {
        config->state->adaptiveKp *= 1.6;  // 60% boost for moderate cumulative error
    } else if (config->state->cumulativeError > 0.3) {
        config->state->adaptiveKp *= 1.3;  // 30% boost for small cumulative error
    }
    
    // Boost gain if error is decreasing (good trajectory)
    if (errorRate < 0 && absErrorRate > 0.15 && absErrorRate < 1.5) {
        config->state->adaptiveKp *= 1.35;  // 35% boost for good progress
    }
    
    // Reduce gain if oscillating (high error rate)
    if (absErrorRate > 4.0) {
        config->state->adaptiveKp *= 0.55;  // Strong damping
    } else if (absErrorRate > 2.5) {
        config->state->adaptiveKp *= 0.70;  // Moderate damping
    }
    
    // Update previous error for next iteration
    config->state->previousError = error;
    
    // Apply proportional control with adaptive gain
    *controlSignal = config->state->adaptiveKp * error;
    return ERROR_SUCCESS;
}

// PI controller
ErrorCode piController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Update integral term
    config->state->integral += error * config->dt;
    
    // Apply PI control: control signal = Kp * error + Ki * integral
    *controlSignal = config->params->Kp * error + 
                     config->params->Ki * config->state->integral;
    return ERROR_SUCCESS;
}

// PD controller
ErrorCode pdController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Calculate derivative term
    double derivative = (error - config->state->previousError) / config->dt;
    
    // Update previous error
    config->state->previousError = error;
    
    // Apply PD control: control signal = Kp * error + Kd * derivative
    *controlSignal = config->params->Kp * error + 
                     config->params->Kd * derivative;
    return ERROR_SUCCESS;
}

// PID controller
ErrorCode pidController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Update integral term
    config->state->integral += error * config->dt;
    
    // Calculate derivative term
    double derivative = (error - config->state->previousError) / config->dt;
    
    // Update previous error
    config->state->previousError = error;
    
    // Apply PID control: control signal = Kp * error + Ki * integral + Kd * derivative
    *controlSignal = config->params->Kp * error + 
                     config->params->Ki * config->state->integral + 
                     config->params->Kd * derivative;
    return ERROR_SUCCESS;
}

// Adaptive PD controller with gain scheduling
ErrorCode adaptivePdController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Calculate derivative term
    double derivative = (error - config->state->previousError) / config->dt;
    
    // Calculate error rate for adaptive tuning
    double absError = fabs(error);
    double errorRate = derivative;
    double absErrorRate = fabs(errorRate);
    
    // Update cumulative error (with decay to prevent unbounded growth)
    config->state->cumulativeError = config->state->cumulativeError * 0.98 + absError * config->dt;
    
    // Adaptive gain scheduling for PD controller
    double baseKp = config->params->Kp;
    double adaptiveKp;
    
    if (absError > 1.0) {
        adaptiveKp = baseKp * 3.5;
    } else if (absError > 0.6) {
        adaptiveKp = baseKp * 2.5;
    } else if (absError > 0.3) {
        adaptiveKp = baseKp * 2.0;
    } else if (absError > 0.15) {
        adaptiveKp = baseKp * 1.5;
    } else if (absError > 0.05) {
        adaptiveKp = baseKp * 1.15;
    } else if (absError > 0.02) {
        adaptiveKp = baseKp * 1.0;
    } else {
        adaptiveKp = baseKp * 0.85;
    }
    
    // Boost gain based on cumulative error (persistent error needs more action)
    // More aggressive thresholds for PD controller to overcome steady-state error
    if (config->state->cumulativeError > 3.0) {
        adaptiveKp *= 2.0;  // 100% boost for large cumulative error
    } else if (config->state->cumulativeError > 1.0) {
        adaptiveKp *= 1.6;  // 60% boost for moderate cumulative error
    } else if (config->state->cumulativeError > 0.3) {
        adaptiveKp *= 1.3;  // 30% boost for small cumulative error
    }
    
    // Boost gain if error is decreasing
    if (errorRate < 0 && absErrorRate > 0.15 && absErrorRate < 1.5) {
        adaptiveKp *= 1.35;
    }
    
    // Reduce gain if oscillating
    if (absErrorRate > 4.0) {
        adaptiveKp *= 0.55;
    } else if (absErrorRate > 2.5) {
        adaptiveKp *= 0.70;
    }
    
    // Update previous error
    config->state->previousError = error;
    
    // Apply PD control with adaptive proportional gain
    *controlSignal = adaptiveKp * error + config->params->Kd * derivative;
    return ERROR_SUCCESS;
}

// Adaptive PI controller with gain scheduling
ErrorCode adaptivePiController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Update integral term
    config->state->integral += error * config->dt;
    
    // Calculate error rate for adaptive tuning
    double absError = fabs(error);
    double errorRate = (error - config->state->previousError) / config->dt;
    double absErrorRate = fabs(errorRate);
    
    // Update cumulative error (with decay to prevent unbounded growth)
    config->state->cumulativeError = config->state->cumulativeError * 0.98 + absError * config->dt;
    
    // Adaptive gain scheduling for PI controller
    double baseKp = config->params->Kp;
    double adaptiveKp;
    
    if (absError > 1.0) {
        adaptiveKp = baseKp * 3.5;
    } else if (absError > 0.6) {
        adaptiveKp = baseKp * 2.5;
    } else if (absError > 0.3) {
        adaptiveKp = baseKp * 2.0;
    } else if (absError > 0.15) {
        adaptiveKp = baseKp * 1.5;
    } else if (absError > 0.05) {
        adaptiveKp = baseKp * 1.15;
    } else if (absError > 0.02) {
        adaptiveKp = baseKp * 1.0;
    } else {
        adaptiveKp = baseKp * 0.85;
    }
    
    // Boost gain based on cumulative error (persistent error needs more action)
    if (config->state->cumulativeError > 5.0) {
        adaptiveKp *= 1.5;  // 50% boost for large cumulative error
    } else if (config->state->cumulativeError > 2.0) {
        adaptiveKp *= 1.3;  // 30% boost for moderate cumulative error
    } else if (config->state->cumulativeError > 0.5) {
        adaptiveKp *= 1.15;  // 15% boost for small cumulative error
    }
    
    // Boost gain if error is decreasing
    if (errorRate < 0 && absErrorRate > 0.15 && absErrorRate < 1.5) {
        adaptiveKp *= 1.35;
    }
    
    // Reduce gain if oscillating
    if (absErrorRate > 4.0) {
        adaptiveKp *= 0.55;
    } else if (absErrorRate > 2.5) {
        adaptiveKp *= 0.70;
    }
    
    // Update previous error
    config->state->previousError = error;
    
    // Apply PI control with adaptive proportional gain
    *controlSignal = adaptiveKp * error + config->params->Ki * config->state->integral;
    return ERROR_SUCCESS;
}

// Adaptive PID controller with gain scheduling
ErrorCode adaptivePidController(double error, void *system, double *controlSignal) {
    if (system == NULL || controlSignal == NULL) return ERROR_NULL_POINTER;
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->params == NULL || config->state == NULL) return ERROR_NULL_POINTER;
    
    // Update integral term
    config->state->integral += error * config->dt;
    
    // Calculate derivative term
    double derivative = (error - config->state->previousError) / config->dt;
    
    // Calculate error rate for adaptive tuning
    double absError = fabs(error);
    double errorRate = derivative;
    double absErrorRate = fabs(errorRate);
    
    // Update cumulative error (with decay to prevent unbounded growth)
    config->state->cumulativeError = config->state->cumulativeError * 0.98 + absError * config->dt;
    
    // Adaptive gain scheduling for PID controller
    double baseKp = config->params->Kp;
    double adaptiveKp;
    
    if (absError > 1.0) {
        adaptiveKp = baseKp * 3.5;
    } else if (absError > 0.6) {
        adaptiveKp = baseKp * 2.5;
    } else if (absError > 0.3) {
        adaptiveKp = baseKp * 2.0;
    } else if (absError > 0.15) {
        adaptiveKp = baseKp * 1.5;
    } else if (absError > 0.05) {
        adaptiveKp = baseKp * 1.15;
    } else if (absError > 0.02) {
        adaptiveKp = baseKp * 1.0;
    } else {
        adaptiveKp = baseKp * 0.85;
    }
    
    // Boost gain based on cumulative error (persistent error needs more action)
    if (config->state->cumulativeError > 5.0) {
        adaptiveKp *= 1.5;  // 50% boost for large cumulative error
    } else if (config->state->cumulativeError > 2.0) {
        adaptiveKp *= 1.3;  // 30% boost for moderate cumulative error
    } else if (config->state->cumulativeError > 0.5) {
        adaptiveKp *= 1.15;  // 15% boost for small cumulative error
    }
    
    // Boost gain if error is decreasing
    if (errorRate < 0 && absErrorRate > 0.15 && absErrorRate < 1.5) {
        adaptiveKp *= 1.35;
    }
    
    // Reduce gain if oscillating
    if (absErrorRate > 4.0) {
        adaptiveKp *= 0.55;
    } else if (absErrorRate > 2.5) {
        adaptiveKp *= 0.70;
    }
    
    // Update previous error
    config->state->previousError = error;
    
    // Apply PID control with adaptive proportional gain
    *controlSignal = adaptiveKp * error + 
                     config->params->Ki * config->state->integral + 
                     config->params->Kd * derivative;
    return ERROR_SUCCESS;
}

// Generic system update using controller and model callbacks
ErrorCode updateSystem(void *system, double dt, double *output,
                  ControllerCallback controllerCallback,
                  ErrorCalculationCallback errorCalcCallback) {
    if (errorCalcCallback == NULL) {
        errorCalcCallback = calculateError;
    }
    if (controllerCallback == NULL || system == NULL || output == NULL) {
        return ERROR_NULL_POINTER;
    }
    
    WaterTank *tank = (WaterTank*)system;
    ControllerConfig *config = &tank->controller;
    
    if (config->getSetpoint == NULL || config->getOutput == NULL || 
        config->params == NULL || tank->model.callback == NULL) {
        return ERROR_NULL_POINTER;
    }
    
    // Get setpoint and current output from system
    double setpoint, currentOutput;
    ErrorCode err = config->getSetpoint(system, &setpoint);
    if (err != ERROR_SUCCESS) return err;
    
    err = config->getOutput(system, &currentOutput);
    if (err != ERROR_SUCCESS) return err;
    
    // Calculate error using callback if provided, otherwise use default calculateError function
    double error;
    err = errorCalcCallback(setpoint, currentOutput, &error);
    if (err != ERROR_SUCCESS) return err;
    
    // Calculate control input using controller callback with error as input
    double controlInput;
    err = controllerCallback(error, system, &controlInput);
    if (err != ERROR_SUCCESS) return err;
    
    // Update system using model callback from system structure
    err = tank->model.callback(system, controlInput, dt, output);
    return err;
}
