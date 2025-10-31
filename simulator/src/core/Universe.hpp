#pragma once
#include <vector>
#include "Body.hpp"

class Universe {
public:
    Universe() = default;

    void addBody(const Body& body) { bodies_.push_back(body); }

    std::vector<Body>& getBodies() { return bodies_; }
    const std::vector<Body>& getBodies() const { return bodies_; }

    size_t getNumBodies() const { return bodies_.size(); }

private:
    std::vector<Body> bodies_;
};
