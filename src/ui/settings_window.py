from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSlider, QComboBox, QPushButton, QFileDialog, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt
import subprocess
import os
import signal
from shutil import which
from pathlib import Path

class SettingsWindow(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.apply_theme()
        self.setup_ui()

    def apply_theme(self):
        if self.config.theme == "dark":
            self.setStyleSheet("""
                QDialog { background-color: #1e1e2e; color: #cdd6f4; }
                QLabel { color: #cdd6f4; }
                QLineEdit { background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px; color: #cdd6f4; }
                QComboBox { background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px 10px; color: #cdd6f4; }
                QComboBox::drop-down { border: none; }
                QPushButton { background-color: #313244; border: none; border-radius: 5px; color: #cdd6f4; padding: 8px 12px; }
                QPushButton:hover { background-color: #45475a; }
                QCheckBox { color: #cdd6f4; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #eff1f5; color: #4c4f69; }
                QLabel { color: #4c4f69; }
                QLineEdit { background-color: #e6e9ef; border: 1px solid #ccd0da; border-radius: 5px; padding: 5px; color: #4c4f69; }
                QComboBox { background-color: #e6e9ef; border: 1px solid #ccd0da; border-radius: 5px; padding: 5px 10px; color: #4c4f69; }
                QComboBox::drop-down { border: none; }
                QPushButton { background-color: #ccd0da; border: none; border-radius: 5px; color: #4c4f69; padding: 8px 12px; }
                QPushButton:hover { background-color: #bcc0cc; }
                QCheckBox { color: #4c4f69; }
            """)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Hyprctl Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("hyprctl Path:"))
        self.path_edit = QLineEdit(self.config.hyprctl_path)
        self.path_edit.setMinimumWidth(250)
        path_layout.addWidget(self.path_edit)

        reset_btn = QPushButton("↺")
        reset_btn.setToolTip("Reset to default hyprctl path")
        reset_btn.setFixedWidth(30)
        reset_btn.clicked.connect(self.reset_path)
        path_layout.addWidget(reset_btn)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.config.theme)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Transparency
        layout.addWidget(QLabel("Transparency (0=Opaque, 100=Transparent):"))
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 100)
        current_transparency = int((1.0 - self.config.transparency) * 100)
        self.transparency_slider.setValue(current_transparency)
        layout.addWidget(self.transparency_slider)

        # Tracking Feature
        self.tracking_check = QCheckBox("Enable Window Activity Tracking (Required for Garbage Collect)")
        self.tracking_check.setChecked(self.config.tracking_enabled)
        self.tracking_check.toggled.connect(self.toggle_tracking)
        layout.addWidget(self.tracking_check)

        # Buttons
        btns_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns_layout.addStretch()
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(cancel_btn)
        layout.addLayout(btns_layout)

    def toggle_tracking(self, checked):
        if checked:
            reply = QMessageBox.question(self, "Enable Tracking Service",
                                        "Enabling this feature will start a background service to track window focus history.\n\n"
                                        "This is required for the 'Collect Garbage' functionality.\n\n"
                                        "Do you want to proceed?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.enable_tracking_service()
            else:
                self.tracking_check.blockSignals(True)
                self.tracking_check.setChecked(False)
                self.tracking_check.blockSignals(False)
        else:
            reply = QMessageBox.question(self, "Disable Tracking Service",
                                        "Disabling this feature will stop the background service and remove it from autostart.\n\n"
                                        "The 'Collect Garbage' button will be hidden.\n\n"
                                        "Do you want to proceed?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.disable_tracking_service()
            else:
                self.tracking_check.blockSignals(True)
                self.tracking_check.setChecked(True)
                self.tracking_check.blockSignals(False)

    def enable_tracking_service(self):
        # 1. Create autostart file
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = autostart_dir / "hypr-ws-manager-tracker.desktop"
        
        project_dir = Path(__file__).parent.parent.parent.absolute()
        tracker_script = project_dir / "src" / "tracker.py"
        
        # Determine python path
        venv_python = project_dir / ".venv" / "bin" / "python"
        cmd = f"{venv_python} {tracker_script}"
        
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Type=Application
Exec={cmd}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Hyprland Workspace Manager Tracker
Comment=Tracks window activity for garbage collection
""")
        
        # 2. Start process
        subprocess.Popen(cmd.split(), start_new_session=True)
        self.config.tracking_enabled = True

    def disable_tracking_service(self):
        # 1. Remove autostart file
        desktop_file = Path.home() / ".config" / "autostart" / "hypr-ws-manager-tracker.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
            
        # 2. Kill process
        try:
            # Simple way to kill the tracker
            subprocess.run(["pkill", "-f", "src/tracker.py"], check=False)
        except Exception:
            pass
            
        self.config.tracking_enabled = False

    def reset_path(self):
        default_path = which("hyprctl")
        if default_path:
            self.path_edit.setText(default_path)
        else:
            self.path_edit.setText("hyprctl")

    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select hyprctl binary")
        if path:
            self.path_edit.setText(path)

    def save_settings(self):
        new_path = self.path_edit.text().strip()
        
        # Validation
        valid = False
        error_msg = ""
        
        if not new_path:
            error_msg = "Path cannot be empty."
        elif not os.path.exists(new_path) and not which(new_path):
            error_msg = f"File not found: {new_path}"
        else:
            try:
                # Try to run hyprctl --version to see if it's actually hyprctl
                subprocess.run([new_path, "version"], capture_output=True, check=True, timeout=2)
                valid = True
            except (subprocess.CalledProcessError, FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
                error_msg = f"The file at '{new_path}' is not a valid hyprctl binary or is not executable."

        if not valid:
            QMessageBox.critical(self, "Invalid Path", error_msg)
            return

        # Convert slider transparency back to opacity
        opacity = 1.0 - (self.transparency_slider.value() / 100.0)
        
        self.config.hyprctl_path = new_path
        self.config.theme = self.theme_combo.currentText()
        self.config.transparency = opacity
        self.accept()
