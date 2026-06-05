from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QPushButton, QProgressBar, QDoubleSpinBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from utils import resource_path


class LeftPanel(QFrame):
    slider_changed = pyqtSignal()
    go_pose_requested = pyqtSignal()
    home_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, joint_limits, parent=None):
        super().__init__(parent)
        self.joint_limits = joint_limits
        self.setFixedWidth(360)
        self.setStyleSheet("background-color: #f1f3f4; border-right: 1px solid #dadce0;")

        layout = QVBoxLayout(self)
        self._build_sliders(layout)
        self._build_warning_label(layout)
        self._build_pose_inputs(layout)
        layout.addStretch()
        self._build_logos(layout)
        layout.addStretch()
        self._build_action_buttons(layout)

    # ------------------------------------------------------------------ #
    # Build helpers                                                        #
    # ------------------------------------------------------------------ #

    def _build_sliders(self, layout):
        title = QLabel("CONTROL MANUAL DIRECTO [rad]")
        title.setStyleSheet("font-weight: bold; color: #202124; font-size: 13px; margin-top: 5px;")
        layout.addWidget(title)

        self.sliders, self.protection_bars, self.val_labels = [], [], []
        self._bar_colors = [None] * 6  # cached colors — skip setStyleSheet when unchanged
        for i in range(6):
            header = QHBoxLayout()
            lbl = QLabel(f"Motor {i + 1} [rad]")
            lbl.setStyleSheet("font-weight: bold; font-size: 11px;")
            val_lbl = QLabel("0.00")
            val_lbl.setStyleSheet(
                "color: #1a73e8; font-family: 'Consolas'; font-weight: bold;"
            )
            header.addWidget(lbl)
            header.addStretch()
            header.addWidget(val_lbl)

            low, up = self.joint_limits[i]
            slider = QSlider(Qt.Horizontal)
            slider.setRange(int(low * 100), int(up * 100))
            slider.setValue(0)
            slider.valueChanged.connect(
                lambda v, idx=i: self._on_slider_value_changed(idx, v)
            )

            bar = QProgressBar()
            bar.setFixedHeight(4)
            bar.setTextVisible(False)

            self.sliders.append(slider)
            self.protection_bars.append(bar)
            self.val_labels.append(val_lbl)
            layout.addLayout(header)
            layout.addWidget(slider)
            layout.addWidget(bar)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

    def _build_warning_label(self, layout):
        self.warning_label = QLabel()
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet(
            "background-color: #d93025; color: white; font-weight: bold; "
            "font-size: 11px; padding: 5px 8px; border-radius: 3px;"
        )
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)

    def _build_pose_inputs(self, layout):
        title = QLabel("IR A POSE MANUAL (3 PASOS + PDF)")
        title.setStyleSheet("font-weight: bold; color: #202124; font-size: 13px;")
        layout.addWidget(title)

        grid = QGridLayout()
        self.pose_inputs = []
        for i in range(6):
            low, up = self.joint_limits[i]
            spin = QDoubleSpinBox()
            spin.setRange(low, up)
            spin.setSingleStep(0.1)
            spin.setValue(0.0)
            spin.setStyleSheet("padding: 2px; border: 1px solid #ccc; background: white;")
            self.pose_inputs.append(spin)
            lbl = QLabel(f"L{i + 1} [rad]:\n[{low:.1f}, {up:.1f}]")
            lbl.setStyleSheet("font-size: 10px; color: #5f6368;")
            grid.addWidget(lbl, i // 2, (i % 2) * 2)
            grid.addWidget(spin, i // 2, (i % 2) * 2 + 1)
        layout.addLayout(grid)

        btn = QPushButton("▶ VIAJAR A ESTA POSE (PDF)")
        btn.setStyleSheet(
            "background-color: #1a73e8; color: white; padding: 6px; font-weight: bold;"
        )
        btn.clicked.connect(self.go_pose_requested)
        layout.addWidget(btn)

    def _build_logos(self, layout):
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(frame)

        hbox = QHBoxLayout()
        lbl_utp = QLabel()
        lbl_utp.setAlignment(Qt.AlignCenter)
        lbl_utp.setPixmap(
            QPixmap(resource_path("Logo_UTP.png")).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        lbl_grupo = QLabel()
        lbl_grupo.setAlignment(Qt.AlignCenter)
        lbl_grupo.setPixmap(
            QPixmap(resource_path("gseea.png")).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        hbox.addWidget(lbl_utp)
        hbox.addWidget(lbl_grupo)
        vbox.addLayout(hbox)

        lbl_autores = QLabel(
            "<b>Universidad Tecnológica de Pereira</b><br><br>"
            "<b>Autores:</b><br>"
            "Elias Escobar Pereira<br>"
            "Kevin David Ortega Quiñones<br>"
            "Daniela Buitrago Largo<br>"
            "Mauricio Holguín Londoño<br>"
            "German Andres Holguín Londoño"
        )
        lbl_autores.setAlignment(Qt.AlignCenter)
        lbl_autores.setStyleSheet("font-size: 12px; color: #3c4043;")
        vbox.addWidget(lbl_autores)
        layout.addWidget(frame)

    def _build_action_buttons(self, layout):
        self.btn_home = QPushButton("🏠 VOLVER A POSE INICIAL (HOME)")
        self.btn_home.setStyleSheet(
            "background-color: #f9ab00; color: #202124; padding: 10px; "
            "font-weight: bold; border-radius: 4px; margin-bottom: 5px;"
        )
        self.btn_home.clicked.connect(self.home_requested)
        layout.addWidget(self.btn_home)

        btn_stop = QPushButton("🛑 DETENER MOVIMIENTO")
        btn_stop.setStyleSheet(
            "background-color: #d93025; color: white; padding: 10px; "
            "font-weight: bold; border-radius: 4px;"
        )
        btn_stop.clicked.connect(self.stop_requested)
        layout.addWidget(btn_stop)

    # ------------------------------------------------------------------ #
    # Internal slot                                                        #
    # ------------------------------------------------------------------ #

    def _on_slider_value_changed(self, idx, raw_value):
        self.val_labels[idx].setText(f"{raw_value / 100.0:.2f}")
        self.slider_changed.emit()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def get_slider_values(self):
        return [s.value() / 100.0 for s in self.sliders]

    def get_pose_values(self):
        return [spin.value() for spin in self.pose_inputs]

    def sync_sliders(self, joint_values):
        for i, val in enumerate(joint_values):
            self.sliders[i].blockSignals(True)
            self.sliders[i].setValue(int(val * 100))
            self.val_labels[i].setText(f"{val:.2f}")
            self.sliders[i].blockSignals(False)

    def update_protection_bar(self, idx, curr, low, up):
        """Update bar color. Returns True if joint is in critical zone (red)."""
        if up <= low:
            return False
        pct = int(((curr - low) / (up - low)) * 100)
        pct = max(0, min(100, pct))
        self.protection_bars[idx].setValue(pct)
        critical = pct < 5 or pct > 95
        if critical:
            color = "#d93025"
        elif pct < 15 or pct > 85:
            color = "#f9ab00"
        else:
            color = "#34a853"
        # setStyleSheet triggers a full Qt style recompute — skip when color unchanged.
        if color != self._bar_colors[idx]:
            self._bar_colors[idx] = color
            self.protection_bars[idx].setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {color}; }}"
            )
        return critical

    def set_joint_warning(self, joint_idx):
        """Show warning label for joint_idx (0-based), or hide if None."""
        if joint_idx is None:
            self.warning_label.setVisible(False)
        else:
            self.warning_label.setText(
                f"⚠  MOTOR {joint_idx + 1}: CERCA DEL LÍMITE MECÁNICO"
            )
            self.warning_label.setVisible(True)

    def set_buttons_enabled(self, enabled):
        self.btn_home.setEnabled(enabled)
