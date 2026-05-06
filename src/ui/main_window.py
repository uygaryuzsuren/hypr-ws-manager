from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton, QLabel)
from PySide6.QtCore import Qt, QTimer, QThread
from src.ui.widgets import WorkspaceItem
from src.ui.settings_window import SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self, config, hypr):
        super().__init__()
        self.config = config
        self.hypr = hypr
        self.is_editing = False
        self.is_exploding = False
        self.setWindowTitle("Hyprland Workspace Manager")
        self.resize(400, 600)
        
        # Set window flags for always on top and transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.setup_ui()
        self.apply_settings()
        self.refresh_workspaces()
        
        # Track active workspace for auto-close
        active_ws = self.hypr.get_active_workspace()
        self.last_workspace_id = active_ws['id'] if active_ws else None
        
        # Auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_workspace_change)
        self.timer.start(200) # Check frequently for responsiveness

    def check_workspace_change(self):
        if self.is_exploding:
            return
            
        active_ws = self.hypr.get_active_workspace()
        if active_ws and active_ws['id'] != self.last_workspace_id:
            self.close()
        
        self.refresh_workspaces()

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

        self.explode_btn = QPushButton("Explode Current Workspace")
        self.explode_btn.clicked.connect(self.on_explode_all)
        self.main_layout.addWidget(self.explode_btn)

        self.error_label = QLabel("No workspaces found. Is Hyprland running?")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

    def on_explode_all(self):
        active_ws = self.hypr.get_active_workspace()
        if not active_ws:
            return
        original_ws_id = active_ws['id']
        
        self.is_exploding = True

        windows = self.hypr.get_active_workspace_windows()
        if not windows:
            self.is_exploding = False
            return

        # Get existing IDs to find empty ones
        existing_ids = self.hypr.get_existing_workspace_ids()
        
        # Start looking for empty workspaces from ID 1
        available_ws_ids = []
        candidate_id = 1
        while len(available_ws_ids) < len(windows):
            if candidate_id not in existing_ids:
                available_ws_ids.append(candidate_id)
            candidate_id += 1
        
        for i, window in enumerate(windows):
            new_ws_id = available_ws_ids[i]
            win_addr = window['address']
            win_title = window['title']
            win_class = window['class']
            if not win_title:
                win_title = f"Window_{win_class}"
            
            # Sanitise title for workspace name
            import re
            clean_title = re.sub(r'[^a-zA-Z0-9_-]', ' ', win_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip().replace(" ", "_")
            
            # Sanitise class
            clean_class = re.sub(r'[^a-zA-Z0-9_-]', '_', win_class)
            
            name = f"{new_ws_id}-[{clean_class}]-{clean_title}"
            
            # Create/switch to workspace so it exists, then move and rename
            self.hypr.switch_to_workspace(new_ws_id)
            self.hypr.move_window_to_workspace(win_addr, new_ws_id)
            QThread.msleep(100)
            self.hypr.set_workspace_name(new_ws_id, name)
            self.config.set_workspace_name(new_ws_id, name)
            self.config.set_original_title(new_ws_id, win_title)
            
        self.hypr.switch_to_workspace(original_ws_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def apply_settings(self):
        # We handle opacity via rgba in the CSS instead of setWindowOpacity
        alpha = int(self.config.transparency * 255)
        
        if self.config.theme == "dark":
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{ background-color: rgba(30, 30, 46, {alpha}); color: #cdd6f4; }}
                QLineEdit {{ background-color: rgba(49, 50, 68, {alpha}); border: 1px solid #45475a; border-radius: 5px; padding: 5px; color: #cdd6f4; }}
                QListWidget {{ background-color: transparent; border: none; }}
                QPushButton {{ background-color: rgba(49, 50, 68, {alpha}); border: none; border-radius: 5px; color: #cdd6f4; padding: 8px 12px; }}
                QPushButton:hover {{ background-color: #45475a; }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{ background-color: rgba(239, 241, 245, {alpha}); color: #4c4f69; }}
                QLineEdit {{ background-color: rgba(230, 233, 239, {alpha}); border: 1px solid #ccd0da; border-radius: 5px; padding: 5px; color: #4c4f69; }}
                QListWidget {{ background-color: transparent; border: none; }}
                QPushButton {{ background-color: rgba(230, 233, 239, {alpha}); border: none; border-radius: 5px; color: #4c4f69; padding: 8px 12px; }}
                QPushButton:hover {{ background-color: #ccd0da; }}
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
            # We want to display: ID-[APP_CLASS]-Original_Title
            # We fetch original title and app class from config
            original_title = self.config.get_original_title(ws_id)
            
            # Extract app class from the sanitized name if available for display
            # Or store app class in a new config field? Let's try to extract from the sanitized name first.
            sanitized_name = self.config.get_workspace_name(ws_id)
            
            display_name = str(ws_id)
            if sanitized_name:
                import re
                match = re.search(r'\[(.*?)\]', sanitized_name)
                app_class = match.group(1) if match else ""
                
                if original_title:
                    display_name = f"{ws_id}-[{app_class}]-{original_title}"
                else:
                    display_name = sanitized_name
            
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
        # Also update original_titles so refresh_workspaces picks up the new name
        self.config.set_original_title(ws_id, new_name)
        self.filter_workspaces()

    def on_editing_started(self):
        self.is_editing = True
        self.timer.stop()

    def on_editing_finished(self):
        self.is_editing = False
        self.timer.start(5000)
