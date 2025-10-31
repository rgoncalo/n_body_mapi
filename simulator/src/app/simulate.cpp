#include <iostream>
#include <vector>
#include <cmath>
#include "core/Body.hpp"
#include "core/PhysicsEngine.hpp"
#include "core/Universe.hpp"
#include "initialConditions.hpp"
#include "io/outputWritter.hpp"

int main(int argc, char* argv[]) {
    // ----------------------------------------------------
    // 1. Load configuration
    // ----------------------------------------------------
    int totalBodies = 30;
    double dt = 3600;             // seconds
    //double totalTime = 315360000;    // seconds
    double totalTime = 36000;    // seconds

    if (argc > 1) totalBodies = std::atoi(argv[1]);
    if (argc > 2) dt = std::atof(argv[2]);
    if (argc > 3) totalTime = std::atof(argv[3]);
    auto bodies = generateInitialConditions(totalBodies);

    std::cout << "Simulation dt = " << dt << " s, total time = " << totalTime << " s\n";

    // ----------------------------------------------------
    // 2. Create Universe and PhysicsEngine
    // ----------------------------------------------------
    Universe universe;                 // container for all bodies
    PhysicsEngine physicsEngine;       // computes forces and advances bodies

    // ----------------------------------------------------
    // 3. Initialize Bodies (example: Sun + Earth)
    // ----------------------------------------------------
    for (const auto& body : bodies) {
        universe.addBody(body);
    }

    std::cout << "Initialized " << universe.getNumBodies() << " bodies\n";

    // ----------------------------------------------------
    // 4. Prepare output
    // ----------------------------------------------------
    OutputWriter writer("../simulation_output.txt");

    // ----------------------------------------------------
    // 5. Simulation Loop with progress bar
    // ----------------------------------------------------
    double currentTime = 0.0;
    size_t stepCounter = 0;

    size_t totalSteps = static_cast<size_t>(totalTime / dt);
    const size_t progressMarkers = 10; // each # = 10%
    size_t nextMarker = 1;             // next 10% threshold

    std::cout << "Starting Simulation...\n";
    std::cout << "[          ]"; // empty progress bar
    std::cout << "\r[";         // start filling

    while (currentTime < totalTime) {
        // Advance simulation by one timestep
        physicsEngine.advance(universe, dt);

        // Save current step to txt
        writer.writeStep(universe.getBodies(), currentTime);

        // Update progress bar at each 10% increment
        if (stepCounter >= nextMarker * totalSteps / progressMarkers) {
            std::cout << "#" << std::flush;
            ++nextMarker;
        }

        currentTime += dt;
        ++stepCounter;
    }

    // Finish progress bar
    std::cout << "] Done!\n";
    std::cout << "Simulation finished.\n";

    return 0;
}
