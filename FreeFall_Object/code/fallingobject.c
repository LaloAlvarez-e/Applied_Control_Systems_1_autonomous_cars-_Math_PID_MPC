#include "fallingobject.h"
#include <math.h>

// Get desired position from object
ErrorCode getObjectSetpoint(void *system, double *setpoint) {
    if (system == NULL || setpoint == NULL) return ERROR_NULL_POINTER;
    
    FallingObject *object = (FallingObject *)system;
    *setpoint = object->setpoint;
    return ERROR_SUCCESS;
}

// Get current position from object
ErrorCode getObjectOutput(void *system, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    FallingObject *object = (FallingObject *)system;
    *output = object->position_pct;
    return ERROR_SUCCESS;
}

// Calculate net force for falling object (with drag)
// F_net = F_applied - F_gravity_tangential - F_drag
// From Image 2: F_g_t = Fg*sin(θ) (component along incline)
// F_drag = drag_coeff * v²
double calculateObjectNetForce(FallingObject *object, double velocity, double applied_force) {
    // Gravity component tangential to motion: F_g_t = m*g*sin(θ)
    // For vertical free fall: sin(90°) = 1, so F_g_t = m*g
    double gravity_force = object->model.mass * object->model.gravity * sin(object->model.incline_angle);
    
    // Air resistance/drag: F_drag = C_d * v²
    double drag_force = object->model.drag_coeff * velocity * velocity;
    
    // Net force: F_net = F_applied - F_gravity - F_drag
    // Positive direction is upward (against gravity)
    double net_force = applied_force - gravity_force - drag_force;
    
    return net_force;
}

// Calculate simplified net force (no drag)
double calculateObjectNetForceSimplified(FallingObject *object, double velocity, double applied_force) {
    (void)velocity;  // Unused in simplified model
    
    // Only gravity component: F_g_t = m*g*sin(θ)
    double gravity_force = object->model.mass * object->model.gravity * sin(object->model.incline_angle);
    
    // Net force: F_net = F_applied - F_gravity
    double net_force = applied_force - gravity_force;
    
    return net_force;
}

// Falling object math model callback (Euler integration)
// From Image 1: F_a(t) → 1/m → dv/dt=a → ∫ → v(t) → dx/dt=v(t) → ∫ → x(t)
ErrorCode objectModel(void *system, double input, double dt, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    FallingObject *object = (FallingObject *)system;
    
    // Set applied force from control input (limit to maximum)
    object->applied_force = input;
    if (object->applied_force > object->model.max_force) {
        object->applied_force = object->model.max_force;
    }
    if (object->applied_force < -object->model.max_force) {
        object->applied_force = -object->model.max_force;
    }
    
    // Calculate net force using callback
    double net_force = object->model.netForceCallback(object, object->velocity, object->applied_force);
    
    // Calculate acceleration: a = F_net / m (from diagram: dv/dt = a)
    double acceleration = net_force / object->model.mass;
    
    // Update velocity: v(t) = v_i + (1/m) * ∫F_a(t)dt (Euler integration)
    object->velocity += acceleration * dt;
    
    // Update position: x(t) = x_i + ∫v(t)dt (from diagram: dx/dt = v(t))
    object->position += object->velocity * dt;
    
    // Keep position within physical limits (0 to max_position)
    if (object->position < 0.0) object->position = 0.0;
    if (object->position > object->model.max_position) object->position = object->model.max_position;
    
    // Derive position percentage from position: position_pct = (position / max_position) × 100
    object->position_pct = (object->position / object->model.max_position) * 100.0;
    
    // Return the updated position percentage as output
    *output = object->position_pct;
    return ERROR_SUCCESS;
}

// Falling object model with trapezoidal integration
// From Image 1: v(t_j) = v(t_{j-1}) + (1/m) * (F_a(t_{j-1}) + F_a(t_j))/2 * Δt
//              x(t_j) = x(t_{j-1}) + (v(t_{j-1}) + v(t_j))/2 * Δt
ErrorCode objectModelTrapezoidal(void *system, double input, double dt, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    FallingObject *object = (FallingObject *)system;
    
    // Set applied force from control input
    object->applied_force = input;
    if (object->applied_force > object->model.max_force) {
        object->applied_force = object->model.max_force;
    }
    if (object->applied_force < -object->model.max_force) {
        object->applied_force = -object->model.max_force;
    }
    
    // Calculate net force at current state (this becomes F_a(t_j))
    double net_force_current = object->model.netForceCallback(object, object->velocity, object->applied_force);
    
    // Apply trapezoidal rule: average of previous and current net forces
    // From Image 1: (F_a(t_{j-1}) + F_a(t_j))/2
    double net_force_avg = (object->previousNetForce + net_force_current) / 2.0;
    
    // Calculate average acceleration: a_avg = F_net_avg / m
    double acceleration_avg = net_force_avg / object->model.mass;
    
    // Store current velocity for position update
    double velocity_prev = object->velocity;
    
    // Update velocity: v(t_j) = v(t_{j-1}) + (1/m) * (F_a(t_{j-1}) + F_a(t_j))/2 * Δt
    object->velocity += acceleration_avg * dt;
    
    // Update position using trapezoidal rule for velocity
    // From Image 1: x(t_j) = x(t_{j-1}) + (v(t_{j-1}) + v(t_j))/2 * Δt
    double velocity_avg = (velocity_prev + object->velocity) / 2.0;
    object->position += velocity_avg * dt;
    
    // Keep position within physical limits
    if (object->position < 0.0) object->position = 0.0;
    if (object->position > object->model.max_position) object->position = object->model.max_position;
    
    // Derive position percentage from position
    object->position_pct = (object->position / object->model.max_position) * 100.0;
    
    // Store current net force for next iteration
    object->previousNetForce = net_force_current;
    
    // Return the updated position percentage as output
    *output = object->position_pct;
    return ERROR_SUCCESS;
}

// Falling object model with trapezoidal integration (Simplified - No Drag)
ErrorCode objectModelTrapezoidalSimplified(void *system, double input, double dt, double *output) {
    if (system == NULL || output == NULL) return ERROR_NULL_POINTER;
    
    FallingObject *object = (FallingObject *)system;
    
    // Set applied force from control input
    object->applied_force = input;
    if (object->applied_force > object->model.max_force) {
        object->applied_force = object->model.max_force;
    }
    if (object->applied_force < -object->model.max_force) {
        object->applied_force = -object->model.max_force;
    }
    
    // Calculate net force at current state (simplified - no drag)
    double net_force_current = object->model.netForceCallback(object, object->velocity, object->applied_force);
    
    // Apply trapezoidal rule: average of previous and current net forces
    double net_force_avg = (object->previousNetForce + net_force_current) / 2.0;
    
    // Calculate average acceleration
    double acceleration_avg = net_force_avg / object->model.mass;
    
    // Store current velocity for position update
    double velocity_prev = object->velocity;
    
    // Update velocity using trapezoidal rule
    object->velocity += acceleration_avg * dt;
    
    // Update position using trapezoidal rule
    double velocity_avg = (velocity_prev + object->velocity) / 2.0;
    object->position += velocity_avg * dt;
    
    // Keep position within physical limits
    if (object->position < 0.0) object->position = 0.0;
    if (object->position > object->model.max_position) object->position = object->model.max_position;
    
    // Derive position percentage from position
    object->position_pct = (object->position / object->model.max_position) * 100.0;
    
    // Store current net force for next iteration
    object->previousNetForce = net_force_current;
    
    // Return the updated position percentage as output
    *output = object->position_pct;
    return ERROR_SUCCESS;
}
