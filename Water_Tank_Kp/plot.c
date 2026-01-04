#include "plot.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <pthread.h>
#endif

// Global state for plotting
static int useFallback = 0;

#ifdef _WIN32
static CRITICAL_SECTION gnuplotMutex;
static int mutexInitialized = 0;
#else
static pthread_mutex_t gnuplotMutex = PTHREAD_MUTEX_INITIALIZER;
#endif

// Structure to hold real-time plot data
#define MAX_PLOT_POINTS 2000  // Store all data points (100s / 0.1s = 1000 points, 2000 for safety)

typedef struct {
    double time;
    double level;
    double setpoint;
    double control;
} PlotDataPoint;

typedef struct {
    FILE *gnuplotPipe;
    char sanitizedName[256];
    int pointCount;
    PlotDataPoint *dataBuffer;
    int bufferSize;
    int bufferIndex;
    int windowIndex;
} RealtimePlot;

void initPlot(void) {
    // Check if gnuplot is available
#ifdef _WIN32
    FILE *test = _popen("gnuplot-qt5 --version 2>nul", "r");
    if (test == NULL) {
        test = _popen("gnuplot --version 2>nul", "r");
    }
#else
    FILE *test = popen("gnuplot --version 2>/dev/null", "r");
#endif
    
    if (test == NULL) {
        fprintf(stderr, "Warning: gnuplot not found. Falling back to CSV output.\n");
        fprintf(stderr, "Data will be saved to 'output.csv'. You can plot it with Excel or another tool.\n");
        useFallback = 1;
    } else {
#ifdef _WIN32
        _pclose(test);
#else
        pclose(test);
#endif
    }
}

void closePlot(void) {
    // Not needed for script file approach
}

int isPlotFallbackEnabled(void) {
    return useFallback;
}

ErrorCode initRealtimePlot(const char *controllerName, double Kp, int windowIndex, void **plotHandle) {
    if (plotHandle == NULL || controllerName == NULL) return ERROR_NULL_POINTER;
    
    *plotHandle = NULL;
    
    if (useFallback) return ERROR_SUCCESS;
    
    RealtimePlot *plot = (RealtimePlot*)malloc(sizeof(RealtimePlot));
    if (!plot) return ERROR_NULL_POINTER;
    
    // Sanitize controller name
    snprintf(plot->sanitizedName, sizeof(plot->sanitizedName), "%s", controllerName);
    for (int i = 0; plot->sanitizedName[i]; i++) {
        if (plot->sanitizedName[i] == ' ') plot->sanitizedName[i] = '_';
    }
    
    plot->pointCount = 0;
    plot->bufferSize = MAX_PLOT_POINTS;
    plot->bufferIndex = 0;
    plot->windowIndex = windowIndex;
    plot->gnuplotPipe = NULL;  // No real-time plotting, only save at end
    
    plot->dataBuffer = (PlotDataPoint*)malloc(MAX_PLOT_POINTS * sizeof(PlotDataPoint));
    if (!plot->dataBuffer) {
        free(plot);
        return ERROR_NULL_POINTER;
    }
    
    *plotHandle = plot;
    return ERROR_SUCCESS;
}

ErrorCode updateRealtimePlot(void *plotHandle, double time, double level, 
                             double setpoint, double control_signal) {
    if (!plotHandle) return ERROR_NULL_POINTER;
    
    RealtimePlot *plot = (RealtimePlot*)plotHandle;
    
    // Store in circular buffer
    plot->dataBuffer[plot->bufferIndex].time = time;
    plot->dataBuffer[plot->bufferIndex].level = level;
    plot->dataBuffer[plot->bufferIndex].setpoint = setpoint;
    plot->dataBuffer[plot->bufferIndex].control = control_signal;
    
    plot->bufferIndex = (plot->bufferIndex + 1) % plot->bufferSize;
    plot->pointCount++;
    
    // No real-time plotting - data is just stored and plotted at the end
    
    return ERROR_SUCCESS;
}

