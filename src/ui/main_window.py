from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton, QLabel)
from PySide6.QtCore import Qt, QTimer
from src.ui.widgets import WorkspaceItem
from src.ui.settings_window import SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self, config, hypr):
        super().__init__()
        self.config = config
        self.hypr = hypr
        self.is_editing = False
        self.setWindowTitle("Hyprland Workspace Manager")
        self.resize(400, 600)
        
        # Set window flags for always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.setup_ui()
        self.apply_settings()
        self.refresh_workspaces()
        
        # Auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_workspaces)
        self.timer.start(5000) # Refresh every 5 seconds

    def showEvent(self, event):
        super().showEvent(event)
        # Use a tiny delay to ensure Hyprland has registered the window
        QTimer.singleShot(50, self.hypr.make_floating_and_center)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Top bar
        top_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search workspaces...")
        self.search_bar.textChanged.connect(self.filter_workspaces)
        top_layout.addWidget(self.search_bar)
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(self.settings_btn)
        
        self.main_layout.addLayout(top_layout)

        # Workspace list
        self.list_widget = QListWidget()
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.list_widget)

        self.error_label = QLabel("No workspaces found. Is Hyprland running?")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

    def apply_settings(self):
        self.setWindowOpacity(self.config.transparency)
        if self.config.theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #1e1e2e; color: #cdd6f4; }
                QLineEdit { background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px; color: #cdd6f4; }
                QListWidget { background-color: #1e1e2e; border: none; }
                QPushButton { background-color: #313244; border: none; border-radius: 5px; color: #cdd6f4; }
                QPushButton:hover { background-color: #45475a; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #eff1f5; color: #4c4f69; }
                QLineEdit { background-color: #e6e9ef; border: 1px solid #ccd0da; border-radius: 5px; padding: 5px; color: #4c4f69; }
                QListWidget { background-color: #eff1f5; border: none; }
                QPushButton { background-color: #e6e9ef; border: none; border-radius: 5px; color: #4c4f69; }
                QPushButton:hover { background-color: #ccd0da; }
            """)

    def open_settings(self):
        dialog = SettingsWindow(self.config, self)
        if dialog.exec():
            self.apply_settings()
            self.hypr.hyprctl_path = self.config.hyprctl_path
            self.refresh_workspaces()

    def cleanup_empty_workspaces(self, active_workspaces):
        active_ids = {str(ws['id']) for ws in active_workspaces}
        stored_names = self.config.data.get("workspace_names", {})
        
        # Find IDs that are in config but not in active workspaces
        to_remove = [ws_id for ws_id in stored_names if ws_id not in active_ids]
        
        for ws_id in to_remove:
            self.config.remove_workspace_name(ws_id)

    def refresh_workspaces(self):
        if self.is_editing:
            return

        # Store current search text
        search_text = self.search_bar.text().lower()
        
        workspaces = self.hypr.get_workspaces()
        self.cleanup_empty_workspaces(workspaces)
        
        if not workspaces:
            self.list_widget.hide()
            self.error_label.show()
            return
        
        self.list_widget.show()
        self.error_label.hide()

        # Sort by ID
        workspaces.sort(key=lambda x: x['id'])
        
        self.list_widget.clear()
        for ws in workspaces:
            ws_id = ws['id']
            custom_name = self.config.get_workspace_name(ws_id)
            display_name = custom_name if custom_name else str(ws_id)
            
            if search_text and search_text not in display_name.lower():
                continue
                
            item = QListWidgetItem(self.list_widget)
            widget = WorkspaceItem(ws_id, display_name)
            widget.clicked.connect(self.navigate_to_workspace)
            widget.renamed.connect(self.rename_workspace)
            widget.editing_started.connect(self.on_editing_started)
            widget.editing_finished.connect(self.on_editing_finished)
            
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def filter_workspaces(self):
        self.refresh_workspaces()

    def navigate_to_workspace(self, ws_id):
        self.hypr.switch_to_workspace(ws_id)
        self.close()

    def rename_workspace(self, ws_id, new_name):
        self.config.set_workspace_name(ws_id, new_name)
        self.filter_workspaces()

    def on_editing_started(self):
        self.is_editing = True
        self.timer.stop()

    def on_editing_finished(self):
        self.is_editing = False
        self.timer.start(5000)
