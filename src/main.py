import sys
import os
import subprocess
from shutil import which
from PySide6.QtWidgets import QApplication
from src.config import Config
from src.hypr_manager import HyprManager
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("hypr-ws-manager")
    app.setDesktopFileName("hypr-ws-manager")
    
    config = Config()
    
    # Startup validation of hyprctl path
    hyprctl_path = config.hyprctl_path
    if not (os.path.exists(hyprctl_path) or which(hyprctl_path)):
        print(f"Warning: Saved hyprctl path '{hyprctl_path}' is invalid. Falling back to default.")
        hyprctl_path = "hyprctl"
    
    hypr = HyprManager(hyprctl_path)
    
    window = MainWindow(config, hypr)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