ErrorCode closeRealtimePlot(void *plotHandle, const char *controllerName) {
    if (!plotHandle) return ERROR_NULL_POINTER;
    if (controllerName == NULL) return ERROR_NULL_POINTER;
    
    RealtimePlot *plot = (RealtimePlot*)plotHandle;
    
    // Prepare data range
    int totalPoints = (plot->pointCount < plot->bufferSize) ? plot->pointCount : plot->bufferSize;
    int startIdx = (plot->pointCount < plot->bufferSize) ? 0 : plot->bufferIndex;
    
    // Open gnuplot pipe only for final PNG generation
#ifdef _WIN32
    _putenv("PATH=C:\\Program Files\\gnuplot\\bin;%PATH%");
    plot->gnuplotPipe = _popen("\"C:\\Program Files\\gnuplot\\bin\\wgnuplot.exe\"", "w");
#else
    plot->gnuplotPipe = popen("gnuplot -persist", "w");
#endif
    
    if (!plot->gnuplotPipe) {
        free(plot->dataBuffer);
        free(plot);
        return ERROR_CALLBACK_FAILED;
    }
    
    // Save to PNG file using datablocks (already defined from real-time updates)
    // Redefine datablocks with all collected data
    fprintf(plot->gnuplotPipe, "$level << EOD\n");
    for (int i = 0; i < totalPoints; i++) {
        int idx = (startIdx + i) % plot->bufferSize;
        fprintf(plot->gnuplotPipe, "%f %f\n", plot->dataBuffer[idx].time, plot->dataBuffer[idx].level);
    }
    fprintf(plot->gnuplotPipe, "EOD\n");
    
    fprintf(plot->gnuplotPipe, "$setpoint << EOD\n");
    for (int i = 0; i < totalPoints; i++) {
        int idx = (startIdx + i) % plot->bufferSize;
        fprintf(plot->gnuplotPipe, "%f %f\n", plot->dataBuffer[idx].time, plot->dataBuffer[idx].setpoint);
    }
    fprintf(plot->gnuplotPipe, "EOD\n");
    
    fprintf(plot->gnuplotPipe, "$control << EOD\n");
    for (int i = 0; i < totalPoints; i++) {
        int idx = (startIdx + i) % plot->bufferSize;
        fprintf(plot->gnuplotPipe, "%f %f\n", plot->dataBuffer[idx].time, plot->dataBuffer[idx].control);
    }
    fprintf(plot->gnuplotPipe, "EOD\n");
    
    // Now save to PNG using datablocks
    char outputName[512];
    snprintf(outputName, sizeof(outputName), "plot_%s.png", plot->sanitizedName);
    fprintf(plot->gnuplotPipe, "set terminal pngcairo size 1000,700 enhanced font 'Verdana,10'\n");
    fprintf(plot->gnuplotPipe, "set output '%s'\n", outputName);
    fprintf(plot->gnuplotPipe, "set multiplot layout 2,1\n");
    fprintf(plot->gnuplotPipe, "set grid\n");
    fprintf(plot->gnuplotPipe, "set xlabel 'Time (s)'\n");
    fprintf(plot->gnuplotPipe, "set key top right\n");
    
    // Plot water level using datablocks
    fprintf(plot->gnuplotPipe, "set title 'Water Tank Level Control - %s'\n", controllerName);
    fprintf(plot->gnuplotPipe, "set ylabel 'Water Level (m)'\n");
    fprintf(plot->gnuplotPipe, "plot $level using 1:2 with lines lw 2 lt rgb 'blue' title 'Actual Level', "
            "$setpoint using 1:2 with lines lw 2 lt rgb 'red' dashtype 2 title 'Setpoint'\n");
    
    // Plot control signal using datablock
    fprintf(plot->gnuplotPipe, "set title 'Control Signal (Inflow Rate) - %s'\n", controllerName);
    fprintf(plot->gnuplotPipe, "set ylabel 'Inflow (m³/s)'\n");
    fprintf(plot->gnuplotPipe, "plot $control using 1:2 with lines lw 2 lt rgb 'green' title 'Control Signal'\n");
    
    fprintf(plot->gnuplotPipe, "unset multiplot\n");
    fprintf(plot->gnuplotPipe, "set output\n");  // Close output file
    fprintf(plot->gnuplotPipe, "exit\n");  // Explicitly tell gnuplot to exit
    fflush(plot->gnuplotPipe);
    
    // Wait briefly for gnuplot to finish writing
#ifdef _WIN32
    Sleep(500);
#else
    usleep(500000);
#endif
    
    // Cleanup
    if (plot->dataBuffer) free(plot->dataBuffer);
#ifdef _WIN32
    _pclose(plot->gnuplotPipe);
#else
    pclose(plot->gnuplotPipe);
#endif
    
    printf("Plot saved to '%s'\n", outputName);
    
    free(plot);
    return ERROR_SUCCESS;
}

