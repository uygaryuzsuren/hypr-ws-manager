from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton, QLabel, QComboBox)
from PySide6.QtCore import Qt, QTimer, QThread, QEvent, QSize
from PySide6.QtGui import QGuiApplication
import json
import time
from pathlib import Path
from src.ui.widgets import WorkspaceItem
from src.ui.settings_window import SettingsWindow
from src.ui.overview_window import OverviewWindow
from src import __version__

class MainWindow(QMainWindow):
    def __init__(self, config, hypr):
        super().__init__()
        self.config = config
        self.hypr = hypr
        self.is_editing = False
        self.is_exploding = False
        self.setWindowTitle(f"Hyprland Workspace Manager {__version__}")
        self.setMinimumSize(800, 600)
        
        # Set dynamic maximum size (4/5 of total viewport)
        screen = QGuiApplication.primaryScreen().geometry()
        max_w = int(screen.width() * 0.8)
        max_h = int(screen.height() * 0.8)
        self.setMaximumSize(max_w, max_h)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setup_ui()
        self.apply_settings()
        self.refresh_workspaces()
        
        active_ws = self.hypr.get_active_workspace()
        self.last_workspace_id = active_ws['id'] if active_ws else None
        
        self.search_bar.setFocus()
        
        # Workspace update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_workspace_change)
        self.timer.start(2000)

    def check_workspace_change(self):
        if self.is_exploding:
            return
            
        #active_ws = self.hypr.get_active_workspace()
        #if active_ws and active_ws['id'] != self.last_workspace_id:
        #    self.close()
        
        self.refresh_workspaces()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self.hypr.make_floating_and_center)

    def keyPressEvent(self, event):
        if self.is_editing:
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
            current_item = self.list_widget.currentItem()
            if current_item:
                ws_id = current_item.data(Qt.UserRole)
                if ws_id:
                    self.navigate_to_workspace(ws_id)
        super().keyPressEvent(event)

    def create_custom_icon(self, color1, color2, with_triangle=False, icon_type="default"):
        from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPainterPath, QPen
        from PySide6.QtCore import Qt, QPoint
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if icon_type == "quotes":
            painter.setPen(QColor(color1))
            painter.setFont(QFont("Monospace", 14, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, '""')
        elif icon_type == "collect":
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(color1), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            path = QPainterPath()
            path.moveTo(16, 4)
            path.lineTo(16, 20)
            path.lineTo(8, 20)
            path.lineTo(12, 16)
            path.moveTo(8, 20)
            path.lineTo(12, 24)
            painter.drawPath(path)
        elif icon_type == "collect_token":
            painter.setPen(QPen(QColor(color1), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.moveTo(16, 4)
            path.lineTo(16, 16)
            path.lineTo(10, 16)
            path.lineTo(13, 13)
            path.moveTo(10, 16)
            path.lineTo(13, 19)
            painter.drawPath(path)
            painter.setPen(QColor(color1))
            painter.setFont(QFont("Monospace", 10, QFont.Bold))
            painter.drawText(pixmap.rect().adjusted(0, 4, 0, 0), Qt.AlignCenter, '""')
        elif icon_type == "clock":
            painter.setPen(QPen(QColor(color1), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(6, 6, 20, 20)
            painter.drawLine(16, 16, 16, 10)
            painter.drawLine(16, 16, 22, 16)
        elif icon_type == "magnifier":
            painter.setPen(QPen(QColor(color1), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(6, 6, 12, 12)
            painter.drawLine(16, 16, 26, 26)
        else:
            painter.setBrush(QColor(color1))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(4, 4, 24, 24)
            if with_triangle:
                painter.setBrush(QColor(color2))
                points = [QPoint(24, 24), QPoint(32, 24), QPoint(28, 32)]
                painter.drawPolygon(points)
        
        painter.end()
        return QIcon(pixmap)

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

        # Overview and Action Buttons
        overview_layout = QHBoxLayout()
        self.overview_btn = QPushButton("Overview")
        self.overview_btn.setIcon(self.create_custom_icon("#89b4fa", "#89b4fa", icon_type="magnifier"))
        self.overview_btn.clicked.connect(self.open_overview)
        overview_layout.addWidget(self.overview_btn)
        overview_layout.addStretch()
        self.main_layout.addLayout(overview_layout)

        explode_layout = QHBoxLayout()
        self.explode_btn = QPushButton("Explode")
        self.explode_btn.setIcon(self.create_custom_icon("#89b4fa", "#89b4fa", with_triangle=False))
        self.explode_btn.clicked.connect(self.on_explode_all)
        explode_layout.addWidget(self.explode_btn)

        self.app_selector_explode_all = QComboBox()
        self.app_selector_explode_all.setMinimumWidth(150)
        self.app_selector_explode_all.hide()
        explode_layout.addWidget(self.app_selector_explode_all)

        self.explode_app_btn = QPushButton("Explode by App")
        self.explode_app_btn.setIcon(self.create_custom_icon("#89b4fa", "#f38ba8", with_triangle=True))
        self.explode_app_btn.clicked.connect(self.on_explode_by_app)
        explode_layout.addWidget(self.explode_app_btn)

        self.app_selector_explode_app = QComboBox()
        self.app_selector_explode_app.setMinimumWidth(150)
        self.app_selector_explode_app.hide()
        explode_layout.addWidget(self.app_selector_explode_app)

        self.explode_token_btn = QPushButton("Explode by Token")
        self.explode_token_btn.setIcon(self.create_custom_icon("#89b4fa", "#89b4fa", icon_type="quotes"))
        self.explode_token_btn.clicked.connect(self.on_explode_by_token)
        explode_layout.addWidget(self.explode_token_btn)
        
        self.token_input_explode = QLineEdit()
        self.token_input_explode.setPlaceholderText("Token...")
        self.token_input_explode.setFixedWidth(80)
        self.token_input_explode.hide()
        explode_layout.addWidget(self.token_input_explode)
        
        self.main_layout.addLayout(explode_layout)

        collect_layout = QHBoxLayout()
        self.collect_app_btn = QPushButton("Collect by App")
        self.collect_app_btn.setIcon(self.create_custom_icon("#89b4fa", "#89b4fa", icon_type="collect"))
        self.collect_app_btn.clicked.connect(self.on_collect_by_app)
        collect_layout.addWidget(self.collect_app_btn)

        self.app_selector = QComboBox()
        self.app_selector.setMinimumWidth(150)
        self.app_selector.hide()
        collect_layout.addWidget(self.app_selector)

        self.collect_token_btn = QPushButton("Collect by Token")
        self.collect_token_btn.setIcon(self.create_custom_icon("#89b4fa", "#89b4fa", icon_type="collect_token"))
        self.collect_token_btn.clicked.connect(self.on_collect_by_token)
        collect_layout.addWidget(self.collect_token_btn)

        self.token_input_collect = QLineEdit()
        self.token_input_collect.setPlaceholderText("Token...")
        self.token_input_collect.setFixedWidth(80)
        self.token_input_collect.hide()
        collect_layout.addWidget(self.token_input_collect)
        
        self.collect_garbage_btn = QPushButton("Collect Garbage")
        self.collect_garbage_btn.setIcon(self.create_custom_icon("#89b4fa", "#89b4fa", icon_type="clock"))
        self.collect_garbage_btn.clicked.connect(self.on_collect_garbage)
        self.collect_garbage_btn.setVisible(self.config.tracking_enabled)
        collect_layout.addWidget(self.collect_garbage_btn)

        self.garbage_time_selector = QComboBox()
        self.garbage_time_selector.addItems([
            "15 minutes", "30 minutes", "45 minutes", "1 hour", "2 hours", 
            "3 hours", "6 hours", "12 hours", "24 hours", "36 hours", "72 hours", "Older"
        ])
        self.garbage_time_selector.hide()
        collect_layout.addWidget(self.garbage_time_selector)
        
        # Bottom row
        self.main_layout.addLayout(collect_layout)

        # Sync inputs
        self.token_input_explode.textChanged.connect(self.token_input_collect.setText)
        self.token_input_collect.textChanged.connect(self.token_input_explode.setText)

        self.error_label = QLabel("No workspaces found. Is Hyprland running?")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

    def open_overview(self):
        dialog = OverviewWindow(self.config, self.hypr, self)
        dialog.exec()

    def open_settings(self):
        dialog = SettingsWindow(self.config, self)
        if dialog.exec():
            self.apply_settings()
            self.hypr.hyprctl_path = self.config.hyprctl_path
            self.refresh_workspaces()

    def navigate_to_workspace(self, ws_id):
        self.hypr.switch_to_workspace(ws_id)
        #self.close()

    def on_item_clicked(self, ws_id, item):
        # If the item is already selected, navigate
        if self.list_widget.currentItem() == item:
            self.navigate_to_workspace(ws_id)
        else:
            # Otherwise, just select it
            self.list_widget.setCurrentItem(item)

    def on_explode_by_app(self):
        # Reveal input on first click
        if self.app_selector_explode_app.isHidden():
            self.app_selector_explode_app.show()
            self.app_selector_explode_app.setFocus()
            return

        # Capture the initially active workspace to return to it later
        active_ws = self.hypr.get_active_workspace()
        if not active_ws: return
        initial_active_id = active_ws['id']

        # Get source workspace from selection, fallback to active
        current_item = self.list_widget.currentItem()
        if current_item:
            source_ws_id = current_item.data(Qt.UserRole)
        else:
            source_ws_id = initial_active_id
        
        all_windows = self.hypr.get_all_windows()
        all_windows = [w for w in all_windows if int(w['workspace']['id']) == int(source_ws_id) and w['class'] != "hypr-ws-manager"]
        if not all_windows:
            return

        self.is_exploding = True
        
        from collections import defaultdict
        all_grouped_windows = defaultdict(list)
        grouped_windows = defaultdict(list)

        selected_type = self.app_selector_explode_app.currentText()
        
        for win in all_windows:
            all_grouped_windows[win['class']].append('x')
            if selected_type == "All" or win['class'] == selected_type:
                grouped_windows[win['class']].append(win)

        if not grouped_windows:
            self.is_exploding = False
            return

        existing_ids = self.hypr.get_existing_workspace_ids()
        candidate_id = 1
        count_left = len(all_grouped_windows)
        for app_class, group in grouped_windows.items():
            
            if count_left <= 1:
                break

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
            
            #self.hypr.switch_to_workspace(new_ws_id)
            for window in group:
                self.hypr.move_window_to_workspace(window['address'], new_ws_id)
            
            count_left-=1
            QThread.msleep(100)
            self.hypr.set_workspace_name(new_ws_id, name)
            self.config.set_workspace_name(new_ws_id, name)
            self.config.set_original_title(new_ws_id, win_title)
            
        #self.hypr.switch_to_workspace(initial_active_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_explode_by_token(self):
        # Reveal input on first click
        if self.token_input_explode.isHidden():
            self.token_input_explode.show()
            self.token_input_explode.setFocus()
            return

        token = self.token_input_explode.text().strip()
        if not token:
            return

        # Capture the initially active workspace to return to it later
        active_ws = self.hypr.get_active_workspace()
        if not active_ws: return
        initial_active_id = active_ws['id']

        # Get source workspace from selection, fallback to active
        current_item = self.list_widget.currentItem()
        if current_item:
            source_ws_id = current_item.data(Qt.UserRole)
        else:
            source_ws_id = initial_active_id
        
        all_windows = self.hypr.get_all_windows()
        windows = [w for w in all_windows if int(w['workspace']['id']) == int(source_ws_id)]
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
            
        self.hypr.switch_to_workspace(initial_active_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_explode_all(self):
        # Reveal input on first click
        if self.app_selector_explode_all.isHidden():
            self.app_selector_explode_all.show()
            self.app_selector_explode_all.setFocus()
            return

        # Capture the initially active workspace to return to it later
        active_ws = self.hypr.get_active_workspace()
        if not active_ws: return
        initial_active_id = active_ws['id']

        #print("Initial Active Id=" + str(initial_active_id))

        # Get source workspace from selection, fallback to active
        current_item = self.list_widget.currentItem()
        if current_item:
            source_ws_id = current_item.data(Qt.UserRole)
            #print("Selected Id = " + str(source_ws_id))
        else:
            source_ws_id = initial_active_id
        
        self.is_exploding = True

        all_windows = self.hypr.get_all_windows()
        all_windows = [w for w in all_windows if int(w['workspace']['id']) == int(source_ws_id) and w['class'] != "hypr-ws-manager"]
        
        selected_type = self.app_selector_explode_all.currentText()

        windows = all_windows
        # Filter windows if a specific app is selected
        if selected_type != "All":
            windows = [w for w in windows if w['class'] == selected_type]

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
        count_to_move = len(all_windows) 
        for i, window in enumerate(windows):
            #print("Count to move = " + str(count_to_move))
            if count_to_move <= 1:
                break;
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
            
            #self.hypr.switch_to_workspace(new_ws_id)
            self.hypr.move_window_to_workspace(win_addr, new_ws_id)
            count_to_move-=1;
            QThread.msleep(100)
            self.hypr.set_workspace_name(new_ws_id, name)
            self.config.set_workspace_name(new_ws_id, name)
            self.config.set_original_title(new_ws_id, win_title)
            
        #self.hypr.switch_to_workspace(initial_active_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_collect_by_app(self):
        # Reveal input on first click
        if self.app_selector.isHidden():
            self.app_selector.show()
            self.app_selector.setFocus()
            return

        selected_app = self.app_selector.currentText()
        if not selected_app:
            return

        # Get target workspace from selection, fallback to active
        current_item = self.list_widget.currentItem()
        if current_item:
            target_ws_id = current_item.data(Qt.UserRole)
        else:
            active_ws = self.hypr.get_active_workspace()
            if not active_ws: return
            target_ws_id = active_ws['id']

        self.is_exploding = True
        
        all_windows = self.hypr.get_all_windows()
        for window in all_windows:
            # Move if app matches OR if "All" is selected
            if (selected_app == "All" or window['class'] == selected_app) and int(window['workspace']['id']) != int(target_ws_id):
                self.hypr.move_window_to_workspace(window['address'], target_ws_id)
        
        self.hypr.switch_to_workspace(target_ws_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_collect_by_token(self):
        # Reveal input on first click
        if self.token_input_collect.isHidden():
            self.token_input_collect.show()
            self.token_input_collect.setFocus()
            return

        token = self.token_input_collect.text().strip()
        if not token:
            return

        # Get target workspace from selection, fallback to active
        current_item = self.list_widget.currentItem()
        if current_item:
            target_ws_id = current_item.data(Qt.UserRole)
        else:
            active_ws = self.hypr.get_active_workspace()
            if not active_ws: return
            target_ws_id = active_ws['id']

        self.is_exploding = True
        
        all_windows = self.hypr.get_all_windows()
        for window in all_windows:
            if token.lower() in window['title'].lower() and int(window['workspace']['id']) != int(target_ws_id):
                self.hypr.move_window_to_workspace(window['address'], target_ws_id)
        
        self.hypr.switch_to_workspace(target_ws_id)
        self.is_exploding = False
        self.refresh_workspaces()

    def on_collect_garbage(self):
        # Reveal selector on first click
        if self.garbage_time_selector.isHidden():
            self.garbage_time_selector.show()
            self.garbage_time_selector.setFocus()
            return

        # Get the selected duration
        selection = self.garbage_time_selector.currentText()
        
        # Calculate threshold in seconds
        now = int(time.time())
        threshold = 0
        
        if "minute" in selection:
            threshold = int(selection.split()[0]) * 60
        elif "hour" in selection:
            threshold = int(selection.split()[0]) * 3600
        elif selection == "Older":
            threshold = 72 * 3600 
        
        cutoff = now - threshold
        
        # Read activity state
        cache_file = Path.home() / ".cache" / "hypr-ws-manager" / "activity.json"
        if not cache_file.exists():
            return
            
        try:
            with open(cache_file, 'r') as f:
                activity = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        # Get target workspace (the one the app is in)
        active_ws = self.hypr.get_active_workspace()
        if not active_ws: return
        target_ws_id = active_ws['id']

        self.is_exploding = True
        
        all_windows = self.hypr.get_all_windows()
        for window in all_windows:
            addr = window['address']
            win_ws = int(window['workspace']['id'])
            
            # Only consider windows NOT in the target workspace
            if win_ws != int(target_ws_id):
                last_active = activity.get(addr, 0)
                if last_active < cutoff:
                    self.hypr.move_window_to_workspace(addr, target_ws_id)
        
        self.is_exploding = False
        self.refresh_workspaces()

    def apply_settings(self):
        # Update visibility of garbage collection feature
        if hasattr(self, 'collect_garbage_btn'):
            is_enabled = self.config.tracking_enabled
            self.collect_garbage_btn.setVisible(is_enabled)
            # If disabling, also hide the selector
            if not is_enabled:
                self.garbage_time_selector.hide()

        alpha = int(self.config.transparency * 255)
        
        if self.config.theme == "dark":
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{ background-color: rgba(30, 30, 46, {alpha}); color: #cdd6f4; }}
                QLineEdit {{ background-color: rgba(49, 50, 68, {alpha}); border: 1px solid #45475a; border-radius: 5px; padding: 5px; color: #cdd6f4; }}
                QComboBox {{ background-color: rgba(49, 50, 68, {alpha}); border: 1px solid #45475a; border-radius: 5px; padding: 5px 10px; color: #cdd6f4; }}
                QComboBox::drop-down {{ border: none; }}
                QListWidget {{ background-color: transparent; border: none; outline: none; }}
                QListWidget::item:hover {{ background-color: #313244; border-radius: 5px; }}
                QListWidget::item:selected {{ background-color: #3572af; border: none; border-radius: 5px; color: #ffffff; }}
                QListWidget::item:selected:active {{ background-color: #3572af; border: none; }}
                QListWidget::item:selected:!active {{ background-color: #3572af; border: none; }}
                QPushButton {{ background-color: rgba(49, 50, 68, {alpha}); border: none; border-radius: 5px; color: #cdd6f4; padding: 8px 12px; }}
                QPushButton:hover {{ background-color: #45475a; }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{ background-color: rgba(239, 241, 245, {alpha}); color: #4c4f69; }}
                QLineEdit {{ background-color: rgba(230, 233, 239, {alpha}); border: 1px solid #ccd0da; border-radius: 5px; padding: 5px; color: #4c4f69; }}
                QComboBox {{ background-color: rgba(204, 208, 218, {alpha}); border: 1px solid #ccd0da; border-radius: 5px; padding: 5px 10px; color: #4c4f69; }}
                QComboBox::drop-down {{ border: none; }}
                QListWidget {{ background-color: transparent; border: none; outline: none; }}
                QListWidget::item:hover {{ background-color: #ccd0da; border-radius: 5px; }}
                QListWidget::item:selected {{ background-color: #1e66f5; border: none; border-radius: 5px; color: #ffffff; }}
                QListWidget::item:selected:active {{ background-color: #1e66f5; border: none; }}
                QListWidget::item:selected:!active {{ background-color: #1e66f5; border: none; }}
                QPushButton {{ background-color: rgba(204, 208, 218, {alpha}); border: none; border-radius: 5px; color: #4c4f69; padding: 8px 12px; }}
                QPushButton:hover {{ background-color: #bcc0cc; }}
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
        
        all_wins = self.hypr.get_all_windows()
        # Update app selector with unique classes (excluding self)
        current_selection = self.app_selector.currentText()
        all_classes = ["All"]
        all_classes.extend(sorted(list(set(w['class'] for w in all_wins if w['class'] and w['class'] != "hypr-ws-manager"))))
        self.app_selector.clear()
        self.app_selector.addItems(all_classes)
        if current_selection in all_classes:
            self.app_selector.setCurrentText(current_selection)
        else:
            self.app_selector.setCurrentText("All")

        active_ws = self.hypr.get_active_workspace()
        active_id = active_ws['id'] if active_ws else None
        
        # Target workspace for explode selector is either selected or active
        target_ws_id = selected_ws_id if selected_ws_id else active_id
        explode_classes = ["All"]
        if target_ws_id:
            target_wins = [w for w in all_wins if int(w['workspace']['id']) == int(target_ws_id)]
            explode_classes.extend(sorted(list(set(w['class'] for w in target_wins if w['class'] and w['class'] != "hypr-ws-manager"))))
        
        # Populate Explode All dropdown
        current_explode_all_selection = self.app_selector_explode_all.currentText()
        self.app_selector_explode_all.clear()
        self.app_selector_explode_all.addItems(explode_classes)
        if current_explode_all_selection in explode_classes:
            self.app_selector_explode_all.setCurrentText(current_explode_all_selection)
        else:
            self.app_selector_explode_all.setCurrentText("All")

        # Populate Explode By App dropdown
        current_explode_app_selection = self.app_selector_explode_app.currentText()
        self.app_selector_explode_app.clear()
        self.app_selector_explode_app.addItems(explode_classes)
        if current_explode_app_selection in explode_classes:
            self.app_selector_explode_app.setCurrentText(current_explode_app_selection)
        else:
            self.app_selector_explode_app.setCurrentText("All")

        if not workspaces:
            self.list_widget.hide()
            self.error_label.show()
            return
        
        self.list_widget.show()
        self.error_label.hide()

        workspaces.sort(key=lambda x: x['id'])
        
        self.list_widget.clear()
        reselected_item = None
        active_item = None
        
        # Pre-retrieve and filter all windows to exclude this manager app
        all_wins = [w for w in self.hypr.get_all_windows() if w['class'] != "hypr-ws-manager"]
        
        for ws in workspaces:
            ws_id = ws['id']
            # Find all relevant windows in this workspace
            wins = [w for w in all_wins if int(w['workspace']['id']) == int(ws_id)]
            
            # Skip empty workspaces unless it is the active one
            if not wins and ws_id != active_id:
                continue

            # Get application classes for icons
            app_classes = [w['class'].lower() for w in wins] if wins else []
            
            sanitized_name = self.config.get_workspace_name(ws_id)
            original_title = self.config.get_original_title(ws_id)
            
            # Formatting display: ID-[APP_CLASS]-Original_Title
            if sanitized_name:
                import re
                # Clean up: remove existing ID prefix like "7-" from sanitized_name
                clean_name = re.sub(r'^\d+-', '', sanitized_name)
                match = re.search(r'\[(.*?)\]', clean_name)

                # Extract existing tags and current window tag, then de-duplicate
                existing_tags = re.findall(r'\[(.*?)\]', clean_name)
                app_class_tag = app_classes[0] if app_classes else ""
                
                all_tags = []
                for t in existing_tags + ([app_class_tag] if app_class_tag else []):
                    if t and t not in all_tags:
                        all_tags.append(t)
                
                tags_str = "".join([f"[{t}]" for t in all_tags])
                
                title_to_show = original_title if original_title else re.sub(r'\[.*?\]-', '', clean_name)
                
                # Avoid redundant ID at the end
                if str(title_to_show) == str(ws_id):
                    title_to_show = ""

                if len(str(title_to_show)) > 80:
                    title_to_show = str(title_to_show)[:80] + "..."
                
                # Construct name cleanly
                # We start with ws_id, then add other components
                display_name = str(ws_id)
                
                if tags_str:
                    display_name += "-" + tags_str
                
                if title_to_show and title_to_show not in all_tags:
                    display_name += "-" + title_to_show
                
                # Final cleanup to remove any potential trailing dash
                display_name = display_name.rstrip('-')

            else:
                display_app_class = app_classes[0] if app_classes else ""
                if display_app_class:
                    if original_title and str(original_title) != str(ws_id):
                        display_name = f"{ws_id}-[{display_app_class}]-{original_title}"
                    else:
                        display_name = f"{ws_id}-[{display_app_class}]"
                else:
                    display_name = f"{ws_id}-{original_title}" if original_title and str(original_title) != str(ws_id) else str(ws_id)
            
            # Check if search matches display name OR any window title in this workspace
            match_found = False
            if not search_text or search_text in display_name.lower():
                match_found = True
            else:
                for w in wins:
                    if search_text in w['title'].lower():
                        match_found = True
                        break
            
            if not match_found:
                continue
                
            item = QListWidgetItem("")
            item.setData(Qt.UserRole, ws_id)
            widget = WorkspaceItem(ws_id, display_name, app_classes=app_classes, is_active=(ws_id == active_id), theme=self.config.theme)
            
            # Connect to handle the 2-click logic
            widget.clicked.connect(lambda ws_id, item=item: self.on_item_clicked(ws_id, item))
            
            widget.renamed.connect(self.rename_workspace)
            widget.editing_started.connect(self.on_editing_started)
            widget.editing_finished.connect(self.on_editing_finished)
            
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
            if ws_id == active_id:
                active_item = item
            if selected_ws_id and ws_id == selected_ws_id:
                reselected_item = item
        
        # Priority: reselect previously selected, then focus active workspace
        target_item = reselected_item or active_item
        if target_item:
            self.list_widget.setCurrentItem(target_item)
            self.list_widget.scrollToItem(target_item)
            # Only steal focus back to list if no input is currently focused
            if not self.search_bar.hasFocus() and not self.token_input_explode.hasFocus() and not self.token_input_collect.hasFocus():
                self.list_widget.setFocus()

    def rename_workspace(self, ws_id, new_name):
        import re
        # Remove ID- prefix and all [tag] prefixes
        clean_name = re.sub(r'^\d+-', '', new_name)
        clean_name = re.sub(r'(\[.*?\]-?)', '', clean_name)
        # Strip any leading dashes or whitespace
        clean_name = clean_name.lstrip('-').strip()
        
        # If it's effectively empty or just the ws_id, store as empty to let auto-namer handle it
        if clean_name == str(ws_id) or not clean_name:
            clean_name = ""
            
        self.config.set_workspace_name(ws_id, clean_name)
        self.config.set_original_title(ws_id, clean_name)
        self.filter_workspaces()

    def on_editing_started(self):
        self.is_editing = True
        self.timer.stop()

    def on_editing_finished(self):
        # Use a small delay to prevent the Enter key that finished the edit
        # from bubbling up and triggering navigation in the same turn.
        QTimer.singleShot(200, self._finish_editing_state)

    def _finish_editing_state(self):
        self.is_editing = False
        self.timer.start(5000)
