#ifndef PLOT_H
#define PLOT_H

#include "controller.h"

// Initialize plotting system (checks for gnuplot availability)
void initPlot(void);

// Close plotting system (cleanup)
void closePlot(void);

// Generate plot with falling object simulation data
// Parameters:
//   time: array of time values
//   level: array of position values (train position)
//   setpoint: array of setpoint values (falling object position)
//   control_signal: array of control signal values (applied force)
//   n: number of data points
//   Kp: proportional gain (for plot title)
//   controllerName: name of the controller (for filename and title)
void generatePlot(double *time, double *level, double *setpoint, 
                  double *control_signal, int n, double Kp, const char *controllerName);

// Check if fallback mode is enabled (CSV output instead of plotting)
int isPlotFallbackEnabled(void);

// Real-time plotting functions
// Initialize real-time plot for a specific controller
// Returns: ErrorCode (ERROR_SUCCESS or error code), sets plotHandle to plot pointer or NULL
ErrorCode initRealtimePlot(const char *controllerName, int windowIndex, void **plotHandle);

// Update real-time plot with new data point
// Returns: ErrorCode
ErrorCode updateRealtimePlot(void *plotHandle, double time, double level, 
                             double setpoint, double control_signal,
                             double velocity, double acceleration,
                             double error_derivative, double error_integral);

// Close real-time plot and save final image
// Returns: ErrorCode
ErrorCode closeRealtimePlot(void *plotHandle, const char *controllerName);

#endif // PLOT_H
