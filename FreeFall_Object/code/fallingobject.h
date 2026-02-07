#ifndef FALLINGOBJECT_H
#define FALLINGOBJECT_H

#include "controller.h"

// Forward declaration
typedef struct FallingObject FallingObject;

// Net force calculation callback
// Computes net force given current velocity and applied force
// Parameters: object, velocity, applied_force
// Returns: net force (N)
typedef double (*NetForceCallback)(FallingObject *object, double velocity, double applied_force);

// Model configuration structure
typedef struct {
    double mass;               // Object mass (kg)
    double gravity;            // Gravitational acceleration (m/s²)
    double incline_angle;      // Incline angle θ (radians, 0 = free fall)
    double drag_coeff;         // Air resistance coefficient (N·s²/m²)
    double max_force;          // Maximum applied force (N)
    double max_position;       // Maximum position (m) for 100% normalization
    SystemModelCallback callback; // System model callback
    NetForceCallback netForceCallback; // Net force calculation callback
} ObjectModelConfig;

// Falling object simulation parameters
typedef struct FallingObject {
    double position_pct;       // Derived position (0-100%, computed from position) - OUTPUT
    double velocity;           // Current velocity (m/s) - INTERNAL STATE
    double position;           // Current position (m) - INTERNAL TRACKING
    double setpoint;           // Desired position (0-100%, normalized by max_position)
    double applied_force;      // Applied control force (N)
    double previousNetForce;   // Net force from previous iteration (for trapezoidal integration)
    ControllerConfig controller; // Controller configuration with callbacks
    ObjectModelConfig model;   // Model configuration with parameters
} FallingObject;

// Get desired position from object (GetSetpointCallback compatible)
// Parameters:
//   system: pointer to FallingObject structure (cast from void*)
//   setpoint: pointer to store desired position (percentage 0-100%)
// Returns: ErrorCode
ErrorCode getObjectSetpoint(void *system, double *setpoint);

// Get current position from object (GetOutputCallback compatible)
// Parameters:
//   system: pointer to FallingObject structure (cast from void*)
//   output: pointer to store current position (percentage 0-100%, derived from position)
// Returns: ErrorCode
ErrorCode getObjectOutput(void *system, double *output);

// Falling object math model callback (with gravity and drag)
// Implements position dynamics: F_net = F_applied - F_gravity - F_drag
// F_gravity = m*g*sin(θ) for incline, m*g for free fall (θ=90°)
// Position is derived from velocity integration
// Parameters:
//   system: pointer to FallingObject structure (cast from void*)
//   input: control input (applied force, N)
//   dt: time step (s)
//   output: pointer to store updated position (percentage 0-100%, derived from position)
// Returns: ErrorCode
ErrorCode objectModel(void *system, double input, double dt, double *output);

// Calculate net force for falling object
// F_net = F_applied - F_gravity_tangential - F_drag
// F_gravity_tangential = m*g*sin(θ)
// F_drag = drag_coeff * v²
// Parameters:
//   object: pointer to FallingObject structure
//   velocity: current velocity (m/s)
//   applied_force: applied force (N)
// Returns: net force (N)
double calculateObjectNetForce(FallingObject *object, double velocity, double applied_force);

// Calculate simplified net force (no drag)
// F_net = F_applied - m*g*sin(θ)
// Parameters:
//   object: pointer to FallingObject structure
//   velocity: current velocity (m/s) - not used in simplified model
//   applied_force: applied force (N)
// Returns: net force (N)
double calculateObjectNetForceSimplified(FallingObject *object, double velocity, double applied_force);

// Falling object model with trapezoidal integration
// More accurate numerical integration using trapezoidal rule
// Parameters:
//   system: pointer to FallingObject structure (cast from void*)
//   input: control input (applied force, N)
//   dt: time step (s)
//   output: pointer to store updated position (percentage 0-100%)
// Returns: ErrorCode
ErrorCode objectModelTrapezoidal(void *system, double input, double dt, double *output);

// Falling object model with trapezoidal integration (Simplified - No Drag)
// Pure force accumulation without air resistance
// Parameters:
//   system: pointer to FallingObject structure (cast from void*)
//   input: control input (applied force, N)
//   dt: time step (s)
//   output: pointer to store updated position (percentage 0-100%)
// Returns: ErrorCode
ErrorCode objectModelTrapezoidalSimplified(void *system, double input, double dt, double *output);

#endif // FALLINGOBJECT_H
