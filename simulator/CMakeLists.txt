cmake_minimum_required(VERSION 3.18)
project(MyLittleBigUniverse LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Release)

# ==========================================================
# Core Simulation Library
# ==========================================================
add_library(core
    src/core/Body.cpp
    src/core/PhysicsEngine.cpp
    src/core/Universe.cpp
)
target_include_directories(core PUBLIC src)

# ==========================================================
# Executable
# ==========================================================
add_executable(simulate
    src/app/simulate.cpp
    src/app/initialConditions.cpp
    src/io/outputWritter.cpp

)
target_link_libraries(simulate PRIVATE core)

# ==========================================================
# Global include directories
# ==========================================================
include_directories(src)
