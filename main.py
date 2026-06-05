import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import RobotControl
from utils import resource_path

if __name__ == "__main__":
    # Required on Windows so the taskbar shows the app icon instead of the default Python icon.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("UTP.GIGSEEA.HMI_PAROL6.1")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("brazo-robotico.ico")))
    window = RobotControl()
    window.show()
    sys.exit(app.exec_())
