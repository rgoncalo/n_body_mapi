#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --exclusive
#SBATCH --time=00:05:00
#SBATCH --partition=day

# Consider using SBATCH --exclusive option outside of the class
# It ensures that no other user pollutes your measurements

module load gcc/11.2.0
module load cmake/3.22.0

echo "Compiling..."
cd build 
cmake ..
make

echo "Running..."
./simulate 30 3600 36000

echo "Finished"