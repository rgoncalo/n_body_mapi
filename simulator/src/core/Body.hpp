#pragma once
#include <array>
#include <string>
#include <iostream>

struct Vec3 {
    double x{0};
    double y{0};
    double z{0};

    Vec3() = default;
    Vec3(double x_, double y_, double z_) : x(x_), y(y_), z(z_) {}
};

class Body {
public:
    std::string name;
    double mass;
    Vec3 position;
    Vec3 velocity;

    Body(const std::string& n, double m, const Vec3& pos, const Vec3& vel)
        : name(n), mass(m), position(pos), velocity(vel) {}

    Body() : name(""), mass(0), position(), velocity() {}

    void print() const {
        std::cout << "Name: " << name << "\n";
        std::cout << "Mass: " << mass << "\n";
        std::cout << "Position: (" << position.x << ", " << position.y << ", " << position.z << ")\n";
        std::cout << "Velocity: (" << velocity.x << ", " << velocity.y << ", " << velocity.z << ")\n";
    }
};
