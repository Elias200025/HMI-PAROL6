import time
from collections import deque

import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QApplication,
    QMenuBar, QAction, QDialog, QDialogButtonBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon

from robot.simulation import RobotSimulation
from robot.kinematics import get_kinematic_chain, get_euler_angles
from control.controller import RobotController, MODE_MANUAL, MODE_AUTO_PDF, MODE_AUTO_HOME
from trajectories.generator import (
    get_trajectory, build_manual_trajectory,
    interpolate_trajectory, sample_snapshot_waypoints,
)
from visualization.wireframe import capture_snapshot
from reports.pdf_report import generate_pdf_report
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel
from utils import resource_path

_PHYSICS_MS = 20
_RENDER_MS = 25


class RobotControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMI Industrial - PAROL 6")
        self.setWindowIcon(QIcon(resource_path("brazo-robotico.ico")))
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.showMaximized()

        self.sim = RobotSimulation()
        self.controller = RobotController(self.sim)

        # deque(maxlen=N) gives O(1) append+evict vs O(N) list.pop(0).
        self.path_x = deque(maxlen=100)
        self.path_y = deque(maxlen=100)
        self.path_z = deque(maxlen=100)
        self.snapshots = []
        self.auto_poses = []
        self.current_seq_idx = 0
        self.current_traj_name = ""
        self.current_T_matrix = np.eye(4)
        self.current_euler = np.zeros(3)
        self.current_chain = []
        self.current_q_img = None
        self.current_joints_state = [0.0] * 6

        # Batches slider commands.
        self._sliders_dirty = False
        # Pre-allocated buffer kept alive so QImage data pointer stays valid.
        self._rgb_buffer = None
        # Tick counter for skipping expensive table updates.
        self._tick = 0
        # Kinematics cache — skip recalculation when joints haven't moved.
        self._last_joints_kin = None
        self._kin_dirty = True

        self._build_ui()
        self._build_menu()
        self._connect_signals()

        # Start the two loops.
        self._schedule_physics()
        self._schedule_render()

    # ------------------------------------------------------------------ #
    # singleShot schedulers — guarantee Qt event-loop breathing room      #
    # ------------------------------------------------------------------ #

    def _schedule_physics(self):
        QTimer.singleShot(_PHYSICS_MS, self._physics_tick)

    def _schedule_render(self):
        QTimer.singleShot(_RENDER_MS, self._render_tick)

    # ------------------------------------------------------------------ #
    # UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _build_menu(self):
        menubar = QMenuBar(self)
        ayuda_menu = menubar.addMenu("Ayuda")
        accion_acerca = QAction("Acerca de...", self)
        accion_acerca.triggered.connect(self._show_about)
        ayuda_menu.addAction(accion_acerca)
        self.layout().setMenuBar(menubar)

    @staticmethod
    def _show_about():
        dlg = QDialog()
        dlg.setWindowTitle("Acerca de — HMI Industrial PAROL6")
        dlg.setWindowIcon(QIcon(resource_path("brazo-robotico.ico")))
        dlg.setFixedSize(520, 440)
        dlg.setStyleSheet("QDialog { background-color: #ffffff; font-family: 'Segoe UI'; }")
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint) # ESTA LÍNEA ELIMINA EL SÍMBOLO DE '?'

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 12)

        header = QLabel()
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            "background-color: #1a73e8; color: white; font-size: 15px; "
            "font-weight: bold; padding: 18px 10px;"
        )
        header.setText(
            "HMI Industrial — Robot PAROL6\n"
            "<span style='font-size:11px; font-weight:normal;'>"
            "Simulador Cinemático · 6 Grados de Libertad</span>"
        )
        header.setTextFormat(Qt.RichText)
        layout.addWidget(header)

        body = QLabel()
        body.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        body.setWordWrap(True)
        body.setStyleSheet("font-size: 12px; color: #3c4043; padding: 16px 24px 0 24px;")
        body.setText(
            "<b>Descripción:</b><br>"
            "Interfaz Hombre-Máquina para simulación y análisis cinemático del "
            "robot manipulador PAROL6 (6 GDL). Permite control manual articular, "
            "ejecución de trayectorias automáticas y generación de reportes PDF "
            "con matrices cinemáticas y visualización 3D.<br><br>"
            "<b>Tecnologías:</b> Python · PyQt5 · PyBullet · NumPy · Matplotlib<br><br>"
            "<b>Universidad:</b> Universidad Tecnológica de Pereira<br>"
            "<b>Facultad:</b> Ingenierías<br>"
            "<b>Grupo:</b> GIGSEEA<br><br>"
            "<b>Autores:</b><br>"
            "&nbsp;&nbsp;• Elias Escobar Pereira<br>"
            "&nbsp;&nbsp;• Kevin David Ortega Quiñones<br>"
            "&nbsp;&nbsp;• Daniela Buitrago Largo<br>"
            "&nbsp;&nbsp;• Mauricio Holguín Londoño<br>"
            "&nbsp;&nbsp;• German Andres Holguín Londoño<br><br>"
            "<b>Versión:</b> 1.0.0 &nbsp;|&nbsp; <b>Año:</b> 2026<br><br>"
            "<b>Manual de Usuario:</b> <a href='https://raw.githubusercontent.com/Elias200025/HMI-PAROL6/main/Manual_HMI_PAROL6.pdf'>Abrir Manual de Usuario</a>"
        )
        body.setOpenExternalLinks(True)
        layout.addWidget(body)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dlg.accept)
        buttons.setStyleSheet(
            "QPushButton { background-color: #1a73e8; color: white; "
            "padding: 6px 20px; border-radius: 4px; font-weight: bold; }"
        )
        layout.addWidget(buttons, alignment=Qt.AlignCenter)
        dlg.exec_()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        self.left_panel = LeftPanel(self.sim.joint_limits)

        center = QVBoxLayout()
        self.robot_label = QLabel()
        self.robot_label.setAlignment(Qt.AlignCenter)
        self.robot_label.setStyleSheet("border: 1px solid #dadce0; background: #1a1a2e;")
        self.robot_label.setMinimumSize(400, 400)
        center.addWidget(self.robot_label, 1)

        self.right_panel = RightPanel()

        layout.addWidget(self.left_panel)
        layout.addLayout(center)
        layout.addWidget(self.right_panel)

        self.setStyleSheet("""
            QWidget { background-color: white; color: #3c4043; font-family: 'Segoe UI'; }
            QSlider::groove:horizontal {
                border: 1px solid #dadce0; height: 4px; background: #f1f3f4;
            }
            QSlider::handle:horizontal {
                background: #1a73e8; width: 14px; height: 14px;
                margin: -5px 0; border-radius: 7px;
            }
            QProgressBar { background: #e8eaed; border-radius: 2px; }
        """)

    def _connect_signals(self):
        self.left_panel.slider_changed.connect(self._on_slider_changed)
        self.left_panel.go_pose_requested.connect(lambda: self._start_sequence(4))
        self.left_panel.home_requested.connect(lambda: self._start_sequence(5))
        self.left_panel.stop_requested.connect(self._stop_movement)
        self.right_panel.traj_requested.connect(self._start_sequence)

    # ------------------------------------------------------------------ #
    # Sequence control                                                     #
    # ------------------------------------------------------------------ #

    def _start_sequence(self, traj_id):
        self.snapshots.clear()
        current_joints = self.sim.get_joint_states()

        if traj_id in (1, 2, 3):
            name, poses = get_trajectory(traj_id, self.sim.joint_limits)
        elif traj_id == 4:
            target = self.left_panel.get_pose_values()
            name, poses = build_manual_trajectory(
                current_joints, target, self.sim.joint_limits
            )
        elif traj_id == 5:
            self.controller.set_target([0.0] * 6)
            self.controller.set_mode(MODE_AUTO_HOME)
            self._set_buttons_enabled(False)
            return

        full_traj = interpolate_trajectory(poses, steps_per_segment=25)
        self.auto_poses = sample_snapshot_waypoints(full_traj, n=3)
        self.current_traj_name = name
        self.current_seq_idx = 0
        self.controller.set_target(self.auto_poses[0])
        self.controller.set_mode(MODE_AUTO_PDF)
        self._set_buttons_enabled(False)

    def _stop_movement(self):
        self.controller.set_mode(MODE_MANUAL)
        self.left_panel.sync_sliders(self.sim.get_joint_states())
        self._set_buttons_enabled(True)  # re-enable HOME and trajectory buttons after stop

    def _set_buttons_enabled(self, enabled):
        self.left_panel.set_buttons_enabled(enabled)
        self.right_panel.set_buttons_enabled(enabled)

    # ------------------------------------------------------------------ #
    # Slider handler                                                       #
    # ------------------------------------------------------------------ #

    def _on_slider_changed(self):
        if self.controller.auto_mode == MODE_MANUAL:
            self._sliders_dirty = True

    # ------------------------------------------------------------------ #
    # Fast loop (~50 FPS) — physics, kinematics, tables, warning bars     #
    # ------------------------------------------------------------------ #

    def _physics_tick(self):
        self._tick += 1

        if self._sliders_dirty:
            for i, val in enumerate(self.left_panel.get_slider_values()):
                self.sim.set_joint_instant(i, val)
            self._sliders_dirty = False
            self._last_joints_kin = None  # force kinematics refresh after manual move

        current_joints = self.sim.get_joint_states()
        new_joints, arrived = self.controller.update(current_joints)
        if self.controller.auto_mode in (MODE_AUTO_PDF, MODE_AUTO_HOME):
            self.left_panel.sync_sliders(new_joints)

        if arrived:
            self._handle_arrival()

        self.sim.step()

        self.current_joints_state = self.sim.get_joint_states()

        # Kinematics cache: skip the 42 matrix ops when joints are stable.
        joints_arr = np.array(self.current_joints_state)
        if (self._last_joints_kin is None
                or not np.allclose(joints_arr, self._last_joints_kin, atol=1e-5)):
            self.current_chain = get_kinematic_chain(self.current_joints_state)
            self.current_T_matrix = self.current_chain[-1]
            self.current_euler = get_euler_angles(self.current_T_matrix[:3, :3])
            self._last_joints_kin = joints_arr
            self._kin_dirty = True

        # Update matrix tables at ~10 Hz (every 5 ticks) only when data changed.
        if self._tick % 5 == 0 and self._kin_dirty:
            self.right_panel.update_transform_matrix(self.current_T_matrix)
            self.right_panel.update_rotation_matrix(self.current_T_matrix[:3, :3])
            self._kin_dirty = False

        self._refresh_protection_bars()
        self._schedule_physics()

    def _take_hq_snapshot_image(self):
        rgb, w, h = self.sim.get_snapshot_image()
        buf = np.asarray(rgb, dtype=np.uint8).reshape(h, w, 4)[:, :, :3].copy()
        return QImage(buf.data, w, h, w * 3, QImage.Format_RGB888).copy()

    def _handle_arrival(self):
        current_mode = self.controller.auto_mode
        if current_mode == MODE_AUTO_PDF:
            hq_img = self._take_hq_snapshot_image()
            self.snapshots.append(
                capture_snapshot(
                    len(self.snapshots),
                    hq_img,
                    self.current_chain,
                    self.current_T_matrix,
                    self.current_euler,
                    self.current_joints_state,
                )
            )
            self.current_seq_idx += 1
            if self.current_seq_idx < 3:
                self.controller.set_target(self.auto_poses[self.current_seq_idx])
            else:
                self.controller.set_mode(MODE_MANUAL)
                generate_pdf_report(self.current_traj_name, self.snapshots)
                self.snapshots.clear()
                self._set_buttons_enabled(True)

        elif current_mode == MODE_AUTO_HOME:
            self.controller.set_mode(MODE_MANUAL)
            self._set_buttons_enabled(True)

    # ------------------------------------------------------------------ #
    # Slow loop (~20 FPS) — camera + matplotlib                           #
    # ------------------------------------------------------------------ #

    def _render_tick(self):
        self._refresh_camera()
        self._refresh_path()
        self._schedule_render()

    # ------------------------------------------------------------------ #
    # Refresh helpers                                                      #
    # ------------------------------------------------------------------ #

    def _refresh_camera(self):
        rgb, rw, rh = self.sim.get_camera_image()
        self._rgb_buffer = np.asarray(rgb, dtype=np.uint8).reshape(rh, rw, 4)[:, :, :3].copy()
        img = QImage(self._rgb_buffer.data, rw, rh, rw * 3, QImage.Format_RGB888)
        w, h = self.robot_label.width(), self.robot_label.height()
        # FastTransformation (nearest-neighbour) is ~5× faster than SmoothTransformation.
        self.robot_label.setPixmap(
            QPixmap.fromImage(img).scaled(w, h, Qt.KeepAspectRatio, Qt.FastTransformation)
        )
        self.current_q_img = img.copy()

    def _refresh_path(self):
        pos = self.current_T_matrix[:3, 3]
        self.path_x.append(float(pos[0]))
        self.path_y.append(float(pos[1]))
        self.path_z.append(float(pos[2]))
        self.right_panel.canvas.update_path(self.path_x, self.path_y, self.path_z, pos)

    def _refresh_protection_bars(self):
        warning_joint = None
        for i, curr in enumerate(self.current_joints_state):
            low, up = self.sim.joint_limits[i]
            if self.left_panel.update_protection_bar(i, curr, low, up):
                if warning_joint is None:
                    warning_joint = i
        self.left_panel.set_joint_warning(warning_joint)
