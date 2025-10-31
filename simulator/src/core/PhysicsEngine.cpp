#include "PhysicsEngine.hpp"
#include "Universe.hpp"
#include <vector>
#include <cmath>
#include <iostream>

// -------------------- Vec3 helper functions --------------------
namespace {

Vec3 operator+(const Vec3& a, const Vec3& b) {
    return Vec3{a.x + b.x, a.y + b.y, a.z + b.z};
}

Vec3 operator-(const Vec3& a, const Vec3& b) {
    return Vec3{a.x - b.x, a.y - b.y, a.z - b.z};
}

Vec3 operator*(const Vec3& a, double s) {
    return Vec3{a.x * s, a.y * s, a.z * s};
}

Vec3& operator+=(Vec3& a, const Vec3& b) {
    a.x += b.x;
    a.y += b.y;
    a.z += b.z;
    return a;
}

double norm(const Vec3& v) {
    return std::sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
}

} // anonymous namespace
// ---------------------------------------------------------------

void PhysicsEngine::advance(Universe& universe, double dt) {
    integrateStep(universe.getBodies(), dt);
}

void PhysicsEngine::integrateStep(std::vector<Body>& bodies, double dt) {
    const double G = 6.67430e-11;
    size_t n = bodies.size();

    std::vector<Vec3> accelerations(n, Vec3{0.0, 0.0, 0.0});

    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            if (i == j) continue;
            Vec3 r = bodies[j].position - bodies[i].position;
            double dist = norm(r) + 1e-9; // avoid divide by zero
            accelerations[i] += r * (G * bodies[j].mass / (dist * dist * dist));
        }
    }

    for (size_t i = 0; i < n; ++i) {
        bodies[i].velocity += accelerations[i] * dt;
        bodies[i].position += bodies[i].velocity * dt;
    }
}
