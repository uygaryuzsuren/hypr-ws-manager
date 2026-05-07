from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton, QLabel)
from PySide6.QtCore import Qt, QTimer, QThread, QEvent, QSize
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
        self.setMinimumSize(800, 600)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setup_ui()
        self.apply_settings()
        self.refresh_workspaces()
        
        active_ws = self.hypr.get_active_workspace()
        self.last_workspace_id = active_ws['id'] if active_ws else None
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_workspace_change)
        self.timer.start(2000)

    def check_workspace_change(self):
        if self.is_exploding:
            return
            
        active_ws = self.hypr.get_active_workspace()
        if active_ws and active_ws['id'] != self.last_workspace_id:
            self.close()
        
        self.refresh_workspaces()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self.hypr.make_floating_and_center)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
            current_item = self.list_widget.currentItem()
            if current_item:
                ws_id = current_item.data(Qt.UserRole)
                if ws_id:
                    self.navigate_to_workspace(ws_id)
        super().keyPressEvent(event)

    def filter_workspaces(self):
        self.refresh_workspaces()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

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

        self.list_widget = QListWidget()
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.list_widget)

        explode_layout = QHBoxLayout()
        self.explode_btn = QPushButton("Explode")
        self.explode_btn.clicked.connect(self.on_explode_all)
        explode_layout.addWidget(self.explode_btn)

        self.explode_app_btn = QPushButton("Explode by App")
        self.explode_app_btn.clicked.connect(self.on_explode_by_app)
        explode_layout.addWidget(self.explode_app_btn)

        self.explode_token_btn = QPushButton("Explode by Token")
        self.explode_token_btn.clicked.connect(self.on_explode_by_token)
        explode_layout.addWidget(self.explode_token_btn)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Token...")
        self.token_input.setFixedWidth(80)
        explode_layout.addWidget(self.token_input)
        
        self.main_layout.addLayout(explode_layout)

        self.error_label = QLabel("No workspaces found. Is Hyprland running?")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

    def open_settings(self):
        dialog = SettingsWindow(self.config, self)
        if dialog.exec():
            self.apply_settings()
            self.hypr.hyprctl_path = self.config.hyprctl_path
            self.refresh_workspaces()

    def navigate_to_workspace(self, ws_id):
        self.hypr.switch_to_workspace(ws_id)
        self.close()

    def on_explode_by_app(self):
        active_ws = self.hypr.get_active_workspace()
        if not active_ws:
            return
        original_ws_id = active_ws['id']
        
        all_windows = self.hypr.get_all_windows()
        windows = [w for w in all_windows if int(w['workspace']['id']) == original_ws_id]
        if not windows:
            return

        self.is_exploding = True
        
        from collections import defaultdict
        grouped_windows = defaultdict(list)
        for win in windows:
            grouped_windows[win['class']].append(win)

        existing_ids = self.hypr.get_existing_workspace_ids()
        candidate_id = 1
        
        for app_class, group in grouped_windows.items():
            while candidate_id in existing_ids:
                candidate_id += 1
            new_ws_id = candidate_id
            existing_ids.append(new_ws_id)
            
            first_win = group[0]
            win_title = first_win['title'] or f"Window_{app_class}"
            
            import re
            clean_title = re.sub(r'[^a-zA-Z0-9_-]', ' ', win_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip().replace(" ", "_")
            clean_class = re.sub(r'[^a-zA-Z0-9_-]', '_', app_class)
            
            name = f"[{clean_class}]-{clean_title}"
            
            self.hypr.switch_to_workspace(new_ws_id)
            for window in group:
                self.hypr.move_window_to_workspace(window['address'], new_ws_id)
            
            QThread.msleep(100)
            self.hypr.set_workspace_name(new_ws_id, name)
            self.config.set_workspace_name(new_ws_id, name)
            self.config.set_original_title(new_ws_id, win_title)
            
        self.hypr.switch_to_workspace(original_ws_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_explode_by_token(self):
        token = self.token_input.text().strip()
        if not token:
            return

        active_ws = self.hypr.get_active_workspace()
        if not active_ws:
            return
        original_ws_id = active_ws['id']
        
        all_windows = self.hypr.get_all_windows()
        windows = [w for w in all_windows if int(w['workspace']['id']) == original_ws_id]
        group = [win for win in windows if token.lower() in win['title'].lower()]
        
        if not group:
            return

        self.is_exploding = True
        
        existing_ids = self.hypr.get_existing_workspace_ids()
        candidate_id = 1
        while candidate_id in existing_ids:
            candidate_id += 1
        new_ws_id = candidate_id
        
        first_win = group[0]
        win_title = first_win['title']
        
        import re
        clean_title = re.sub(r'[^a-zA-Z0-9_-]', ' ', win_title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip().replace(" ", "_")
        
        name = f"[Token-{token}]-{clean_title}"
        
        self.hypr.switch_to_workspace(new_ws_id)
        for window in group:
            self.hypr.move_window_to_workspace(window['address'], new_ws_id)
            
        QThread.msleep(100)
        self.hypr.set_workspace_name(new_ws_id, name)
        self.config.set_workspace_name(new_ws_id, name)
        self.config.set_original_title(new_ws_id, win_title)
            
        self.hypr.switch_to_workspace(original_ws_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_explode_all(self):
        active_ws = self.hypr.get_active_workspace()
        if not active_ws:
            return
        original_ws_id = active_ws['id']
        
        self.is_exploding = True

        all_windows = self.hypr.get_all_windows()
        windows = [w for w in all_windows if int(w['workspace']['id']) == original_ws_id]
        if not windows:
            self.is_exploding = False
            return

        existing_ids = self.hypr.get_existing_workspace_ids()
        
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
            
            import re
            clean_title = re.sub(r'[^a-zA-Z0-9_-]', ' ', win_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip().replace(" ", "_")
            clean_class = re.sub(r'[^a-zA-Z0-9_-]', '_', win_class)
            
            name = f"[{clean_class}]-{clean_title}"
            
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
        alpha = int(self.config.transparency * 255)
        
        if self.config.theme == "dark":
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{ background-color: rgba(30, 30, 46, {alpha}); color: #cdd6f4; }}
                QLineEdit {{ background-color: rgba(49, 50, 68, {alpha}); border: 1px solid #45475a; border-radius: 5px; padding: 5px; color: #cdd6f4; }}
                QListWidget {{ background-color: transparent; border: none; }}
                QListWidget::item:hover {{ background-color: #313244; border-radius: 5px; }}
                QPushButton {{ background-color: rgba(49, 50, 68, {alpha}); border: none; border-radius: 5px; color: #cdd6f4; padding: 8px 12px; }}
                QPushButton:hover {{ background-color: #45475a; }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{ background-color: rgba(239, 241, 245, {alpha}); color: #cdd6f4; }}
                QLineEdit {{ background-color: rgba(230, 233, 239, {alpha}); border: 1px solid #ccd0da; border-radius: 5px; padding: 5px; color: #4c4f69; }}
                QListWidget {{ background-color: transparent; border: none; }}
                QListWidget::item:hover {{ background-color: #ccd0da; border-radius: 5px; }}
                QPushButton {{ background-color: rgba(230, 233, 239, {alpha}); border: none; border-radius: 5px; color: #4c4f69; padding: 8px 12px; }}
                QPushButton:hover {{ background-color: #ccd0da; }}
            """)

    def cleanup_empty_workspaces(self, active_workspaces):
        active_ids = {str(ws['id']) for ws in active_workspaces}
        stored_names = self.config.data.get("workspace_names", {})
        
        to_remove = [ws_id for ws_id in stored_names if ws_id not in active_ids]
        
        for ws_id in to_remove:
            self.config.remove_workspace_name(ws_id)

    def refresh_workspaces(self):
        if self.is_editing:
            return

        search_text = self.search_bar.text().lower()
        
        current_item = self.list_widget.currentItem()
        selected_ws_id = current_item.data(Qt.UserRole) if current_item else None
        
        workspaces = self.hypr.get_workspaces()
        self.cleanup_empty_workspaces(workspaces)
        
        if not workspaces:
            self.list_widget.hide()
            self.error_label.show()
            return
        
        self.list_widget.show()
        self.error_label.hide()

        workspaces.sort(key=lambda x: x['id'])
        
        self.list_widget.clear()
        reselected_item = None
        for ws in workspaces:
            ws_id = ws['id']
            # Find all window classes in this workspace
            all_wins = self.hypr.get_all_windows()
            wins = [w for w in all_wins if int(w['workspace']['id']) == int(ws_id)]
            # Exclude hypr-ws-manager itself from the icons
            app_classes = [w['class'].lower() for w in wins if w['class'] != "hypr-ws-manager"] if wins else []
            
            sanitized_name = self.config.get_workspace_name(ws_id)
            original_title = self.config.get_original_title(ws_id)
            
            # Formatting display: ID-[APP_CLASS]-Original_Title
            if sanitized_name:
                import re
                # Clean up: remove existing ID prefix like "7-" from sanitized_name
                clean_name = re.sub(r'^\d+-', '', sanitized_name)
                match = re.search(r'\[(.*?)\]', clean_name)

                # Ensure app_class comes from the window if possible, else the name tag
                display_app_class = app_classes[0] if app_classes else (match.group(1).lower() if match else "application-x-executable")

                title_to_show = original_title if original_title else re.sub(r'\[.*?\]-', '', clean_name)
                
                # Avoid redundant ID at the end
                if str(title_to_show) == str(ws_id):
                    title_to_show = ""

                if len(str(title_to_show)) > 80:
                    title_to_show = str(title_to_show)[:80] + "..."
                
                if title_to_show:
                    display_name = f"{ws_id}-[{display_app_class}]-{title_to_show}"
                else:
                    display_name = f"{ws_id}-[{display_app_class}]"

            else:
                display_app_class = app_classes[0] if app_classes else "application-x-executable"
                if original_title and str(original_title) != str(ws_id):
                    display_name = f"{ws_id}-[{display_app_class}]-{original_title}"
                else:
                    display_name = f"{ws_id}-[{display_app_class}]"
            
            if search_text and search_text not in display_name.lower():
                continue
                
            item = QListWidgetItem("")
            item.setData(Qt.UserRole, ws_id)
            widget = WorkspaceItem(ws_id, display_name, app_classes=app_classes)
            widget.clicked.connect(self.navigate_to_workspace)
            widget.renamed.connect(self.rename_workspace)
            widget.editing_started.connect(self.on_editing_started)
            widget.editing_finished.connect(self.on_editing_finished)
            
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
            if ws_id == selected_ws_id:
                reselected_item = item
        
        if reselected_item:
            self.list_widget.setCurrentItem(reselected_item)

    def rename_workspace(self, ws_id, new_name):
        import re
        # Strip ID- prefix and [class]- prefix if they exist to avoid recursive prefixing
        clean_name = re.sub(r'^\d+-(\[.*?\]-)?', '', new_name)
        # Also handle case where it's just the ID
        if clean_name == str(ws_id):
            clean_name = ""
            
        self.config.set_workspace_name(ws_id, clean_name)
        self.config.set_original_title(ws_id, clean_name)
        self.filter_workspaces()

    def on_editing_started(self):
        self.is_editing = True
        self.timer.stop()

    def on_editing_finished(self):
        self.is_editing = False
        self.timer.start(5000)
