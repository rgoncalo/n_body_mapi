#include "outputWritter.hpp"
#include <iostream>
#include <iomanip>

OutputWriter::OutputWriter(const std::string& filename)
    : outFile_(filename), stepCounter_(0)
{
    if (!outFile_.is_open()) {
        std::cerr << "Error opening file: " << filename << "\n";
    } else {
        std::cout << "Created output TXT file: " << filename << "\n";
    }
}

OutputWriter::~OutputWriter() {
    if (outFile_.is_open()) outFile_.close();
}

void OutputWriter::writeStep(const std::vector<Body>& bodies, double t) {
    if (!outFile_.is_open()) return;

    outFile_ << "# Step " << stepCounter_ << ", Time: " << t << " s\n";
    outFile_ << "Name Mass Px Py Pz Vx Vy Vz\n";

    for (const auto& b : bodies) {
        outFile_ << std::setw(10) << b.name << " "
                 << std::scientific << std::setprecision(6)
                 << b.mass << " "
                 << b.position.x << " " << b.position.y << " " << b.position.z << " "
                 << b.velocity.x << " " << b.velocity.y << " " << b.velocity.z << "\n";
    }

    outFile_ << "\n";
    ++stepCounter_;
}
