import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QSize, QTimer, pyqtSignal
from vispy import scene
from vispy.app import use_app
from vispy.scene.visuals import Markers
from vispy.visuals.transforms import STTransform

use_app('pyqt6')


class SimulationCanvas(QWidget):
    frame_advanced = pyqtSignal()  # Emit signal when frame changes

    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=False, bgcolor='#121212')
        self.canvas.create_native()
        self.canvas.native.setParent(self)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas.native)
        self.setLayout(layout)

        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.TurntableCamera(fov=45, distance=1.5e11, up='z')
        self.canvas.events.key_press.connect(self.on_key_press)

        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)
        self.axis.transform = STTransform(translate=(0, 0, 0))

        self.planet_visual = None
        self.body_color_map = {}  # name → color
        self.body_size = 10

        self.timer = QTimer()
        self.timer.timeout.connect(self._next_frame)

        self.frames = []
        self.current_frame = 0
        self.running = False
        self.frame_interval = 100
        self.skip_rate = 1

    # === Initialization ===

    def initialize_planet_visuals(self, names, positions, masses):
        """
        Initialize visual markers for all bodies with colors based on type/mass.

        Coloring scheme:
            Sun       → yellow
            Planets   → blue
            Moons     → copper
            Comets/asteroids → white
        """
        self.planet_visual = Markers(parent=self.view.scene)
        
        face_colors = []

        for name, mass in zip(names, masses):
            # Default: white (comet/asteroid)
            color = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)

            # Sun (most massive)
            if mass > 1e29:
                color = np.array([1.0, 1.0, 0.0, 1.0], dtype=np.float32)  # yellow
            # Planets (roughly 1e23 - 1e28 kg)
            elif 1e23 <= mass <= 1e28:
                color = np.array([0.2, 0.4, 1.0, 1.0], dtype=np.float32)  # blue
            # Moons (roughly 1e19 - 1e23 kg)
            elif 1e19 <= mass < 1e23:
                color = np.array([0.72, 0.45, 0.2, 1.0], dtype=np.float32)  # copper/brown
            # Comets/asteroids already white by default

            face_colors.append(color)

        self.planet_visual.set_data(
            pos=np.array(positions, dtype=np.float32),
            face_color=np.array(face_colors, dtype=np.float32),
            size=self.body_size
        )

    def load_frames(self, frame_list, masses):
        self.frames = frame_list
        if not frame_list:
            return

        positions = np.array(frame_list[0])
        n_bodies = positions.shape[0]

        if hasattr(self.parent(), "reader"):
            step_data = self.parent().reader.get_step_data(0)
            names = step_data.get("names", [f"b{i}" for i in range(n_bodies)])
        else:
            names = [f"b{i}" for i in range(n_bodies)]

        center = positions.mean(axis=0)
        spread = np.max(np.linalg.norm(positions - center, axis=1))
        self.view.camera.center = center
        self.view.camera.distance = spread * 3
        self.view.camera.up = 'z'

        axis_scale = spread * 0.2
        self.axis.transform = STTransform(scale=(axis_scale, axis_scale, axis_scale))

        self.initialize_planet_visuals(names, frame_list[0], masses)
        self.current_frame = 0
        self.canvas.update()

    # === Frame control ===

    def _next_frame(self):
        if not self.running or not self.frames:
            return

        self.current_frame += self.skip_rate
        if self.current_frame >= len(self.frames):
            self.current_frame = len(self.frames) - 1
            self.stop_animation()

        self.update_frame()
        self.frame_advanced.emit()

    def update_frame(self):
        if not self.frames:
            return

        # Clamp current_frame
        self.current_frame = min(self.current_frame, len(self.frames) - 1)
        positions = np.array(self.frames[self.current_frame], dtype=np.float32)

        # --- Get step data ---
        if hasattr(self.parent(), "reader"):
            step_data = self.parent().reader.get_step_data(self.current_frame)
            names = step_data.get("names", [f"b{i}" for i in range(len(positions))])
            masses = step_data.get("masses", [1.0 for _ in range(len(positions))])
        else:
            names = [f"b{i}" for i in range(len(positions))]
            masses = [1.0 for _ in range(len(positions))]

        # --- Initialize body colors once ---
        if not self.body_color_map:
            for name, mass in zip(names, masses):
                if mass > 1e29:
                    color = np.array([1.0, 1.0, 0.0, 1.0])  # Sun: yellow
                elif 1e23 <= mass <= 1e28:
                    color = np.array([0.2, 0.4, 1.0, 1.0])  # Planets: blue
                elif 1e19 <= mass < 1e23:
                    color = np.array([0.72, 0.45, 0.2, 1.0])  # Moons: copper
                else:
                    color = np.array([1.0, 1.0, 1.0, 1.0])  # Comets/asteroids: white
                self.body_color_map[name] = color

        # --- Set colors and positions ---
        face_colors = np.array([self.body_color_map[name] for name in names], dtype=np.float32)
        self.planet_visual.set_data(pos=positions, face_color=face_colors, size=self.body_size)

        # --- Follow selected body if active ---
        if hasattr(self.parent(), "selected_index") and self.parent().selected_index is not None:
            follow_index = self.parent().selected_index
            if 0 <= follow_index < len(positions):
                target_pos = positions[follow_index]
                self.view.camera.center = target_pos
                self.axis.transform.translate = target_pos

        self.canvas.update()


    # === Camera movement ===

    def on_key_press(self, event):
        camera = self.view.camera
        step = camera.distance * 0.1
        transform = camera.transform.matrix
        forward = np.array([transform[0, 2], transform[1, 2], transform[2, 2]])
        right = np.array([transform[0, 0], transform[1, 0], transform[2, 0]])
        up = np.array([transform[0, 1], transform[1, 1], transform[2, 1]])

        if event.key.name == 'W':
            camera.center -= forward * step
        elif event.key.name == 'S':
            camera.center += forward * step
        elif event.key.name == 'A':
            camera.center -= right * step
        elif event.key.name == 'D':
            camera.center += right * step
        elif event.key.name == 'Q':
            camera.center -= up * step
        elif event.key.name == 'E':
            camera.center += up * step

        self.canvas.update()

    # === Animation control ===

    def start_animation(self):
        if not self.frames:
            return
        self.running = True
        self.timer.start(self.frame_interval)

    def stop_animation(self):
        self.running = False
        self.timer.stop()

    def sizeHint(self):
        return QSize(800, 600)
