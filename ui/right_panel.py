from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal
from visualization.canvas3d import MplCanvas


class RightPanel(QFrame):
    traj_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(420)
        self.setStyleSheet("background-color: #ffffff; border-left: 1px solid #dadce0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self._build_trajectory_buttons(layout)
        self._build_matrix_section(layout)
        self._build_canvas(layout)

    # ------------------------------------------------------------------ #
    # Build helpers                                                        #
    # ------------------------------------------------------------------ #

    def _build_trajectory_buttons(self, layout):
        frame = QFrame()
        frame.setStyleSheet(
            "background-color: #e8f0fe; border: 1px solid #c6dafc; border-radius: 6px;"
        )
        vbox = QVBoxLayout(frame)

        lbl = QLabel("TRAYECTORIAS AUTOMÁTICAS (3 POSES)")
        lbl.setStyleSheet("font-weight: bold; color: #1a73e8; font-size: 12px;")
        vbox.addWidget(lbl)

        self.traj_buttons = []
        traj_labels = [
            "🚀 Ejecutar Trayectoria 1 (Pick & Place)",
            "🚀 Ejecutar Trayectoria 2 (Inspección)",
            "🚀 Ejecutar Trayectoria 3 (Esquivar)",
        ]
        for traj_id, label in enumerate(traj_labels, start=1):
            btn = QPushButton(label)
            btn.setStyleSheet(
                "background-color: white; color: #1a73e8; "
                "border: 1px solid #1a73e8; padding: 8px; font-weight: bold;"
            )
            btn.clicked.connect(lambda checked, t=traj_id: self.traj_requested.emit(t))
            vbox.addWidget(btn)
            self.traj_buttons.append(btn)

        layout.addWidget(frame)

    def _build_matrix_section(self, layout):
        lbl_mat = QLabel("CINEMÁTICA DIRECTA: MATRIZ DE TRANSFORMACIÓN (T) 4x4 [m]")
        lbl_mat.setStyleSheet("font-weight: bold; color: #202124; font-size: 11px;")
        layout.addWidget(lbl_mat)

        self.matrix_table = self._create_table(
            4, 4, height=110, extra_style="background-color: #f8f9fa;"
        )
        layout.addWidget(self.matrix_table)

        lbl_rot = QLabel("MATRIZ DE ROTACIÓN Y EULER Z-Y-X [rad]")
        lbl_rot.setStyleSheet(
            "font-weight: bold; color: #d93025; font-size: 11px; margin-top: 5px;"
        )
        layout.addWidget(lbl_rot)

        self.rot_table = self._create_table(
            3, 3, height=80,
            extra_style="font-weight: bold; color: #d93025; background-color: #fce8e6;",
        )
        layout.addWidget(self.rot_table)

        lbl_path = QLabel("RECONSTRUCCIÓN MATRICIAL 3D")
        lbl_path.setStyleSheet("font-weight: bold; color: #202124; margin-top: 5px;")
        layout.addWidget(lbl_path)

    def _build_canvas(self, layout):
        self.canvas = MplCanvas(self)
        layout.addWidget(self.canvas, stretch=1)

    @staticmethod
    def _create_table(rows, cols, height, extra_style=""):
        table = QTableWidget(rows, cols)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setFixedHeight(height)
        table.setStyleSheet(f"font-family: 'Consolas'; font-size: 12px; {extra_style}")
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem("0.000")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                table.setItem(i, j, item)
        return table

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def update_transform_matrix(self, T_matrix):
        for row in range(4):
            for col in range(4):
                val = T_matrix[row, col]
                text = f"{val:.4f}" if col == 3 else f"{val:.3f}"
                item = self.matrix_table.item(row, col)
                if item.text() != text:
                    item.setText(text)

    def update_rotation_matrix(self, R_mat):
        for row in range(3):
            for col in range(3):
                text = f"{R_mat[row, col]:.3f}"
                item = self.rot_table.item(row, col)
                if item.text() != text:
                    item.setText(text)

    def set_buttons_enabled(self, enabled):
        for btn in self.traj_buttons:
            btn.setEnabled(enabled)
