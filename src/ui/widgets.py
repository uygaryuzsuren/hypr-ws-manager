from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QPixmap
import re

class WorkspaceItem(QWidget):
    clicked = Signal(int)
    renamed = Signal(int, str)
    editing_started = Signal()
    editing_finished = Signal()

    def __init__(self, ws_id, display_name, app_classes=None, is_active=False, theme="dark", parent=None):
        super().__init__(parent)
        self.ws_id = ws_id
        self.display_name = display_name
        self.app_classes = app_classes if app_classes else []
        self.is_active = is_active
        self.theme = theme
        self.setMouseTracking(True)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        if self.is_active:
            # Active workspace highlight
            active_bg = "rgba(137, 180, 250, 0.15)" if self.theme == "dark" else "rgba(30, 102, 245, 0.15)"
            self.setStyleSheet(f"background-color: {active_bg}; border-radius: 5px;")

        self.stack = QStackedWidget()
        
        # Display Mode
        self.display_widget = QWidget()
        self.display_widget.setStyleSheet("background-color: transparent;")
        self.display_layout = QHBoxLayout(self.display_widget)
        self.display_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icons
        if not self.app_classes:
            self.app_classes = ["application-x-executable"]

        for app_class in self.app_classes[:5]: # Show max 5 icons
            icon_label = QLabel()
            icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            icon = QIcon.fromTheme(app_class)
            
            if icon.isNull():
                # Fallback to a solid black 20x20 placeholder
                pixmap = QPixmap(20, 20)
                pixmap.fill(Qt.black)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setPixmap(icon.pixmap(20, 20))
                
            self.display_layout.addWidget(icon_label)

        self.label = QLabel(self.display_name)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        text_color = "#cdd6f4" if self.theme == "dark" else "#4c4f69"
        self.label.setStyleSheet(f"font-size: 12px; color: {text_color};")
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.display_layout.addWidget(self.label)
        
        # Add stretch here to push the edit button to the right
        self.display_layout.addStretch()
        
        self.edit_btn = QPushButton("✎")
        self.edit_btn.setFixedSize(30, 30)
        # Button style should follow global theme but we can ensure it here if needed
        btn_bg = "#45475a" if self.theme == "dark" else "#bcc0cc"
        self.edit_btn.setStyleSheet(f"background-color: {btn_bg}; color: {text_color}; border-radius: 5px;")
        self.edit_btn.clicked.connect(self.enter_edit_mode)
        self.display_layout.addWidget(self.edit_btn)
        
        self.stack.addWidget(self.display_widget)
        
        # Edit Mode
        self.edit_widget = QWidget()
        self.edit_layout = QHBoxLayout(self.edit_widget)
        self.edit_layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit(self.display_name)
        self.line_edit.returnPressed.connect(self.save_name)
        self.edit_layout.addWidget(self.line_edit)
        
        self.edit_layout.addStretch()
        
        self.save_btn = QPushButton("✓")
        self.save_btn.setFixedSize(30, 30)
        self.save_btn.clicked.connect(self.save_name)
        self.edit_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(30, 30)
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.edit_layout.addWidget(self.cancel_btn)
        
        self.stack.addWidget(self.edit_widget)
        
        self.layout.addWidget(self.stack)

    def enter_edit_mode(self):
        self.line_edit.setText(self.display_name)
        self.stack.setCurrentIndex(1)
        self.line_edit.setFocus()
        self.editing_started.emit()

    def save_name(self):
        new_name = self.line_edit.text().strip()
        if new_name:
            self.display_name = new_name
            self.label.setText(new_name)
            self.renamed.emit(self.ws_id, new_name)
        self.stack.setCurrentIndex(0)
        self.editing_finished.emit()

    def cancel_edit(self):
        self.stack.setCurrentIndex(0)
        self.editing_finished.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.ws_id)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Limit label width to 80% of container to prevent pushing buttons out
        if hasattr(self, 'label'):
            max_w = int(self.width() * 0.8)
            self.label.setMaximumWidth(max_w)
