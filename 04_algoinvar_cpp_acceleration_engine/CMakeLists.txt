cmake_minimum_required(VERSION 3.14)
project(algoinvar_cpp VERSION 1.0.0 LANGUAGES CXX)

# Enforce Modern C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization flags
if(MSVC)
    add_compile_options(/O2 /W4 /permissive-)
else()
    add_compile_options(-O3 -Wall -Wextra -pedantic -march=native)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Static library for core evaluation engine
add_library(algoinvar_fast_core STATIC
    src/algoinvar_fast.cpp
)

# Standalone benchmark binary target
add_executable(algoinvar_bench
    src/main.cpp
)
target_link_libraries(algoinvar_bench PRIVATE algoinvar_fast_core)

# Optional pybind11 Python extension module
find_package(pybind11 QUIET)
if(pybind11_FOUND)
    pybind11_add_module(algoinvar_core
        bindings/pybind_module.cpp
    )
    target_link_libraries(algoinvar_core PRIVATE algoinvar_fast_core)
endif()
