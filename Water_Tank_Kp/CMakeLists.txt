cmake_minimum_required(VERSION 3.10)
project(WaterTankKp C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Set default build directory if not specified
if(NOT CMAKE_BINARY_DIR)
    set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/build)
endif()

# Create build directory if it doesn't exist
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR})

# Add executable (now includes all 4 controllers: P, PI, PD, PID)
add_executable(water_tank_kp main.c plot.c controller.c watertank.c)

# Link math library (required for math.h functions like sin, cos, etc.)
target_link_libraries(water_tank_kp m)

# Set compiler warnings
if(MSVC)
    target_compile_options(water_tank_kp PRIVATE /W4)
else()
    target_compile_options(water_tank_kp PRIVATE -Wall -Wextra -pedantic)
endif()

# Optional: Set output directory
set_target_properties(water_tank_kp PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)
