from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSlider, QComboBox, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
import subprocess
import os
from shutil import which

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
        # If config.transparency is actually opacity (0.1 to 1.0),
        # then opacity 1.0 (opaque) = transparency 0
        # and opacity 0.1 = transparency 90
        current_transparency = int((1.0 - self.config.transparency) * 100)
        self.transparency_slider.setValue(current_transparency)
        layout.addWidget(self.transparency_slider)

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
