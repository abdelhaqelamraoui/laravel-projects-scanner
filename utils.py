import os
import platform
import subprocess


def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", path])
    else:  # Linux and others
        subprocess.Popen(["xdg-open", path])
