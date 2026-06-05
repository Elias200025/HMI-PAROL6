import os
import sys


def resource_path(relative_path):
    """Return absolute path to a bundled resource; works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)
