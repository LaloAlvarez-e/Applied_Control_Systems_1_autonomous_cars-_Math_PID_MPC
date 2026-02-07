#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <time.h>
#include "fallingobject.h"
#include "plot.h"

#ifdef _WIN32
    #include <windows.h>
    #include <process.h>
    #define M_PI 3.14159265358979323846
#else
    #include <pthread.h>
    #include <unistd.h>
#endif

// Global flag for graceful shutdown
volatile int keep_running = 1;

// Signal handler for Ctrl+C
void signal_handler(int signum) {
    (void)signum;
    keep_running = 0;
    printf("\nReceived interrupt signal. Stopping simulation...\n");
}

// Simulation configuration
typedef struct {
    void *realtimePlot;
    void *simulationMutex;
    void *simulationThread;
    void *simulationComplete;
    const char *name;
    ControllerCallback controller;
    ControllerParams params;
} SimulationConfig;

// Thread data structure
typedef struct {
    SimulationConfig *config;
    double dt;
    int n;
    double sim_time;
    int windowIndex;
    SystemModelCallback modelCallback;  // Model callback (Euler or Trapezoidal)
    double landing_angle;  // Landing surface angle in degrees
    double ball_x_position;  // Ball X position (where ball lands)
    double train_x_initial;  // Train initial X position
    double ball_y_initial;   // Ball initial Y height (random)
} ThreadData;

