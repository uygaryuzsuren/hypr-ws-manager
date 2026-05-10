from PySide6.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout, QWidget, QLabel, QComboBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QColor
import json
import time
from datetime import datetime
from pathlib import Path

class OverviewWindow(QDialog):
    def __init__(self, config, hypr, parent=None):
        super().__init__(parent)
        self.config = config
        self.hypr = hypr
        self.setWindowTitle("Workspace Overview")
        self.setMinimumSize(1050, 600)
        self.apply_theme()
        self.setup_ui()
        self.populate_tree()

    def apply_theme(self):
        if self.config.theme == "dark":
            self.setStyleSheet("""
                QDialog { background-color: #1e1e2e; color: #cdd6f4; }
                QTreeWidget { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 5px; outline: 0; }
                QTreeWidget::item { padding: 5px; min-height: 30px; }
                QTreeWidget::item:selected { background-color: #45475a; color: #89b4fa; }
                QWidget#action_widget { background-color: transparent; border: none; }
                QComboBox { background-color: #45475a; border: 1px solid #585b70; border-radius: 4px; color: #cdd6f4; padding: 2px; font-size: 11px; }
                QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; selection-background-color: #45475a; }
                QPushButton { background-color: #45475a; border: 1px solid #585b70; border-radius: 4px; color: #cdd6f4; padding: 2px 8px; font-size: 11px; height: 22px; }
                QPushButton:hover { background-color: #585b70; border: 1px solid #89b4fa; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #eff1f5; color: #4c4f69; }
                QTreeWidget { background-color: #e6e9ef; color: #4c4f69; border: 1px solid #ccd0da; border-radius: 5px; outline: 0; }
                QTreeWidget::item { padding: 5px; min-height: 30px; }
                QTreeWidget::item:selected { background-color: #ccd0da; color: #1e66f5; }
                QWidget#action_widget { background-color: transparent; border: none; }
                QComboBox { background-color: #ccd0da; border: 1px solid #bcc0cc; border-radius: 4px; color: #4c4f69; padding: 2px; font-size: 11px; }
                QComboBox QAbstractItemView { background-color: #e6e9ef; color: #4c4f69; border: 1px solid #ccd0da; selection-background-color: #ccd0da; }
                QPushButton { background-color: #ccd0da; border: 1px solid #bcc0cc; border-radius: 4px; color: #4c4f69; padding: 2px 8px; font-size: 11px; height: 22px; }
                QPushButton:hover { background-color: #bcc0cc; border: 1px solid #1e66f5; }
            """)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Workspace / Window", "Last Active", "Actions"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 400)
        layout.addWidget(self.tree)
        
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(120, 35)
        refresh_btn.clicked.connect(self.populate_tree)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 35)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def format_elapsed_time(self, timestamp):
        now = int(time.time())
        diff = now - timestamp
        hours = diff // 3600
        minutes = (diff % 3600) // 60
        return f"({hours}h {minutes}m ago)" if hours > 0 else f"({minutes}m ago)"

    def get_workspace_list(self, exclude_ws_id=None):
        ws = self.hypr.get_workspaces()
        result = []
        for w in sorted(ws, key=lambda x: x['id']):
            ws_id = w['id']
            if str(ws_id) == str(exclude_ws_id):
                continue
            ws_name = self.config.get_workspace_name(ws_id) or f"WS {ws_id}"
            result.append((str(ws_id), f"{ws_id}: {ws_name}"))
        return result

    def create_action_buttons(self, item, is_workspace, identifier):
        widget = QWidget()
        widget.setObjectName("action_widget")
        widget.setStyleSheet("background-color: transparent;")
        widget.setFixedHeight(30)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        nav_btn = QPushButton("Navigate")
        
        if is_workspace:
            term_btn = QPushButton("Terminate")
            term_btn.setStyleSheet(term_btn.styleSheet() + "color: #f38ba8;")
            nav_btn.clicked.connect(lambda: self.on_navigate_ws(identifier))
            term_btn.clicked.connect(lambda: self.on_terminate_ws(identifier))
            layout.addWidget(nav_btn)
            layout.addWidget(term_btn)
        else:
            ws_id, addr = identifier
            term_btn = QPushButton("Terminate")
            term_btn.setStyleSheet(term_btn.styleSheet() + "color: #f38ba8;")
            
            nav_btn.clicked.connect(lambda: self.on_navigate_win(ws_id, addr))
            term_btn.clicked.connect(lambda: self.on_terminate_win(addr))
            
            # Action buttons first
            layout.addWidget(nav_btn)
            layout.addWidget(term_btn)
            
            # Workspace selector
            ws_selector = QComboBox()
            ws_selector.setFixedWidth(100)
            ws_selector.setStyleSheet(self.styleSheet())
            for w_id, w_name in self.get_workspace_list(exclude_ws_id=ws_id):
                ws_selector.addItem(w_name, w_id)

            
            move_btn = QPushButton("Move")
            move_btn.clicked.connect(lambda: self.on_move_win(addr, ws_selector.currentData()))
            
            layout.addWidget(ws_selector)
            layout.addWidget(move_btn)
            
        layout.addStretch()
        return widget


    def suppress_tracking(self, address=None):
        try:
            suppress_file = Path.home() / '.cache' / 'hypr-ws-manager' / 'suppress.json'
            suppress_dir = suppress_file.parent
            suppress_dir.mkdir(parents=True, exist_ok=True)
            suppressed = []
            if suppress_file.exists():
                with open(suppress_file, 'r') as f:
                    try: suppressed = json.load(f)
                    except json.JSONDecodeError: pass
            if address and address not in suppressed:
                suppressed.append(address)
            elif not address and 'GLOBAL_SUPPRESS' not in suppressed:
                suppressed.append('GLOBAL_SUPPRESS')
            with open(suppress_file, 'w') as f:
                json.dump(suppressed, f)
            QTimer.singleShot(500, lambda: self.resume_tracking(address))
        except Exception as e: print(f'Failed to suppress tracking: {e}')

    def resume_tracking(self, address=None):
        try:
            suppress_file = Path.home() / '.cache' / 'hypr-ws-manager' / 'suppress.json'
            if not suppress_file.exists(): return
            with open(suppress_file, 'r') as f: suppressed = json.load(f)
            if address and address in suppressed: suppressed.remove(address)
            elif not address and 'GLOBAL_SUPPRESS' in suppressed: suppressed.remove('GLOBAL_SUPPRESS')
            with open(suppress_file, 'w') as f: json.dump(suppressed, f)
        except Exception as e: print(f'Failed to resume tracking: {e}')
    def on_move_win(self, addr, new_ws_id):
        self.suppress_tracking()
        self.hypr.move_window_to_workspace(addr, new_ws_id)
        time.sleep(0.1)
        self.populate_tree()

    def on_navigate_ws(self, ws_id):
        self.suppress_tracking()
        self.hypr.switch_to_workspace(ws_id)

    def on_terminate_ws(self, ws_id):
        all_wins = self.hypr.get_all_windows()
        ws_wins = [w for w in all_wins if int(w['workspace']['id']) == int(ws_id) and w['class'] != "hypr-ws-manager"]
        for win in ws_wins:
            self.hypr.close_window(win['address'])
        time.sleep(0.1)
        self.populate_tree()

    def on_navigate_win(self, ws_id, addr):
        try:
            suppress_file = Path.home() / ".cache" / "hypr-ws-manager" / "suppress.json"
            suppressed = []
            if suppress_file.exists():
                with open(suppress_file, 'r') as f:
                    suppressed = json.load(f)
            if addr not in suppressed:
                suppressed.append(addr)
                with open(suppress_file, 'w') as f:
                    json.dump(suppressed, f)
        except: pass
        self.hypr.switch_to_workspace(ws_id)
        self.hypr.focus_window(addr)

    def on_terminate_win(self, addr):
        self.hypr.close_window(addr)
        time.sleep(0.1)
        self.populate_tree()

    def populate_tree(self):
        self.tree.clear()
        workspaces = self.hypr.get_workspaces()
        workspaces.sort(key=lambda x: x['id'])
        all_wins = [w for w in self.hypr.get_all_windows() if w['class'] != "hypr-ws-manager"]
        activity = {}
        if self.config.tracking_enabled:
            cache_file = Path.home() / ".cache" / "hypr-ws-manager" / "activity.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        activity = json.load(f)
                except: pass
        for ws in workspaces:
            ws_id = ws['id']
            ws_name = self.config.get_workspace_name(ws_id) or f"Workspace {ws_id}"
            ws_item = QTreeWidgetItem(self.tree)
            ws_item.setText(0, f"Workspace {ws_id}: {ws_name}")
            self.tree.setItemWidget(ws_item, 2, self.create_action_buttons(ws_item, True, ws_id))
            ws_wins = [w for w in all_wins if int(w['workspace']['id']) == int(ws_id)]
            for win in ws_wins:
                addr = win['address']
                win_class = win['class']
                win_title = win['title']
                win_item = QTreeWidgetItem(ws_item)
                win_item.setText(0, f"[{win_class}] {win_title}")
                icon = QIcon.fromTheme(win_class.lower())
                if not icon.isNull():
                    win_item.setIcon(0, icon)
                else:
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(QColor(0, 0, 0, 100) if self.config.theme == "dark" else QColor(0, 0, 0, 50))
                    win_item.setIcon(0, QIcon(pixmap))
                if self.config.tracking_enabled:
                    ts = activity.get(addr)
                    if ts:
                        dt = datetime.fromtimestamp(ts)
                        win_item.setText(1, f"{dt.strftime('%a %d %H:%M')} {self.format_elapsed_time(ts)}")
                    else: win_item.setText(1, "Never")
                self.tree.setItemWidget(win_item, 2, self.create_action_buttons(win_item, False, (ws_id, addr)))
        self.tree.expandAll()
