#include "plot.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/stat.h>
#endif

// Structure to hold simulation data for CSV export
#define MAX_PLOT_POINTS 2000  // Store all data points

typedef struct {
    double time;
    double level;      // Train position
    double setpoint;   // Falling object position
    double control;    // Applied force
    double velocity;   // Train velocity
    double acceleration; // Train acceleration
    double error_derivative; // Rate of change of error (de/dt)
    double error_integral;   // Accumulated error integral
} PlotDataPoint;

typedef struct {
    char sanitizedName[256];
    int pointCount;
    PlotDataPoint *dataBuffer;
    int bufferSize;
    int bufferIndex;
} RealtimePlot;

void initPlot(void) {
    // Create CSV data directory
#ifdef _WIN32
    CreateDirectoryA("csv_data", NULL);
#else
    mkdir("csv_data", 0755);
#endif
    printf("CSV data directory created. Data will be saved for Python visualization.\n");
}

void closePlot(void) {
    printf("\nAll simulation data saved to CSV files in 'csv_data/' directory.\n");
    printf("Run 'python visualize_simulation.py' to generate plots and animations.\n");
}

int isPlotFallbackEnabled(void) {
    return 0;  // Always use CSV export
}

ErrorCode initRealtimePlot(const char *controllerName, int windowIndex, void **plotHandle) {
    if (plotHandle == NULL || controllerName == NULL) return ERROR_NULL_POINTER;
    
    *plotHandle = NULL;
    
    // Create plot structure to store data
    RealtimePlot *plot = (RealtimePlot*)malloc(sizeof(RealtimePlot));
    if (!plot) return ERROR_NULL_POINTER;
    
    // Sanitize controller name (replace spaces with underscores)
    snprintf(plot->sanitizedName, sizeof(plot->sanitizedName), "%s", controllerName);
    for (int i = 0; plot->sanitizedName[i]; i++) {
        if (plot->sanitizedName[i] == ' ') plot->sanitizedName[i] = '_';
    }
    
    plot->pointCount = 0;
    plot->bufferSize = MAX_PLOT_POINTS;
    plot->bufferIndex = 0;
    
    plot->dataBuffer = (PlotDataPoint*)malloc(MAX_PLOT_POINTS * sizeof(PlotDataPoint));
    if (!plot->dataBuffer) {
        free(plot);
        return ERROR_NULL_POINTER;
    }
    
    *plotHandle = plot;
    return ERROR_SUCCESS;
}

ErrorCode updateRealtimePlot(void *plotHandle, double time, double level, 
                             double setpoint, double control_signal,
                             double velocity, double acceleration,
                             double error_derivative, double error_integral) {
    if (!plotHandle) return ERROR_NULL_POINTER;
    
    RealtimePlot *plot = (RealtimePlot*)plotHandle;
    
    // Store data point in buffer
    int idx = plot->bufferIndex;
    plot->dataBuffer[idx].time = time;
    plot->dataBuffer[idx].level = level;
    plot->dataBuffer[idx].setpoint = setpoint;
    plot->dataBuffer[idx].control = control_signal;
    plot->dataBuffer[idx].velocity = velocity;
    plot->dataBuffer[idx].acceleration = acceleration;
    plot->dataBuffer[idx].error_derivative = error_derivative;
    plot->dataBuffer[idx].error_integral = error_integral;
    
    // Update indices
    plot->bufferIndex = (plot->bufferIndex + 1) % plot->bufferSize;
    plot->pointCount++;
    
    return ERROR_SUCCESS;
}

ErrorCode closeRealtimePlot(void *plotHandle, const char *controllerName) {
    if (!plotHandle) return ERROR_NULL_POINTER;
    if (controllerName == NULL) return ERROR_NULL_POINTER;
    
    RealtimePlot *plot = (RealtimePlot*)plotHandle;
    
    // Calculate how many points we have
    int totalPoints = (plot->pointCount < plot->bufferSize) ? plot->pointCount : plot->bufferSize;
    int startIdx = (plot->pointCount < plot->bufferSize) ? 0 : plot->bufferIndex;
    
    if (totalPoints < 1) {
        fprintf(stderr, "Warning: No data to save for %s\n", controllerName);
        free(plot->dataBuffer);
        free(plot);
        return ERROR_CALLBACK_FAILED;
    }
    
    // Save to CSV file
    char csvFilename[512];
    snprintf(csvFilename, sizeof(csvFilename), "csv_data/%s.csv", plot->sanitizedName);
    
    FILE *csvFile = fopen(csvFilename, "w");
    if (!csvFile) {
        fprintf(stderr, "Error: Could not open CSV file %s\n", csvFilename);
        free(plot->dataBuffer);
        free(plot);
        return ERROR_CALLBACK_FAILED;
    }
    
    // Write CSV header
    fprintf(csvFile, "time,train_position,falling_object_position,applied_force,train_velocity,train_acceleration,error_derivative,error_integral\n");
    
    // Write all data points
    for (int i = 0; i < totalPoints; i++) {
        int idx = (startIdx + i) % plot->bufferSize;
        fprintf(csvFile, "%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n",
                plot->dataBuffer[idx].time,
                plot->dataBuffer[idx].level,
                plot->dataBuffer[idx].setpoint,
                plot->dataBuffer[idx].control,
                plot->dataBuffer[idx].velocity,
                plot->dataBuffer[idx].acceleration,
                plot->dataBuffer[idx].error_derivative,
                plot->dataBuffer[idx].error_integral);
    }
    
    fclose(csvFile);
    printf("CSV data saved to '%s' (%d points)\n", csvFilename, totalPoints);
    
    // Cleanup
    free(plot->dataBuffer);
    free(plot);
    
    return ERROR_SUCCESS;
}

void generatePlot(double *time, double *level, double *setpoint, 
                  double *control_signal, int n, double Kp, const char *controllerName) {
    // This function is deprecated - all data is now saved via real-time collection
    // Just print a message
    (void)time; (void)level; (void)setpoint; (void)control_signal; 
    (void)n; (void)Kp; (void)controllerName;
    printf("Note: generatePlot() called but data is already saved via CSV export\n");
}
