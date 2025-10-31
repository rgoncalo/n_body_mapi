#pragma once
#include <vector>
#include "Body.hpp"
#include "Universe.hpp"
#include <iostream>

class PhysicsEngine {
public:
    void advance(Universe& universe, double dt);
    // Performs one integration step using Newtonian gravity
    void integrateStep(std::vector<Body>& bodies, double dt);
};
