import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy

# Matplotlib 3D redraws are expensive (~10-30 ms each).  Cap at ~5 Hz so the
# Qt event loop never spends more than 30 ms per render cycle on this alone.
_MIN_DRAW_INTERVAL = 0.20  # seconds between actual redraws


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=3, dpi=80):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.axes = self.fig.add_subplot(111, projection="3d")
        self.axes.set_box_aspect(None, zoom=0.85)
        self.fig.patch.set_facecolor("#f8f9fa")
        self.axes.set_facecolor("#ffffff")
        self.axes.set_xlim(-0.5, 0.5)
        self.axes.set_ylim(-0.5, 0.5)
        self.axes.set_zlim(0, 0.7)
        self.line, = self.axes.plot([], [], [], color="#1a73e8", lw=1.5, label="Trayectoria")
        self.scatter = self.axes.scatter([], [], [], color="#34a853", s=70,
                                         marker="o", zorder=10, label="J6/TCP")
        self.axes.legend(fontsize=7, loc="upper right")
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.setMinimumHeight(200)

        self._last_pos = np.array([np.inf, np.inf, np.inf])
        self._last_path_len = 0
        self._last_draw_time = 0.0

    def update_path(self, path_x, path_y, path_z, pos):
        pos = np.asarray(pos)
        path_len = len(path_x)

        # Skip if position and path length haven't changed.
        if np.allclose(pos, self._last_pos, atol=1e-4) and path_len == self._last_path_len:
            return

        self._last_pos = pos.copy()
        self._last_path_len = path_len

        # Time-based throttle: matplotlib 3D draws are costly — enforce minimum interval.
        now = time.monotonic()
        if now - self._last_draw_time < _MIN_DRAW_INTERVAL:
            return
        self._last_draw_time = now

        self.line.set_data(np.array(path_x), np.array(path_y))
        self.line.set_3d_properties(np.array(path_z))
        self.scatter._offsets3d = ([pos[0]], [pos[1]], [pos[2]])
        self.draw_idle()
