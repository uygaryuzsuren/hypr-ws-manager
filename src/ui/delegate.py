from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionButton, QApplication
from PySide6.QtCore import Signal, QObject, Qt, QRect, QEvent, QSize
from PySide6.QtGui import QPainter

class WorkspaceDelegate(QStyledItemDelegate):
    edit_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_rect = QRect()
        self.hovered_index = -1

    def set_hovered_index(self, index):
        if self.hovered_index != index:
            self.hovered_index = index
            return True # Indicates state change
        return False

    def paint(self, painter, option, index):
        # Adjust rect for spacing
        rect = option.rect.adjusted(0, 5, 0, -5)

        # Draw the workspace name
        text = index.data(Qt.DisplayRole)
        painter.drawText(rect.adjusted(10, 0, -60, 0), Qt.AlignVCenter, text)

        # DEBUG: Unconditionally draw the "Edit" button
        self.button_rect = QRect(rect.right() - 60, rect.top() + 2, 55, 25)

        # Fill the button area with a color to see if it renders
        painter.fillRect(self.button_rect, Qt.red)
        painter.setPen(Qt.white)
        painter.drawText(self.button_rect, Qt.AlignCenter, "Edit")


    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return size + QSize(0, 10) # Add vertical padding

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if self.button_rect.contains(event.pos()):
                # Get the ws_id from the data
                ws_id = int(index.data(Qt.UserRole) or index.row() + 1)
                self.edit_requested.emit(ws_id)
                return True
        return super().editorEvent(event, model, option, index)