// Thread function to run a single simulation
#ifdef _WIN32
unsigned __stdcall runSimulation(void *arg) {
#else
void* runSimulation(void *arg) {
#endif
    ThreadData *data = (ThreadData*)arg;
    SimulationConfig *sim = data->config;
    double dt = data->dt;
    int n = data->n;
    
    printf("[Thread %s] Starting simulation (Kp=%.2f, Ki=%.2f, Kd=%.2f)...\n", 
           sim->name,
           sim->params.Kp,
           sim->params.Ki,
           sim->params.Kd);
    
    // Initialize data collection (no real-time plotting)
    void *realtimePlot = NULL;
    ErrorCode plotErr = initRealtimePlot(sim->name, data->windowIndex, &realtimePlot);
    if (plotErr == ERROR_SUCCESS && realtimePlot != NULL) {
        printf("[Thread %s] Data collection initialized\n", sim->name);
    } else if (plotErr != ERROR_SUCCESS) {
        printf("[Thread %s] Warning: Data collection failed with error code %d\n", sim->name, plotErr);
    }
    
    // Controller state (reset for each simulation)
    ControllerState controllerState = {
        .integral = 0.0,
        .previousError = 0.0,
        .adaptiveKp = 0.0,
        .historyIndex = 0,
        .cumulativeError = 0.0
    };
    
    // Initialize falling object with controller configuration
    // ===== NEW PHYSICS MODEL: Train catching falling ball =====
    // Ball falls at fixed X position: ball_x_position from ThreadData
    // Train moves horizontally from train_x_initial to reach ball_x_position
    // Landing surface has inclination angle
    
    double ball_landing_x = data->ball_x_position;  // Ball X position from parameter sweep
    double train_start_x = data->train_x_initial;   // Train initial X from parameter sweep
    double max_position = 100.0;   // Maximum X position (m) for normalization
    double falling_object_initial_height = data->ball_y_initial;  // Ball starts at random Y height
    double landing_surface_angle = data->landing_angle * M_PI / 180.0;  // Convert degrees to radians
    
    // Train horizontal position (X coordinate)
    double initial_train_x_pct = (train_start_x / max_position) * 100.0;  // Train position as percentage
    double initial_train_x = train_start_x;  // Initial X position from parameter
    double initial_train_velocity = 0.0;  // Train starts from rest
    
    FallingObject object = {
        .position_pct = initial_train_x_pct, // Output: TRAIN horizontal position (percentage)
        .velocity = initial_train_velocity,  // Internal state: TRAIN horizontal velocity (0 m/s)
        .position = initial_train_x,         // Internal tracking: TRAIN horizontal X position
        .setpoint = (ball_landing_x / max_position) * 100.0, // Target: Ball landing X position (percentage)
        .applied_force = 0.0,        // Will be controlled
        .previousNetForce = 0.0,     // Initialize for trapezoidal integration
        .controller = {
            .params = &sim->params,
            .state = &controllerState,
            .getSetpoint = getObjectSetpoint,
            .getOutput = getObjectOutput,
            .dt = dt
        },
        .model = {
            .mass = 100.0,          // 100 kg train (realistic mass)
            .gravity = 9.81,        // Earth gravity (m/s²)
            .incline_angle = landing_surface_angle, // Landing surface inclination (0° = flat)
            .drag_coeff = 0.5,      // Friction/air resistance (increased)
            .max_force = 3000.0,    // Maximum control force (3000 N, a_max = 30 m/s²)
            .max_position = max_position, // 100 m maximum X position
            .callback = data->modelCallback,  // System model callback (Euler/Trapezoidal/Simplified)
            .netForceCallback = (data->modelCallback == objectModelTrapezoidalSimplified) ? 
                               calculateObjectNetForceSimplified : calculateObjectNetForce
        }
    };
    
    // Run simulation
    int i = 0;
    double max_time = data->sim_time;  // Use sim_time from thread data
    while (keep_running && (i * dt < max_time)) {
        double current_time = i * dt;
        
        // Calculate falling ball's Y position using free-fall physics: y(t) = y₀ - ½gt²
        // Ball falls vertically at fixed X position (ball_landing_x)
        double g = object.model.gravity;  // 9.81 m/s²
        double ball_height_y = falling_object_initial_height - 0.5 * g * current_time * current_time;
        
        // Keep ball above ground (0m minimum)
        if (ball_height_y < 0.0) {
            ball_height_y = 0.0;  // Ball hits ground
        }
        
        // Setpoint remains constant: Train must reach ball_landing_x position
        // object.setpoint is already set to ball_landing_x (60m = 60%)
        // Train's control objective: move horizontally to match this X position
        
        // Update object using specified controller
        double current_position_pct;
        ErrorCode err = updateSystem(&object, dt, &current_position_pct, 
                                    sim->controller, NULL);
        if (err != ERROR_SUCCESS) {
            printf("[Thread %s] Error during system update at t=%.2f: Error code %d\n", 
                   sim->name, current_time, err);
            keep_running = 0;
            break;
        }
        
        // Check if we should stop
        if (!keep_running) {
            printf("[Thread %s] Stopping simulation at t=%.2f\n", sim->name, current_time);
            break;
        }
        
        // Update data collection
        if (realtimePlot) {
            // Store: time, train_x_position, ball_y_height, applied_force,
            //        velocity, acceleration, error_derivative, error_integral
            // For CSV: train position is current_position_pct, ball height is ball_height_y
            double ball_height_pct = (ball_height_y / falling_object_initial_height) * 100.0;
            
            // Calculate acceleration: a = F_net / m
            // Get net force from object's previous net force (stored after physics update)
            double train_acceleration = object.previousNetForce / object.model.mass;
            
            // Calculate error and error derivative for logging
            double error = object.setpoint - current_position_pct;
            double error_derivative = (error - object.controller.state->previousError) / dt;
            double error_integral = object.controller.state->integral;
            
            ErrorCode plotErr = updateRealtimePlot(realtimePlot, current_time, 
                                                  current_position_pct, ball_height_pct, object.applied_force,
                                                  object.velocity, train_acceleration,
                                                  error_derivative, error_integral);
            if (plotErr != ERROR_SUCCESS) {
                printf("[Thread %s] Warning: Data update failed at t=%.2f: Error code %d\n", 
                       sim->name, current_time, plotErr);
            }
        }
        
        i++;
    }
    
    // Save plot at the end
    if (realtimePlot) {
        printf("[Thread %s] Saving plot to PNG...\n", sim->name);
        closeRealtimePlot(realtimePlot, sim->name);
        printf("[Thread %s] Completed!\n", sim->name);
    }
    
#ifdef _WIN32
    return 0;
#else
    return NULL;
#endif
}

int main(void) {
    // Set up signal handler for graceful shutdown
#ifdef _WIN32
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
#else
    signal(SIGINT, signal_handler);
#endif
    
    // Initialize plotting system (creates CSV directory)
    initPlot();
    
    printf("Train Catching Falling Ball - Random Scenario Generation\n");
    printf("==============================================================================\n");
    printf("Generating 10 random scenarios with varied parameters:\n");
    printf("  - Angles: Random 0° to 45°\n");
    printf("  - Ball X positions: Random 20m to 100m\n");
    printf("  - Ball Y heights: Random 30m to 100m\n");
    printf("  - Train initial X: Random 0m to (ball_x - 20m)\n");
    printf("Physics: Ball falls with y(t) = Y0 - 0.5*g*t^2, Train moves on inclined surface\n");
    printf("Goal: Train must reach ball X position before ball lands\n");
    printf("==============================================================================\n\n");
    
    // Simulation parameters
    double dt = 0.02;             // Time step (s) - 50 Hz control rate
    double sim_time = 0.0;        // Infinite simulation
    double t_end = 40.0;          // Simulation end time (s)
    
    // Seed random number generator
    srand((unsigned int)time(NULL));
    
    int num_scenarios = 10;
    int total_simulations = 0;
    
// Controller parameter definitions - TUNED for 100kg train with proper physics
// With m=100kg, F_max=3000N → a_max = 30 m/s²
// Higher Kp = faster response to position error (scaled for 100kg mass)
// Higher Ki = eliminate steady-state error faster
// Higher Kd = better damping at high speeds
ControllerParams PARAMS_PID = {500.0, 50.0, 200.0};  // Aggressive tuning scaled for 100kg train
    
    // Generate 10 random scenarios
    for (int scenario = 1; scenario <= num_scenarios; scenario++) {
        // Random angle: 0° to 45°
        double current_angle = ((double)rand() / RAND_MAX) * 45.0;
        
        // Random ball X position: 20m to 100m
        double ball_x = 20.0 + ((double)rand() / RAND_MAX) * 80.0;
        
        // Random ball initial Y height: 30m to 100m
        double ball_y_initial = 30.0 + ((double)rand() / RAND_MAX) * 70.0;
        
        // Random train initial X: 0m to (ball_x - 20m) to ensure some distance
        double max_train_x = (ball_x > 20.0) ? (ball_x - 20.0) : 0.0;
        double train_x = ((double)rand() / RAND_MAX) * max_train_x;
        
        total_simulations++;
        
        printf("\n[Scenario %d/%d]\n", scenario, num_scenarios);
        printf("  Angle: %.1f°\n", current_angle);
        printf("  Ball: (%.1fm, %.1fm)\n", ball_x, ball_y_initial);
        printf("  Train start: %.1fm\n", train_x);
        printf("  Generating...");
        fflush(stdout);
        
        // Create simulation configuration for PID controller
        SimulationConfig simulation = {
            .realtimePlot = NULL,
            .simulationMutex = NULL,
            .simulationThread = NULL,
            .simulationComplete = NULL,
            .name = NULL,
            .controller = pidController,
            .params = PARAMS_PID
        };
        
        // Allocate memory for simulation name with all parameters including Y height
        char *name_buffer = (char*)malloc(150 * sizeof(char));
        if (name_buffer) {
            sprintf(name_buffer, "Random_S%02d_A%02.0f_BallX%03.0fY%03.0f_TrainX%03.0f", 
                   scenario, current_angle, ball_x, ball_y_initial, train_x);
            simulation.name = name_buffer;
        }
        
        // Run simulation with current parameters
        ThreadData threadData = {
            .config = &simulation,
            .dt = dt,
            .n = (int)(t_end / dt),
            .sim_time = t_end,
            .windowIndex = total_simulations - 1,
            .modelCallback = objectModel,
            .landing_angle = current_angle,
            .ball_x_position = ball_x,
            .train_x_initial = train_x,
            .ball_y_initial = ball_y_initial
        };
        
#ifdef _WIN32
        HANDLE thread = (HANDLE)_beginthreadex(NULL, 0, runSimulation, &threadData, 0, NULL);
        WaitForSingleObject(thread, INFINITE);
        CloseHandle(thread);
#else
        pthread_t thread;
        pthread_create(&thread, NULL, runSimulation, &threadData);
        pthread_join(thread, NULL);
#endif
        
        printf(" Done!\n");
        
        // Free simulation name
        if (simulation.name) {
            free((void*)simulation.name);
        }
    }
    
    printf("\n\n=================================================================\n");
    printf("All random scenarios completed!\n\n");
    printf("Total CSV files generated: %d\n", total_simulations);
    printf("  - Random angles: 0-45°\n");
    printf("  - Random ball positions: 20-100m (X), 30-100m (Y)\n");
    printf("  - Random train initial X: 0 to (ball_x - 20m)\n");
    
    // Finalize plotting system
    closePlot();
    
    printf("\nAll simulation data saved to CSV files in 'csv_data/' directory.\n");
    printf("Run 'python visualize_simulation.py' to generate plots and animations.\n");
    printf("\nPress Enter to close...\n");
    getchar();
    
    return 0;
}
