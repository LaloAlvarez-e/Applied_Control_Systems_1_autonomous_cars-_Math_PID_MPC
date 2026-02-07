#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <signal.h>
#include "plot.h"
#include "controller.h"
#include "watertank.h"

#ifdef _WIN32
#include <windows.h>
#include <process.h>
#else
#include <unistd.h>
#include <pthread.h>
#endif

// Global flag for Ctrl-C handling
volatile sig_atomic_t keep_running = 1;

#ifdef _WIN32
BOOL WINAPI console_ctrl_handler(DWORD dwCtrlType) {
    if (dwCtrlType == CTRL_C_EVENT || dwCtrlType == CTRL_BREAK_EVENT) {
        printf("\n\nCtrl-C detected! Force terminating...\\n");
        fflush(stdout);
        // Force immediate exit - don't wait for threads
        TerminateProcess(GetCurrentProcess(), 1);
        return TRUE;
    }
    return FALSE;
}
#else
void signal_handler(int signum) {
    (void)signum;
    printf("\n\nCtrl-C detected! Force terminating...\n");
    fflush(stdout);
    _exit(1);  // Force immediate exit
}
#endif

// Structure to hold simulation results
typedef struct {
    double *time;
    double *level;
    double *setpoint_array;
    double *control_signal;
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
    
    // Initialize water tank with controller configuration
    // Python reference: vol_o1_i=30 m³, vol_r1_i=70 m³, radius=5m → area=π*r²≈78.54 m²
    // Percentage-based: 0% = empty, 100% = max_level (4.507 m)
    double tank_radius = 5.0;  // Tank radius in meters
    double tank_area = M_PI * tank_radius * tank_radius;  // π × r² ≈ 78.54 m² (matches Python)
    double max_level = 4.507;  // Maximum tank height in meters (100% = 4.507m)
    double max_volume = tank_area * max_level;  // V_max = area × max_level ≈ 354.00 m³
    
    // Initialize volume from initial level percentage
    double initial_level_pct = 30.0;  // Start at 30%
    double initial_volume = (initial_level_pct / 100.0) * max_volume;  // volume = (30/100) × 354 = 106.2 m³
    double initial_height = initial_volume / tank_area;  // height = volume / area = 106.2 / 78.54 = 1.352 m
    
    WaterTank tank = {
        .level = initial_level_pct, // Output: level in percentage (30%)
        .volume = initial_volume,  // Internal state: volume in m³ (106.2 m³)
        .height = initial_height,  // Internal tracking: height in m (1.352 m)
        .setpoint = 70.0,       // Target 70% (3.1549 m height)
        .inflow = 0.0,          // Will be controlled
        .previousNetFlow = 0.0, // Initialize for trapezoidal integration
        .controller = {
            .params = &sim->params,
            .state = &controllerState,
            .getSetpoint = getTankSetpoint,
            .getOutput = getTankOutput,
            .dt = dt
        },
        .model = {
            .outflow_coeff = 0.1,   // Outflow coefficient
            .area = tank_area,      // 78.54 m² cross-section (matches Python π*r²)
            .max_inflow = 50.0,     // Max 50 m³/s inflow (increased for high Kp values)
            .density = 1000.0,      // Water density (kg/m³) - matches Python density_water=1000
            .max_level = max_level, // 4.507 m maximum height (100%)
            .callback = data->modelCallback,  // System model callback (Euler/Trapezoidal/Simplified)
            .netFlowCallback = (data->modelCallback == tankModelTrapezoidalSimplified) ? 
                               calculateTankNetFlowSimplified : calculateTankNetFlow
        }
    };
    
    // Run simulation matching Python reference
    int i = 0;
    double max_time = data->sim_time;  // Use sim_time from thread data
    while (keep_running && (i * dt < max_time)) {
        double current_time = i * dt;
        
        // Setpoint profile matching Python Tank 1 reference (percentage 0-100%)
        // Setpoint transitions: 70%→20%→90%→50% of max height (4.507 m)
        if (current_time < 12.0) {
            tank.setpoint = 70.0;  // 70% (3.1549 m)
        } else if (current_time < 24.0) {
            tank.setpoint = 20.0;  // 20% (0.9014 m)
        } else if (current_time < 36.0) {
            tank.setpoint = 90.0;  // 90% (4.0563 m)
        } else {
            tank.setpoint = 50.0;  // 50% (2.2535 m)
        }
        
        // Update tank using specified controller
        double current_level;
        ErrorCode err = updateSystem(&tank, dt, &current_level, 
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
            ErrorCode plotErr = updateRealtimePlot(realtimePlot, current_time, 
                                                  current_level, tank.setpoint, tank.inflow);
            if (plotErr != ERROR_SUCCESS) {
                printf("[Thread %s] Warning: Data update failed at t=%.2f: Error code %d\n", 
                       sim->name, current_time, plotErr);
            }
        }
        
        i++;
        
        // No real-time delay - run simulation as fast as possible
    }
    
    // Save final plot to PNG
    if (realtimePlot) {
        printf("[Thread %s] Saving plot to PNG...\n", sim->name);
        ErrorCode plotErr = closeRealtimePlot(realtimePlot, sim->name);
        if (plotErr != ERROR_SUCCESS) {
            printf("[Thread %s] Warning: Failed to save plot: Error code %d\n", sim->name, plotErr);
        }
    }
    
    printf("[Thread %s] Completed!\n", sim->name);
    
#ifdef _WIN32
    return 0;
#else
    return NULL;
#endif
}

