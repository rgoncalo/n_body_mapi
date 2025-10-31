###Step 1
Create a directory "build" at the same level as "src" (mkdir build)
###Step 2
module load cmake 3.22.0
Go to build (cd build) and run: cmake ..
###Step 3
Run make
###Step 4
Run the job.sh with sbatch (you can add as args the number of bodies, time_step size (seg), total time (seg) e.g ./simulate 50 3600 36000)
###Step 5
Copy simulation_output.txt to visualizer
