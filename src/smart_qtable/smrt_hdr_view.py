from PyQt6 import QtCore, QtWidgets, QtGui
from smart_resources import smrt_resources

class ExcelHeaderView(QtWidgets.QHeaderView):

    clicked = QtCore.pyqtSignal(int)

    _x_offset = 3
    _y_offset = 0  # This value is calculated later, based on the height of the paint rect
    _width = 20
    _height = 20

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self.setSectionsClickable(True)
        sections_moveable = kwargs.get('sections_moveable', False)
        self.setSectionsMovable(sections_moveable)

        self._hdr_icons: dict[int, str] = {}
        self._btns_enabled = True
        self._hdr_state: QtCore.QByteArray = None

    def set_default_hdr_state(self):
        self._hdr_state = self.saveState()

    def reset_hdr_state(self):
        if self._hdr_state:
            self.restoreState(self._hdr_state)

    def set_column_icon(self, logical_index: int, icon_path: str):
        self._hdr_icons[logical_index] = icon_path

    def reset_column_icons(self):
        self._hdr_icons.clear()
        self.update()

    def paintSection(self, painter: QtGui.QPainter, rect: QtCore.QRect, logicalIndex: int) -> None:
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2)

        option = QtWidgets.QStyleOptionButton()
        option.rect = QtCore.QRect(rect.x() + rect.width() - self._x_offset - self._width,
                                   rect.y() + self._y_offset, self._width, self._height)

        option.state = QtWidgets.QStyle.StateFlag.State_Enabled | QtWidgets.QStyle.StateFlag.State_Active

        if logicalIndex in self._hdr_icons:
            option.icon = QtGui.QIcon(self._hdr_icons[logicalIndex])
        else:
            option.icon = QtGui.QIcon(':/menu_down.PNG')
        option.iconSize = QtCore.QSize(20, 20)
        painter.save()
        self.style().drawControl(QtWidgets.QStyle.ControlElement.CE_PushButton, option, painter)
        painter.restore()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        index = self.logicalIndexAt(e.pos())
        if 0 <= index < self.count():
            x = self.sectionViewportPosition(index)
            cell_width = self.sectionSize(index)
            if x + cell_width - self._x_offset - self._width < e.pos().x() < x + cell_width - self._x_offset and \
                    self._y_offset < e.pos().y() < self._y_offset + self._height:
                if self._btns_enabled:
                    self.clicked.emit(index)
                    self.viewport().update()
            else:
                super().mousePressEvent(e)
        else:
            super().mousePressEvent(e)

