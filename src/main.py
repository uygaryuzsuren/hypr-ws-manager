import sys
import os
import subprocess
import signal
import atexit
from shutil import which
from PySide6.QtWidgets import QApplication
from src.config import Config; import os
from src.hypr_manager import HyprManager
from src.ui.main_window import MainWindow

PID_FILE = f"/tmp/{Config.APP_NAME}.pid"

def cleanup_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def check_single_instance():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            try:
                pid = int(f.read().strip())
                # Check if process exists and is actually ours (simple check)
                if os.path.exists(f"/proc/{pid}"):
                    print(f"Stopping existing instance (PID: {pid})")
                    os.kill(pid, signal.SIGTERM)
                    # Give it a moment to exit
                    import time
                    time.sleep(0.5)
            except (ValueError, ProcessLookupError):
                pass
        cleanup_pid()
    
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    atexit.register(cleanup_pid)

def main():
    check_single_instance()
    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setDesktopFileName(Config.APP_NAME)
    
    config = Config()
    
    # Startup validation of hyprctl path
    hyprctl_path = config.hyprctl_path
    if not (os.path.exists(hyprctl_path) or which(hyprctl_path)):
        print(f"Warning: Saved hyprctl path '{hyprctl_path}' is invalid. Falling back to default.")
        hyprctl_path = "hyprctl"
    
    hypr = HyprManager(hyprctl_path)
    
    # Capture the active window before our app takes focus
    active_win = hypr.get_active_window()
    initial_window_addr = active_win['address'] if active_win else None
    
    window = MainWindow(config, hypr)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
