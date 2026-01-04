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
    int n = data->n;
    
    printf("[Thread %s] Starting simulation (Kp=%.2f, Ki=%.2f, Kd=%.2f)...\n", 
           sim->name,
           sim->params.Kp,
           sim->params.Ki,
           sim->params.Kd);
    
    // Initialize data collection (no real-time plotting)
    void *realtimePlot = NULL;
    ErrorCode plotErr = initRealtimePlot(sim->name, sim->params.Kp, data->windowIndex, &realtimePlot);
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
    WaterTank tank = {
        .level = 0.5,           // Start at 0.5 m
        .setpoint = 2.0,        // Target 2.0 m
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
            .area = 1.0,            // 1 m² cross-section
            .max_inflow = 0.5,      // Max 0.5 m³/s inflow
            .density = 1000.0,      // Water density (kg/m³)
            .callback = data->modelCallback,  // System model callback (Euler or Trapezoidal)
            .netFlowCallback = calculateTankNetFlow  // Net flow calculation callback
        }
    };
    
    // Run simulation for 100 seconds (optimal for visualization with 50-second buffer)
    int i = 0;
    double max_time = 125.0;  // Run for 125 seconds
    while (keep_running && (i * dt < max_time)) {
        double current_time = i * dt;
        
        // 8 setpoints: 5 normal + 3 aggressive at the end
        if (current_time < 20.0) {
            tank.setpoint = 2.0;  // Setpoint 1: 0-20s
        } else if (current_time < 40.0) {
            tank.setpoint = 1.5;  // Setpoint 2: 20-40s
        } else if (current_time < 60.0) {
            tank.setpoint = 2.5;  // Setpoint 3: 40-60s
        } else if (current_time < 80.0) {
            tank.setpoint = 1.8;  // Setpoint 4: 60-80s
        } else if (current_time < 100.0) {
            tank.setpoint = 2.2;  // Setpoint 5: 80-100s
        } else if (current_time < 110.0) {
            tank.setpoint = 3.0;  // Setpoint 6 AGGRESSIVE: 100-110s (10s, +0.8m jump)
        } else if (current_time < 117.0) {
            tank.setpoint = 1.0;  // Setpoint 7 AGGRESSIVE: 110-117s (7s, -2.0m drop!)
        } else {
            tank.setpoint = 2.8;  // Setpoint 8 AGGRESSIVE: 117-125s (8s, +1.8m jump!)
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
    printf("Running 125-second simulation and saving plots to PNG files...\n\n");
    
    // Simulation parameters
    double dt = 0.1;              // Time step (s)
    double sim_time = 0.0;        // Infinite simulation
    int n = 0;                    // Not used anymore
    
    // Configure 8 different controllers with optimized tuning
    // System characteristics: outflow_coeff=0.1, area=1.0, max_inflow=0.5
    SimulationConfig simulations[8] = {
        // P Controller: Regular proportional control (high steady-state error)
        {NULL, NULL, NULL, NULL, "P Controller", pController, {0.85, 0.0, 0.0}},
        
        // Adaptive P Controller: P with gain scheduling (better performance than regular P)
        {NULL, NULL, NULL, NULL, "P Adaptive Controller", adaptivePController, {2.5, 0.0, 0.0}},
        
        // PD Controller: Proportional-Derivative control (faster response, less overshoot)
        {NULL, NULL, NULL, NULL, "PD Controller", pdController, {0.40, 0.0, 0.60}},
        
        // Adaptive PD Controller: PD with gain scheduling
        {NULL, NULL, NULL, NULL, "PD Adaptive Controller", adaptivePdController, {2.8, 0.0, 0.45}},
        
        // PI Controller: Eliminates steady-state error with integral term
        {NULL, NULL, NULL, NULL, "PI Controller", piController, {0.30, 0.08, 0.0}},
        
        // Adaptive PI Controller: PI with gain scheduling
        {NULL, NULL, NULL, NULL, "PI Adaptive Controller", adaptivePiController, {0.80, 0.08, 0.0}},
        
        // PID Controller: Balanced all three terms for optimal performance
        {NULL, NULL, NULL, NULL, "PID Controller", pidController, {0.35, 0.08, 0.50}},
        
        // Adaptive PID Controller: PID with gain scheduling (ultimate performance)
        {NULL, NULL, NULL, NULL, "PID Adaptive Controller", adaptivePidController, {1.0, 0.08, 0.50}}
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
        threadData[s].sim_time = sim_time;
        threadData[s].windowIndex = s;
        threadData[s].modelCallback = tankModel;  // Euler integration
    }
    
#ifdef _WIN32
    // Windows threads
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
        {NULL, NULL, NULL, NULL, "P Controller Trapezoidal", pController, {0.85, 0.0, 0.0}},
        {NULL, NULL, NULL, NULL, "P Adaptive Controller Trapezoidal", adaptivePController, {2.5, 0.0, 0.0}},
        {NULL, NULL, NULL, NULL, "PD Controller Trapezoidal", pdController, {0.40, 0.0, 0.60}},
        {NULL, NULL, NULL, NULL, "PD Adaptive Controller Trapezoidal", adaptivePdController, {2.8, 0.0, 0.45}},
        {NULL, NULL, NULL, NULL, "PI Controller Trapezoidal", piController, {0.30, 0.08, 0.0}},
        {NULL, NULL, NULL, NULL, "PI Adaptive Controller Trapezoidal", adaptivePiController, {0.80, 0.08, 0.0}},
        {NULL, NULL, NULL, NULL, "PID Controller Trapezoidal", pidController, {0.35, 0.08, 0.50}},
        {NULL, NULL, NULL, NULL, "PID Adaptive Controller Trapezoidal", adaptivePidController, {1.0, 0.08, 0.50}}
    };
    
    // Create thread data for trapezoidal simulations
    ThreadData threadDataTrap[8];
    for (int s = 0; s < 8; s++) {
        threadDataTrap[s].config = &simulationsTrapezoidal[s];
        threadDataTrap[s].dt = dt;
        threadDataTrap[s].n = n;
        threadDataTrap[s].sim_time = sim_time;
        threadDataTrap[s].windowIndex = s + 8;  // Offset window index to avoid overlap
        threadDataTrap[s].modelCallback = tankModelTrapezoidal;  // Trapezoidal integration
    }
    
#ifdef _WIN32
    // Windows threads for trapezoidal simulations
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
    
    printf("\n=================================================================\n");
    printf("All simulations completed!\n\n");
    
    // Static plots are saved by real-time plotting
    printf("Total plots generated: 16 (8 Euler + 8 Trapezoidal)\n");
    printf("All plots have been saved.\n");
    
    printf("\nPress Enter to close...\n");
    getchar();
    
    return 0;
}