int main() {
    // Install signal handler for Ctrl-C
#ifdef _WIN32
    SetConsoleCtrlHandler(console_ctrl_handler, TRUE);
#else
    signal(SIGINT, signal_handler);
#endif
    
    printf("Water Tank Control System - Comparing P, PI, PD, and PID Controllers\n");
    printf("=====================================================================\n");
    printf("Running 50-second simulation (matching Python reference) and saving plots to PNG files...\n\n");
    
    // Simulation parameters (matching Python reference: calculus_sim_waterTanks_Kp_controller.py)
    double dt = 0.04;             // Time step (s) - matches Python dt=0.04
    int n = 0;                    // Not used anymore
    double t_end = 50.0;          // Simulation end time (s) - matches Python t_end=50
    
    // Controller parameter definitions
    // System now uses PERCENTAGE (0-100%) for level and setpoint
    // Error is in percentage units, so gains can be smaller
    // Python reference: Kp=1000 (kg/s per m³ error) → C_Kp = 1000/1000 = 1.0 (m³/s per m³ error)
    // Since percentage error ~22x larger than volume error, we can use smaller gains
    // Percentage range 0-100, typical error = 40% → control needs to produce appropriate m³/s flow
    const ControllerParams PARAMS_P           = {1.0,  0.0, 0.0};   // P: Kp=1.0
    const ControllerParams PARAMS_P_ADAPTIVE  = {5.0,  0.0, 0.0};   // P Adaptive: Kp=5.0
    const ControllerParams PARAMS_PD          = {0.40, 0.0, 0.60};  // PD Controller
    const ControllerParams PARAMS_PD_ADAPTIVE = {2.8,  0.0, 0.45};  // PD Adaptive
    const ControllerParams PARAMS_PI          = {0.30, 0.08, 0.0};  // PI Controller
    const ControllerParams PARAMS_PI_ADAPTIVE = {0.80, 0.08, 0.0};  // PI Adaptive
    const ControllerParams PARAMS_PID         = {0.35, 0.08, 0.50}; // PID Controller
    const ControllerParams PARAMS_PID_ADAPTIVE = {1.0, 0.08, 0.50}; // PID Adaptive
    
    // Configure 8 different controllers with optimized tuning
    SimulationConfig simulations[8] = {
        // P Controller: Regular proportional control (high steady-state error)
        {NULL, NULL, NULL, NULL, "P Controller", pController, PARAMS_P},
        
        // Adaptive P Controller: P with gain scheduling (better performance than regular P)
        {NULL, NULL, NULL, NULL, "P Adaptive Controller", adaptivePController, PARAMS_P_ADAPTIVE},
        
        // PD Controller: Proportional-Derivative control (faster response, less overshoot)
        {NULL, NULL, NULL, NULL, "PD Controller", pdController, PARAMS_PD},
        
        // Adaptive PD Controller: PD with gain scheduling
        {NULL, NULL, NULL, NULL, "PD Adaptive Controller", adaptivePdController, PARAMS_PD_ADAPTIVE},
        
        // PI Controller: Eliminates steady-state error with integral term
        {NULL, NULL, NULL, NULL, "PI Controller", piController, PARAMS_PI},
        
        // Adaptive PI Controller: PI with gain scheduling
        {NULL, NULL, NULL, NULL, "PI Adaptive Controller", adaptivePiController, PARAMS_PI_ADAPTIVE},
        
        // PID Controller: Balanced all three terms for optimal performance
        {NULL, NULL, NULL, NULL, "PID Controller", pidController, PARAMS_PID},
        
        // Adaptive PID Controller: PID with gain scheduling (ultimate performance)
        {NULL, NULL, NULL, NULL, "PID Adaptive Controller", adaptivePidController, PARAMS_PID_ADAPTIVE}
    };
    
    printf("Running simulations for all controller types in parallel...\n");
    printf("=================================================================\n\n");
    
    // ============= FIRST RUN: Euler Integration (Standard) =============
    printf("Phase 1: Running with Euler integration (standard model)...\n\n");
    
    // Create thread data for each simulation with Euler model
    ThreadData threadData[8];
    for (int s = 0; s < 8; s++) {
        threadData[s].config = &simulations[s];
        threadData[s].dt = dt;
        threadData[s].n = n;
        threadData[s].sim_time = t_end;  // Use t_end for simulation time
        threadData[s].windowIndex = s;
        threadData[s].modelCallback = tankModel;  // Euler integration
    }
    
#ifdef _WIN32
    // Windows threadst_end;  // Use t_end for simulation time
    HANDLE threads[8];
    for (int s = 0; s < 8; s++) {
        threads[s] = (HANDLE)_beginthreadex(NULL, 0, runSimulation, &threadData[s], 0, NULL);
        if (threads[s] == NULL) {
            printf("Failed to create thread for %s\n", simulations[s].name);
        }
    }
    
    // Wait for all threads to complete with timeout
    DWORD waitResult = WaitForMultipleObjects(8, threads, TRUE, INFINITE);
    
    // Close thread handles
    for (int s = 0; s < 8; s++) {
        CloseHandle(threads[s]);
    }
    
    printf("\nPhase 1 completed. Euler integration plots saved.\n\n");
#else
    // POSIX threads
    pthread_t threads[8];
    for (int s = 0; s < 8; s++) {
        if (pthread_create(&threads[s], NULL, runSimulation, &threadData[s]) != 0) {
            printf("Failed to create thread for %s\n", simulations[s].name);
        }
    }
    
    // Wait for all threads to complete
    for (int s = 0; s < 8; s++) {
        pthread_join(threads[s], NULL);
    }
    
    printf("\nPhase 1 completed. Euler integration plots saved.\n\n");
#endif
    
    // ============= SECOND RUN: Trapezoidal Integration =============
    printf("Phase 2: Running with Trapezoidal integration (improved accuracy)...\n\n");
    
    // Reconfigure all simulations with Trapezoidal model and update plot names
    SimulationConfig simulationsTrapezoidal[8] = {
        {NULL, NULL, NULL, NULL, "P Controller Trapezoidal", pController, PARAMS_P},
        {NULL, NULL, NULL, NULL, "P Adaptive Controller Trapezoidal", adaptivePController, PARAMS_P_ADAPTIVE},
        {NULL, NULL, NULL, NULL, "PD Controller Trapezoidal", pdController, PARAMS_PD},
        {NULL, NULL, NULL, NULL, "PD Adaptive Controller Trapezoidal", adaptivePdController, PARAMS_PD_ADAPTIVE},
        {NULL, NULL, NULL, NULL, "PI Controller Trapezoidal", piController, PARAMS_PI},
        {NULL, NULL, NULL, NULL, "PI Adaptive Controller Trapezoidal", adaptivePiController, PARAMS_PI_ADAPTIVE},
        {NULL, NULL, NULL, NULL, "PID Controller Trapezoidal", pidController, PARAMS_PID},
        {NULL, NULL, NULL, NULL, "PID Adaptive Controller Trapezoidal", adaptivePidController, PARAMS_PID_ADAPTIVE}
    };
    
    // Create thread data for trapezoidal simulations
    ThreadData threadDataTrap[8];
    for (int s = 0; s < 8; s++) {
        threadDataTrap[s].config = &simulationsTrapezoidal[s];
        threadDataTrap[s].dt = dt;
        threadDataTrap[s].n = n;
        threadDataTrap[s].sim_time = t_end;  // Use t_end for simulation time
        threadDataTrap[s].windowIndex = s + 8;  // Offset window index to avoid overlap
        threadDataTrap[s].modelCallback = tankModelTrapezoidal;  // Trapezoidal integration
    }
    
#ifdef _WIN32
    // Windows threads for trapezoidat_end;  // Use t_end for simulation timeions
    HANDLE threadsTrap[8];
    for (int s = 0; s < 8; s++) {
        threadsTrap[s] = (HANDLE)_beginthreadex(NULL, 0, runSimulation, &threadDataTrap[s], 0, NULL);
        if (threadsTrap[s] == NULL) {
            printf("Failed to create thread for %s\n", simulationsTrapezoidal[s].name);
        }
    }
    
    // Wait for all trapezoidal threads to complete
    WaitForMultipleObjects(8, threadsTrap, TRUE, INFINITE);
    
    // Close thread handles
    for (int s = 0; s < 8; s++) {
        CloseHandle(threadsTrap[s]);
    }
    
    printf("\nPhase 2 completed. Trapezoidal integration plots saved.\n");
#else
    // POSIX threads for trapezoidal simulations
    pthread_t threadsTrap[8];
    for (int s = 0; s < 8; s++) {
        if (pthread_create(&threadsTrap[s], NULL, runSimulation, &threadDataTrap[s]) != 0) {
            printf("Failed to create thread for %s\n", simulationsTrapezoidal[s].name);
        }
    }
    
    // Wait for all trapezoidal threads to complete
    for (int s = 0; s < 8; s++) {
        pthread_join(threadsTrap[s], NULL);
    }
    
    printf("\nPhase 2 completed. Trapezoidal integration plots saved.\n");
#endif
    
    // ============= THIRD RUN: Simplified Model (No Outflow) =============
    printf("\nPhase 3: Running with Simplified model (no outflow - matches Python reference)...\n\n");
    
    // All 8 controllers for simplified model comparison
    SimulationConfig simulationsSimplified[8] = {
        {NULL, NULL, NULL, NULL, "P Controller Simplified", pController, PARAMS_P},
        {NULL, NULL, NULL, NULL, "P Adaptive Controller Simplified", adaptivePController, PARAMS_P_ADAPTIVE},
        {NULL, NULL, NULL, NULL, "PD Controller Simplified", pdController, PARAMS_PD},
        {NULL, NULL, NULL, NULL, "PD Adaptive Controller Simplified", adaptivePdController, PARAMS_PD_ADAPTIVE},
        {NULL, NULL, NULL, NULL, "PI Controller Simplified", piController, PARAMS_PI},
        {NULL, NULL, NULL, NULL, "PI Adaptive Controller Simplified", adaptivePiController, PARAMS_PI_ADAPTIVE},
        {NULL, NULL, NULL, NULL, "PID Controller Simplified", pidController, PARAMS_PID},
        {NULL, NULL, NULL, NULL, "PID Adaptive Controller Simplified", adaptivePidController, PARAMS_PID_ADAPTIVE}
    };
    
    // Create thread data for simplified simulations
    ThreadData threadDataSimp[8];
    for (int s = 0; s < 8; s++) {
        threadDataSimp[s].config = &simulationsSimplified[s];
        threadDataSimp[s].dt = dt;
        threadDataSimp[s].n = n;
        threadDataSimp[s].sim_time = t_end;  // Use t_end for simulation time
        threadDataSimp[s].windowIndex = s + 16;  // Offset window index to avoid overlap
        threadDataSimp[s].modelCallback = tankModelTrapezoidalSimplified;  // Simplified model
    }
    
#ifdef _WIN32
    // Windows threads for simplified simulations
    HANDLE threadsSimp[8];
    for (int s = 0; s < 8; s++) {
        threadsSimp[s] = (HANDLE)_beginthreadex(NULL, 0, runSimulation, &threadDataSimp[s], 0, NULL);
        if (threadsSimp[s] == NULL) {
            printf("Failed to create thread for %s\n", simulationsSimplified[s].name);
        }
    }
    
    // Wait for all simplified threads to complete
    WaitForMultipleObjects(8, threadsSimp, TRUE, INFINITE);
    
    // Close thread handles
    for (int s = 0; s < 8; s++) {
        CloseHandle(threadsSimp[s]);
    }
    
    printf("\nPhase 3 completed. Simplified model plots saved.\n");
#else
    // POSIX threads for simplified simulations
    pthread_t threadsSimp[8];
    for (int s = 0; s < 8; s++) {
        if (pthread_create(&threadsSimp[s], NULL, runSimulation, &threadDataSimp[s]) != 0) {
            printf("Failed to create thread for %s\n", simulationsSimplified[s].name);
        }
    }
    
    // Wait for all simplified threads to complete
    for (int s = 0; s < 8; s++) {
        pthread_join(threadsSimp[s], NULL);
    }
    
    printf("\nPhase 3 completed. Simplified model plots saved.\n");
#endif
    
    printf("\n=================================================================\n");
    printf("All simulations completed!\n\n");
    
    // Static plots are saved by real-time plotting
    printf("Total plots generated: 24 (8 Euler + 8 Trapezoidal + 8 Simplified)\n");
    printf("All plots have been saved.\n");
    
    printf("\nPress Enter to close...\n");
    getchar();
    
    return 0;
}