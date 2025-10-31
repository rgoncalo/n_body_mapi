class TXTSimulationReader:
    """
    Reads simulation output in plain text format produced by OutputWriter.
    Expected format per timestep:

    # Step N, Time: t s
    Name Mass Px Py Pz Vx Vy Vz
    Sun 1.989e30 0 0 0 0 0 0
    Earth 5.972e24 1.496e11 0 0 0 29780 0
    ...
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.steps = []  # list of dictionaries with timestep data
        self._parse_file()

    def _parse_file(self):
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        current_step = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("# Step"):
                # Start a new step
                if current_step is not None:
                    self.steps.append(current_step)
                # Extract time
                parts = line.split("Time:")
                time = float(parts[1].split()[0])
                current_step = {"time": time, "names": [], "masses": [], "positions": [], "velocities": []}
                continue

            if line.startswith("Name") or line.startswith("#"):
                # Header line or comment
                continue

            # Parse body data
            tokens = line.split()
            name = tokens[0]
            mass = float(tokens[1])
            px, py, pz = map(float, tokens[2:5])
            vx, vy, vz = map(float, tokens[5:8])

            current_step["names"].append(name)
            current_step["masses"].append(mass)
            current_step["positions"].append([px, py, pz])
            current_step["velocities"].append([vx, vy, vz])

        # Add last step
        if current_step is not None:
            self.steps.append(current_step)

    def get_num_steps(self):
        return len(self.steps)

    def get_step_data(self, i):
        return self.steps[i]
