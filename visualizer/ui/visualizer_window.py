from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QListWidget, QSlider, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime, timedelta
import numpy as np
from render.simulation_canvas import SimulationCanvas
from data.data_loader import TXTSimulationReader


class VisualizerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universe Visualizer")

        # --- Load simulation data ---
        self.reader = TXTSimulationReader("simulation_output.txt")

        self.frames = [self.reader.get_step_data(i)["positions"]
                       for i in range(self.reader.get_num_steps())]
        step0 = self.reader.get_step_data(0)
        self.names = step0["names"]
        self.masses = step0["masses"]
        self.velocities = step0["velocities"]

        # --- Canvas setup ---
        self.canvas = SimulationCanvas()
        self.canvas.setParent(self)
        self.canvas.load_frames(self.frames, self.masses)
        self.canvas.frame_interval = 30

        # --- Buttons ---
        self.play_button = QPushButton("▶ Play")
        self.stop_button = QPushButton("⏹ Stop")
        self.restart_button = QPushButton("🔄 Restart")
        self.ff_button = QPushButton("⏩")
        self.rw_button = QPushButton("⏪")
        self.reset_speed_button = QPushButton("🔁 Reset Speed")

        self.play_button.clicked.connect(self.play_animation)
        self.stop_button.clicked.connect(self.stop_animation)
        self.restart_button.clicked.connect(self.restart_simulation)
        self.ff_button.pressed.connect(self.increase_skip_rate)
        self.rw_button.pressed.connect(self.decrease_skip_rate)
        self.ff_button.released.connect(self.stop_skip_adjust)
        self.rw_button.released.connect(self.stop_skip_adjust)
        self.reset_speed_button.clicked.connect(self.reset_speed)

        # --- Speed control ---
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(500)
        self.speed_slider.setValue(self.canvas.frame_interval)
        self.speed_slider.valueChanged.connect(self.adjust_speed)
        self.speed_value_label = QLabel(f"{self.canvas.frame_interval} ms/frame")

        # --- Date label ---
        self.date_label = QLabel()
        self.update_date_label()

        # --- Body list and info ---
        self.body_list = QListWidget()
        self.body_list.currentRowChanged.connect(self.on_body_selected)
        self.body_list.itemDoubleClicked.connect(self.on_body_double_clicked)
        self.body_info = QLabel("Select a body to view details")
        self.body_info.setWordWrap(True)
        self.body_info.setVisible(False)

        self.selected_index = None
        self.update_body_list(self.names)

        # --- Layout setup ---
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.ff_button)
        button_layout.addWidget(self.reset_speed_button)
        button_layout.addWidget(self.rw_button)

        speed_layout = QVBoxLayout()
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_value_label)
        button_layout.addLayout(speed_layout)
        button_layout.addWidget(self.date_label)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.body_list, stretch=1)
        content_layout.addWidget(self.canvas, stretch=4)
        content_layout.addWidget(self.body_info, stretch=2)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        self.resize(1200, 700)

        # --- Skip timer ---
        self.skip_adjust_timer = QTimer()
        self.skip_adjust_timer.timeout.connect(self.adjust_skip_rate)
        self.skip_direction = None

        # Sync animation updates to UI
        self.canvas.frame_advanced.connect(self.update_on_frame_advance)

    # === UI Helpers ===

    def update_on_frame_advance(self):
        self.update_date_label()
        self.update_body_info()

    def update_date_label(self):
        step = self.canvas.current_frame
        self.date_label.setText(f"Step: {step}")


    def update_body_list(self, names):
        self.body_list.clear()
        for n in names:
            self.body_list.addItem(n.strip())

    def on_body_selected(self, index):
        if index < 0 or index >= len(self.names):
            self.body_info.setVisible(False)
            self.selected_index = None
            return
        self.selected_index = index
        self.update_body_info(index)
        self.body_info.setVisible(True)

    def update_body_info(self, index=None):
        if index is None:
            if self.selected_index is None:
                return
            index = self.selected_index
        if index < 0 or index >= len(self.names):
            return

        frame_idx = min(self.canvas.current_frame, self.reader.get_num_steps() - 1)
        step_data = self.reader.get_step_data(frame_idx)

        name = step_data["names"][index].strip()
        mass = step_data["masses"][index]
        vel = step_data["velocities"][index]
        speed = np.linalg.norm(vel)

        self.body_info.setText(
            f"<b>Name:</b> {name}<br>"
            f"<b>Mass:</b> {mass:.3e} kg<br>"
            f"<b>Velocity:</b> ({vel[0]:.2e}, {vel[1]:.2e}, {vel[2]:.2e}) m/s<br>"
            f"<b>Speed:</b> {speed:.2e} m/s"
        )

    def on_body_double_clicked(self, item):
        index = self.body_list.currentRow()
        if 0 <= index < len(self.frames[0]):
            pos = self.frames[self.canvas.current_frame][index]
            self.canvas.view.camera.center = pos

    # === Animation controls ===

    def play_animation(self):
        self.canvas.start_animation()

    def stop_animation(self):
        self.canvas.stop_animation()

    def restart_simulation(self):
        self.canvas.current_frame = 0
        self.canvas.update_frame()
        self.update_date_label()

    def adjust_speed(self, value):
        self.canvas.frame_interval = value
        self.speed_value_label.setText(f"{value} ms/frame")
        self.canvas.timer.setInterval(value)

    def reset_speed(self):
        self.canvas.frame_interval = 30
        self.speed_slider.setValue(30)
        self.speed_value_label.setText("30 ms/frame")
        self.canvas.timer.setInterval(30)

    # === Frame skipping controls ===

    def increase_skip_rate(self):
        self.skip_direction = "forward"
        self.skip_adjust_timer.start(100)

    def decrease_skip_rate(self):
        self.skip_direction = "backward"
        self.skip_adjust_timer.start(100)

    def stop_skip_adjust(self):
        self.skip_adjust_timer.stop()
        self.skip_direction = None

    def adjust_skip_rate(self):
        if self.skip_direction == "forward":
            self.canvas.current_frame = min(self.canvas.current_frame + 5, len(self.frames) - 1)
        elif self.skip_direction == "backward":
            self.canvas.current_frame = max(self.canvas.current_frame - 5, 0)
        self.canvas.update_frame()
        self.update_date_label()
