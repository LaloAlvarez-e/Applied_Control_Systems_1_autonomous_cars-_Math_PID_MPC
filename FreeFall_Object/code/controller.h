#ifndef CONTROLLER_H
#define CONTROLLER_H

// Error code enumeration for application errors
typedef enum {
    ERROR_SUCCESS = 0,           // Operation completed successfully
    ERROR_NULL_POINTER,          // Null pointer provided
    ERROR_INVALID_PARAMETER,     // Invalid parameter value
    ERROR_CALLBACK_FAILED        // Callback function failed
} ErrorCode;

// Get output callback function type
// Parameters:
//   system: pointer to system state structure
//   output: pointer to store current system output (measured variable)
// Returns: ErrorCode
typedef ErrorCode (*GetOutputCallback)(void *system, double *output);

// Get setpoint callback function type
// Parameters:
//   system: pointer to system state structure
//   setpoint: pointer to store desired system output
// Returns: ErrorCode
typedef ErrorCode (*GetSetpointCallback)(void *system, double *setpoint);

// Controller parameters structure
// Contains gain constants for P, PI, and PID controllers
typedef struct {
    double Kp;  // Proportional gain
    double Ki;  // Integral gain
    double Kd;  // Derivative gain
} ControllerParams;

// Controller state structure
// Contains state variables for integral and derivative terms
typedef struct {
    double integral;      // Accumulated integral of error
    double previousError; // Previous error for derivative calculation
    double adaptiveKp;    // Adaptive gain for proportional controller
    double errorHistory[10]; // Error history for adaptive tuning
    int historyIndex;     // Index for circular buffer
    double cumulativeError; // Cumulative error for adaptive gain adjustment
} ControllerState;

// Controller configuration structure
// Contains all callbacks and parameters needed by the controller
typedef struct {
    ControllerParams *params;  // Pointer to controller parameters (Kp, Ki, Kd)
    ControllerState *state;    // Pointer to controller state (integral, previousError)
    GetSetpointCallback getSetpoint;     // Function to get desired system output
    GetOutputCallback getOutput;         // Function to get current system output
    double dt;                           // Time step for integral/derivative calculations
} ControllerConfig;

// Error calculation callback function type
// Parameters:
//   setpoint: desired system output
//   currentOutput: current system output (measured variable)
//   error: pointer to store calculated error
// Returns: ErrorCode
typedef ErrorCode (*ErrorCalculationCallback)(double setpoint, double currentOutput, double *error);

// Controller callback function type
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
typedef ErrorCode (*ControllerCallback)(double error, void *system, double *controlSignal);

// Generic system model callback function type
// Parameters:
//   system: pointer to system state structure
//   input: control input to the system
//   dt: time step (seconds)
//   output: pointer to store system output (e.g., measured variable)
// Returns: ErrorCode
typedef ErrorCode (*SystemModelCallback)(void *system, double input, double dt, double *output);

// Error calculation function
// Parameters:
//   setpoint: desired system output
//   currentOutput: current system output (measured variable)
//   error: pointer to store calculated error
// Returns: ErrorCode
ErrorCode calculateError(double setpoint, double currentOutput, double *error);

// Proportional controller (can be used as ControllerCallback)
// Proportional controller (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode pController(double error, void *system, double *controlSignal);

// Adaptive Proportional controller with gain scheduling (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode adaptivePController(double error, void *system, double *controlSignal);

// PI controller (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode piController(double error, void *system, double *controlSignal);

// PD controller (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode pdController(double error, void *system, double *controlSignal);

// PID controller (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode pidController(double error, void *system, double *controlSignal);

// Adaptive PD controller with gain scheduling (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode adaptivePdController(double error, void *system, double *controlSignal);

// Adaptive PI controller with gain scheduling (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode adaptivePiController(double error, void *system, double *controlSignal);

// Adaptive PID controller with gain scheduling (can be used as ControllerCallback)
// Parameters:
//   error: control error
//   system: pointer to system state structure (for accessing ControllerConfig with state)
//   controlSignal: pointer to store control signal output
// Returns: ErrorCode
ErrorCode adaptivePidController(double error, void *system, double *controlSignal);

// Generic system update using controller and model callbacks
// Parameters:
//   system: pointer to system state structure (must contain ControllerConfig and model callback)
//   dt: time step (seconds)
//   output: pointer to store system output after update
//   controllerCallback: function pointer to controller algorithm
//   errorCalcCallback: function pointer to error calculation (optional, uses calculateError if NULL)
// Returns: ErrorCode
ErrorCode updateSystem(void *system, double dt, double *output,
                  ControllerCallback controllerCallback,
                  ErrorCalculationCallback errorCalcCallback);

#endif // CONTROLLER_H