void generatePlot(double *time, double *level, double *setpoint, 
                  double *control_signal, int n, double Kp, const char *controllerName) {
    // Create sanitized filename (replace spaces with underscores)
    char sanitizedName[256];
    snprintf(sanitizedName, sizeof(sanitizedName), "%s", controllerName);
    for (int i = 0; sanitizedName[i]; i++) {
        if (sanitizedName[i] == ' ') sanitizedName[i] = '_';
    }
    
    if (useFallback) {
        printf("Plotting to CSV file (gnuplot not available)...\n");
        // Save all data to CSV with controller name
        char csvFilename[512];
        snprintf(csvFilename, sizeof(csvFilename), "output_%s.csv", sanitizedName);
        FILE *csvFile = fopen(csvFilename, "w");
        if (csvFile != NULL) {
            fprintf(csvFile, "Time,Level,Setpoint,Control_Signal\n");
            for (int i = 0; i < n; i++) {
                fprintf(csvFile, "%f,%f,%f,%f\n", time[i], level[i], setpoint[i], control_signal[i]);
            }
            fclose(csvFile);
            printf("Data saved to '%s'\n", csvFilename);
        }
    } else {
        printf("Generating plot...\n");
        printf("(Ignoring any gnuplot X11 display warnings...)\n");
        
        // Write data to temporary files with unique names
        char dataLevel[512], dataSetpoint[512], dataControl[512];
        snprintf(dataLevel, sizeof(dataLevel), "_data_level_%s.tmp", sanitizedName);
        snprintf(dataSetpoint, sizeof(dataSetpoint), "_data_setpoint_%s.tmp", sanitizedName);
        snprintf(dataControl, sizeof(dataControl), "_data_control_%s.tmp", sanitizedName);
        
        FILE *f1 = fopen(dataLevel, "w");
        FILE *f2 = fopen(dataSetpoint, "w");
        FILE *f3 = fopen(dataControl, "w");
        
        if (f1 && f2 && f3) {
            for (int i = 0; i < n; i++) {
                fprintf(f1, "%f %f\n", time[i], level[i]);
                fprintf(f2, "%f %f\n", time[i], setpoint[i]);
                fprintf(f3, "%f %f\n", time[i], control_signal[i]);
            }
            fclose(f1);
            fclose(f2);
            fclose(f3);
            
            // Create gnuplot script file with unique name
            char scriptName[512], outputName[512];
            snprintf(scriptName, sizeof(scriptName), "_plot_script_%s.gp", sanitizedName);
            snprintf(outputName, sizeof(outputName), "plot_%s.png", sanitizedName);
            
            FILE *script = fopen(scriptName, "w");
            if (script) {
                fprintf(script, "set terminal pngcairo size 1000,700 enhanced font 'Verdana,10'\n");
                fprintf(script, "set output '%s'\n", outputName);
                fprintf(script, "set multiplot layout 2,1\n");
                fprintf(script, "set title 'Water Tank Level Control - %s (Kp = %.2f)'\n", controllerName, Kp);
                fprintf(script, "set xlabel 'Time (s)'\n");
                fprintf(script, "set ylabel 'Water Level (m)'\n");
                fprintf(script, "set grid\n");
                fprintf(script, "set key top right\n");
                fprintf(script, "plot '%s' with lines lw 2 lt rgb 'blue' title 'Actual Level', ", dataLevel);
                fprintf(script, "'%s' with lines lw 2 lt rgb 'red' dashtype 2 title 'Setpoint'\n", dataSetpoint);
                fprintf(script, "set title 'Control Signal (Inflow Rate) - %s'\n", controllerName);
                fprintf(script, "set xlabel 'Time (s)'\n");
                fprintf(script, "set ylabel 'Inflow (m³/s)'\n");
                fprintf(script, "set grid\n");
                fprintf(script, "plot '%s' with lines lw 2 lt rgb 'green' title 'Control Signal'\n", dataControl);
                fprintf(script, "unset multiplot\n");
                fclose(script);
                
                // Run gnuplot with the script
                printf("Running gnuplot script...\n");
                char command[1024];
#ifdef _WIN32
                snprintf(command, sizeof(command), "gnuplot-qt5 %s 2>nul", scriptName);
                system(command);
                Sleep(500);
#else
                snprintf(command, sizeof(command), "gnuplot %s 2>/dev/null", scriptName);
                system(command);
                sleep(1);
#endif
                
                // Clean up temporary files
                printf("Cleaning up temporary files...\n");
                remove(dataLevel);
                remove(dataSetpoint);
                remove(dataControl);
                remove(scriptName);
            } else {
                printf("ERROR: Could not create plot script file!\n");
            }
        } else {
            printf("ERROR: Could not create temporary data files!\n");
        }
    }
    
#ifdef _WIN32
    char outputName[512];
    snprintf(outputName, sizeof(outputName), "plot_%s.png", sanitizedName);
    printf("\nChecking for plot file '%s'...\n", outputName);
    FILE *checkFile = fopen(outputName, "r");
    if (checkFile != NULL) {
        fclose(checkFile);
        printf("SUCCESS: Plot saved to '%s'\n", outputName);
        printf("Opening the image...\n");
        char openCommand[1024];
        snprintf(openCommand, sizeof(openCommand), "start %s", outputName);
        system(openCommand);
    } else if (!useFallback) {
        printf("ERROR: %s was not created.\n", outputName);
        printf("This may indicate gnuplot is not working properly.\n");
    }
#endif
}
