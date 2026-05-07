from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
from PySide6.QtCore import Signal, Qt

class WorkspaceItem(QWidget):
    clicked = Signal(int)
    renamed = Signal(int, str)
    editing_started = Signal()
    editing_finished = Signal()

    def __init__(self, ws_id, display_name, parent=None):
        super().__init__(parent)
        self.ws_id = ws_id
        self.display_name = display_name
        self.setMouseTracking(True)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.stack = QStackedWidget()

        # Display Mode
        self.display_widget = QWidget()
        self.display_widget.setStyleSheet("background-color: transparent;")
        self.display_widget.setMouseTracking(True)
        self.display_layout = QHBoxLayout(self.display_widget)
        self.display_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self.display_name)
        self.label.setStyleSheet("font-size: 12px; color: #cdd6f4;")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.label.setMouseTracking(True)
        self.display_layout.addWidget(self.label)

        self.edit_btn = QPushButton("✎")
        self.edit_btn.setFixedSize(30, 30)
        self.edit_btn.setStyleSheet("background-color: #45475a; color: #cdd6f4; border-radius: 5px;")
        self.edit_btn.clicked.connect(self.enter_edit_mode)
        self.edit_btn.setMouseTracking(True)
        # self.edit_btn.hide() 
        self.display_layout.addWidget(self.edit_btn)

        self.stack.addWidget(self.display_widget)

        
        # Edit Mode
        self.edit_widget = QWidget()
        self.edit_layout = QHBoxLayout(self.edit_widget)
        self.edit_layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit(self.display_name)
        self.line_edit.returnPressed.connect(self.save_name)
        self.edit_layout.addWidget(self.line_edit)
        
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

    def show_edit_btn(self):
        self.edit_btn.setVisible(True)
        self.update()

    def hide_edit_btn(self):
        self.edit_btn.setVisible(False)
        self.update()
