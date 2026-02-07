cmake_minimum_required(VERSION 3.10)
project(freefall_object C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Add executable
add_executable(freefall_object
    main.c
    fallingobject.c
    controller.c
    plot.c
)

# Link pthread on Unix-like systems
if(UNIX)
    target_link_libraries(freefall_object pthread m)
else()
    target_link_libraries(freefall_object)
endif()

# Set include directories
target_include_directories(freefall_object PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Enable warnings
if(MSVC)
    target_compile_options(freefall_object PRIVATE /W4)
else()
    target_compile_options(freefall_object PRIVATE -Wall -Wextra)
endif()
