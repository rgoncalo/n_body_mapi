#pragma once
#include <vector>
#include <string>
#include <fstream>
#include "core/Body.hpp"

class OutputWriter {
public:
    OutputWriter(const std::string& filename);
    ~OutputWriter();

    void writeStep(const std::vector<Body>& bodies, double t);

private:
    std::ofstream outFile_;
    size_t stepCounter_;
};
