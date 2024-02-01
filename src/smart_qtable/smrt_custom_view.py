from PyQt6 import QtGui, QtCore, QtWidgets
# from smart_qtable import theme_resources

import enum
import uuid

from smart_qtable import smrt_tbl_view
from frameless_dialog import frmls_dialog
from smart_resources import smrt_resources
from smart_qtable import smrt_consts


class BaseColumnWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.id: uuid.UUID = uuid.uuid4()


class IndicatorWidget(BaseColumnWidget):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_widget()

    def setup_widget(self):
        widget_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(widget_layout)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.frm_line = QtWidgets.QFrame(self)
        self.frm_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.frm_line.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.frm_line.setLineWidth(20)
        self.frm_line.setStyleSheet('QFrame {border: 20px solid blue}')
        self.layout().addWidget(self.frm_line)
        self.setFixedHeight(10)

class ColumnWidget(BaseColumnWidget):

    class WidgetMode(enum.IntEnum):

        ADD = 0
        REMOVE = 1

    signal_btn = QtCore.pyqtSignal(BaseColumnWidget)
    signal_move_up = QtCore.pyqtSignal(BaseColumnWidget)
    signal_move_down = QtCore.pyqtSignal(BaseColumnWidget)
    signal_widget_being_dragged = QtCore.pyqtSignal(BaseColumnWidget)
    signal_drag_cancelled = QtCore.pyqtSignal(BaseColumnWidget)
    signal_drag_hovering = QtCore.pyqtSignal(BaseColumnWidget)
    signal_drag_enter = QtCore.pyqtSignal(BaseColumnWidget, bool)
    signal_widget_dropped_other_list = QtCore.pyqtSignal(BaseColumnWidget, BaseColumnWidget)
    signal_widget_dropped_same_list = QtCore.pyqtSignal(BaseColumnWidget, BaseColumnWidget)
    signal_drag_leave = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)

        self.mode: ColumnWidget.WidgetMode = kwargs.get('mode', ColumnWidget.WidgetMode.ADD)
        self.col_name: str = kwargs.get('col_name', '')

        self.setup_ui()
        self.dragStartPosition: QtCore.QPoint = None
        self.setAcceptDrops(True)

        self.btn_add_remove.clicked.connect(lambda: self.signal_btn.emit(self))
        self.btn_move_up.clicked.connect(lambda: self.signal_move_up.emit(self))
        self.btn_move_down.clicked.connect(lambda: self.signal_move_down.emit(self))
        if self.mode == ColumnWidget.WidgetMode.REMOVE:
            self.frm_move_btns.setVisible(False)
        self.drag_direction_up = False
        self.prev_drag_pos_y = 0
        self.drag_move_count = 0

    def copy(self):
        new_widget = ColumnWidget(parent=self.parent(), mode=self.mode, col_name=self.col_name)

        new_widget.id = self.id
        new_widget.dragStartPosition = self.dragStartPosition
        new_widget.drag_direction_up = self.drag_direction_up
        new_widget.prev_drag_pos_y = self.prev_drag_pos_y
        new_widget.drag_move_count = self.drag_move_count

        return new_widget


    def set_mode(self, mode: WidgetMode):
        self.mode: ColumnWidget.WidgetMode = mode
        if self.mode == ColumnWidget.WidgetMode.REMOVE:
            self.frm_move_btns.setVisible(False)
            icon = QtGui.QIcon(':add_item_icon.png')
        else:
            self.frm_move_btns.setVisible(True)
            icon = QtGui.QIcon(':remove_item_icon.png')
        self.btn_add_remove.setIcon(icon)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.pos()
        # super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not (event.buttons() & QtCore.Qt.MouseButton.LeftButton) or self.dragStartPosition is None:
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return
        drag = QtGui.QDrag(self)
        mimeData = QtCore.QMimeData()
        dragPixmap = self.grab()

        drag.setMimeData(mimeData)
        drag.setPixmap(dragPixmap)
        drag.setHotSpot(event.pos())

        # self.setEnabled(False)
        self.signal_widget_being_dragged.emit(self)
        ret = drag.exec(QtCore.Qt.DropAction.MoveAction)
        if ret == QtCore.Qt.DropAction.IgnoreAction:
            self.signal_drag_cancelled.emit(self)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if type(event.source()) != ColumnWidget:
            event.ignore()
            return
        if event.source() == self:
            event.ignore()
            return
        # determine if the 'enter' event occurred in the top or bottom half of the widget
        half_height = self.height() / 2
        if event.position().y() < half_height:
            top_half = True
        else:
            top_half = False
        self.prev_drag_pos_y = event.position().y()

        # curr_pos_y = event.position().y()
        # self.drag_direction_up = (self.prev_drag_pos_y - curr_pos_y) > 0
        self.signal_drag_enter.emit(self, top_half)
        # self.prev_drag_pos_y = curr_pos_y
        event.accept()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.signal_drag_leave.emit()
        self.drag_move_count = 0
        return

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        # if self.parent() == event.source().parent():
        self.signal_drag_hovering.emit(self)
        self.drag_move_count += 1
        if self.drag_move_count < smrt_consts.DRAG_MOVE_SENSITIVITY:
            return
        self.drag_move_count = 0
        curr_pos_y = event.position().y()
        drag_up = (self.prev_drag_pos_y - curr_pos_y) > 0
        self.prev_drag_pos_y = curr_pos_y
        if drag_up == self.drag_direction_up:
            return
        self.drag_direction_up = drag_up
        self.signal_drag_enter.emit(self, self.drag_direction_up)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.source() == self or type(event.source()) != ColumnWidget:
            event.ignore()
            return
        if event.source().mode != self.mode:
            self.signal_widget_dropped_other_list.emit(event.source(), self)
        else:
            self.signal_widget_dropped_same_list.emit(event.source(), self)
        event.accept()
        # self.frm_widget.setStyleSheet('')
        # self.signal_move_widget_to_position.emit(event.source().id, self.id)
        # event.accept()

    def setup_ui(self):
        # self.setLayout(None)
        widget_layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(widget_layout)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)

        self.frm_widget = QtWidgets.QFrame()
        self.frm_widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frm_widget.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.frm_layout = QtWidgets.QHBoxLayout(self.frm_widget)
        self.lbl_col_name = QtWidgets.QLabel(self.col_name, self.frm_widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_col_name.setFont(font)
        self.btn_add_remove = QtWidgets.QToolButton(self.frm_widget)
        # self.btn_add_remove.setFixedSize(QtCore.QSize(20, 20))
        # self.btn_add_remove.setStyleSheet('QToolButton {}')
        if self.mode == ColumnWidget.WidgetMode.ADD:
            icon = QtGui.QIcon(':remove_item_icon.png')
        else:
            icon = QtGui.QIcon(':add_item_icon.png')
        self.btn_add_remove.setIcon(icon)
        self.btn_add_remove.setIconSize(QtCore.QSize(10, 10))

        button_style_sheet = "\nQToolButton {\n\nbackground-color:transparent;\nborder:none;\n\n}\n\n"

        self.frm_move_btns = QtWidgets.QFrame(self.frm_widget)
        self.layout_frm_move_btns = QtWidgets.QVBoxLayout(self.frm_move_btns)
        self.layout_frm_move_btns.setSpacing(0)
        self.layout_frm_move_btns.setContentsMargins(0, 0, 0, 0)
        self.frm_move_btns.setFixedSize(QtCore.QSize(15, 15))
        self.btn_move_up = QtWidgets.QToolButton(self.frm_move_btns)
        self.btn_move_up.setIconSize(QtCore.QSize(5, 5))
        # self.btn_move_up.setFixedHeight(10)
        # self.btn_move_up.setIcon(QtGui.QIcon('resources/move_up_standard.png'))
        self.btn_move_up.setStyleSheet(
            'QToolButton {image: url(:move_up_standard.png);} '
            'QToolButton:hover {image: url(:move_up_hover.png);} '
            'QToolButton:pressed {image: url(:move_up_clicked.png);}'
        )
        self.layout_frm_move_btns.addWidget(self.btn_move_up)
        spcr2 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.layout_frm_move_btns.addItem(spcr2)
        self.btn_move_down = QtWidgets.QToolButton(self.frm_move_btns)
        self.btn_move_down.setIconSize(QtCore.QSize(5, 5))
        # self.btn_move_down.setFixedHeight(10)
        # self.btn_move_down.setIcon(QtGui.QIcon('resources/move_down_standard.png'))
        self.btn_move_down.setStyleSheet(
            'QToolButton {image: url(:move_down_standard.png);} '
            'QToolButton:hover {image: url(:move_down_hover.png);} '
            'QToolButton:pressed {image: url(:move_down_clicked.png);}'
        )
        self.layout_frm_move_btns.addWidget(self.btn_move_down)

        self.frm_layout.addWidget(self.lbl_col_name)
        spcr = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.frm_layout.addItem(spcr)
        self.frm_layout.addWidget(self.btn_add_remove)
        self.frm_layout.addWidget(self.frm_move_btns)
        self.layout().addWidget(self.frm_widget)
        self.setMinimumHeight(40)
        self.frm_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.frm_move_btns.setStyleSheet(button_style_sheet)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)


class SortedVBoxLayout(QtWidgets.QVBoxLayout):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

    def sorted_insert_widget(self, widget: ColumnWidget):
        for i in range(self.count() - 1):
            col_name = self.itemAt(i).widget().col_name
            if widget.col_name < col_name:
                self.insertWidget(i, widget)
                return
        self.insertWidget(self.count() - 1, widget)


class SmartCentralWidget(QtWidgets.QWidget):

    signal_drag_enter_cw = QtCore.pyqtSignal(ColumnWidget)
    signal_drag_move_cw = QtCore.pyqtSignal(ColumnWidget)
    signal_drag_leave_cw = QtCore.pyqtSignal()
    signal_drop_cw = QtCore.pyqtSignal(ColumnWidget)

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setStyleSheet('QWidget {background: #18191a}')

    def paintEvent(self, pe):

        o = QtWidgets.QStyleOption()
        o.initFrom(self)
        p = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_Widget, o, p, self)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if type(event.source()) != ColumnWidget:
            event.ignore()
            return
        self.signal_drag_enter_cw.emit(event.source())
        event.accept()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        self.signal_drag_move_cw.emit(event.source())

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.signal_drag_leave_cw.emit()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if type(event.source()) != ColumnWidget:
            event.ignore()
            return
        self.signal_drop_cw.emit(event.source())
        event.setDropAction(QtCore.Qt.DropAction.MoveAction)
        event.accept()


class SmartCustomizationDialog(frmls_dialog.FramelessDialog):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.tbl_name = kwargs.get('tbl_name', None)
        self.setup_dialog_ui()

        self.list_visible.signal_widget_pass_off.connect(self.list_unused.add_widget)
        self.list_unused.signal_widget_pass_off.connect(self.list_visible.add_widget)
        self.list_visible.signal_widget_drop_other_list_success.connect(self.list_unused.delete_dragged_widget)
        self.list_unused.signal_widget_drop_other_list_success.connect(self.list_visible.delete_dragged_widget)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)

    def setup_dialog_ui(self):
        self.setWindowIcon(QtGui.QIcon(':ConMedSwoosh.png'))
        self.setWindowTitle('Customize view')
        self.cw = QtWidgets.QWidget(self)
        self.set_central_widget(self.cw)
        self.resize(800, 900)
        self.layout_dialog = QtWidgets.QVBoxLayout(self.cw)
        self.layout_dialog.setContentsMargins(5, 5, 5, 5)
        self.layout_dialog.setSpacing(3)

        font = QtGui.QFont()
        font.setPointSize(22)
        font2 = QtGui.QFont()
        font2.setPointSize(18)
        self.lbl_table_name = QtWidgets.QLabel(self.cw)
        self.lbl_table_name.setFont(font)
        if self.tbl_name:
            self.lbl_table_name.setText(f'Customize the columns and ordering for {self.tbl_name}')
        else:
            self.lbl_table_name.setText(f'Customize the columns and ordering')
        self.layout_dialog.addWidget(self.lbl_table_name)

        self.frm_scroll_areas = QtWidgets.QFrame(self.cw)
        self.layout_frm_scroll_areas = QtWidgets.QHBoxLayout(self.frm_scroll_areas)

        self.frm_unused = QtWidgets.QFrame(self.frm_scroll_areas)
        # self.frm_unused.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.layout_frm_unused = QtWidgets.QVBoxLayout(self.frm_unused)
        self.lbl_unused = QtWidgets.QLabel('Ununused columns', self.frm_unused)
        self.lbl_unused.setFont(font2)
        self.layout_frm_unused.addWidget(self.lbl_unused)
        self.list_unused = ColumnWidgetList(parent=self.frm_unused, list_mode=ColumnWidgetList.ListMode.SORTED)

        self.layout_frm_unused.addWidget(self.list_unused)

        self.frm_visible = QtWidgets.QFrame(self.frm_scroll_areas)
        self.layout_frm_visible = QtWidgets.QVBoxLayout(self.frm_visible)
        self.lbl_visible = QtWidgets.QLabel('Visible columns', self.frm_visible)
        self.lbl_visible.setFont(font2)
        self.layout_frm_visible.addWidget(self.lbl_visible)
        self.list_visible = ColumnWidgetList(parent=self.frm_visible, list_mode=ColumnWidgetList.ListMode.ORDERED)
        self.layout_frm_visible.addWidget(self.list_visible)

        self.layout_frm_scroll_areas.addWidget(self.frm_unused)
        self.layout_frm_scroll_areas.addWidget(self.frm_visible)

        self.layout_dialog.addWidget(self.frm_scroll_areas)

        self.btn_box = QtWidgets.QDialogButtonBox(self.cw)
        self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.layout_dialog.addWidget(self.btn_box)
        self.cw.setLayout(self.layout_dialog)

    def set_window_data(self, curr_view: smrt_tbl_view.SmartTableView):
        self.list_visible.clear_all_widgets()
        self.list_unused.clear_all_widgets()
        for col in curr_view.hidden_cols:
            widget = ColumnWidget(col_name=col, mode=ColumnWidget.WidgetMode.REMOVE)
            self.list_unused.add_widget(widget)
        for col in curr_view.col_order:
            widget = ColumnWidget(col_name=col, mode=ColumnWidget.WidgetMode.ADD)
            self.list_visible.add_widget(widget)

    def get_view_on_state(self) -> smrt_tbl_view.SmartTableView:
        col_order = self.list_visible.get_all_widget_col_names()
        hidden_cols = self.list_unused.get_all_widget_col_names()
        name = smrt_consts.CUSTOM_VIEW_NAME

        return smrt_tbl_view.SmartTableView(name=name,
                                            hidden_cols=hidden_cols,
                                            col_order=col_order)

    # def set_current_view(self, view: smrt_tbl_view.SmartTableView):
    #     '''
    #     curr_hidden_cols: list of column names currently hidden
    #     curr_visible_order: list with column names in current order
    #     '''
    #     self.list_unused.clear_all_widgets()
    #     self.list_visible.clear_all_widgets()
    #     for col in curr_hidden_cols:
    #         widget = ColumnWidget(col_name=col, mode=ColumnWidget.WidgetMode.REMOVE)
    #         self.list_unused.add_widget(widget)
    #
    #     for col in curr_visible:
    #         widget = ColumnWidget(col_name=col, mode=ColumnWidget.WidgetMode.ADD)
    #         self.list_visible.add_widget(widget)

    def show_window(self):

        # self.list_unused.clear_all_widgets()
        # self.list_visible.clear_all_widgets()
        # for col in curr_hidden_cols:
        #     widget = ColumnWidget(col_name=col, mode=ColumnWidget.WidgetMode.REMOVE)
        #     self.list_unused.add_widget(widget)
        #
        # for col in curr_visible:
        #     widget = ColumnWidget(col_name=col, mode=ColumnWidget.WidgetMode.ADD)
        #     self.list_visible.add_widget(widget)

        return self.exec()


class ColumnWidgetList(QtWidgets.QWidget):

    signal_widget_pass_off = QtCore.pyqtSignal(ColumnWidget)
    signal_widget_drop_other_list_success = QtCore.pyqtSignal()

    class ListMode(enum.IntEnum):

        ORDERED = 0
        SORTED = 1

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_ui()
        # self.resize(1200, 800)

        self.indicator_index = None
        self.dragged_widget_idx: int = None

        self.list_mode: ColumnWidgetList.ListMode = kwargs.get('list_mode', ColumnWidgetList.ListMode.ORDERED)

        self.min_height: int = 2

        self.central_widget.show()
        self.setAcceptDrops(False)

        self.central_widget.signal_drop_cw.connect(self.on_cw_drop_event)
        self.central_widget.signal_drag_leave_cw.connect(self.on_cw_drag_leave_event)


    def setup_ui(self):
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.frm_widget = QtWidgets.QFrame(self)
        self.frm_widget.setObjectName('frm_widget')
        self.frm_widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.layout_frm_widget = QtWidgets.QVBoxLayout(self.frm_widget)
        self.scroll_area = QtWidgets.QScrollArea(self.frm_widget)
        self.layout_frm_widget.addWidget(self.scroll_area)
        self.central_widget = SmartCentralWidget(parent=self.frm_widget)
        self.central_widget.setObjectName('cw')
        # self.central_widget.setAcceptDrops(True)
        self.central_widget.setLayout(SortedVBoxLayout(parent=self.central_widget))
        self.central_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.central_widget.layout().setSpacing(0)
        self.central_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                          QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        # self.central_widget.setMinimumHeight(400)
        self.scroll_area.setWidget(self.central_widget)
        self.scroll_area.setWidgetResizable(True)

        # self.scroll_area.setBackgroundRole(QtGui.QPalette.ColorRole.Dark)
        self.layout().addWidget(self.frm_widget)

        spcr = QtWidgets.QSpacerItem(10, 2, QtWidgets.QSizePolicy.Policy.Preferred,
                                     QtWidgets.QSizePolicy.Policy.Expanding)
        self.central_widget.layout().addItem(spcr)

    @property
    def num_widgets(self):
        return self.central_widget.layout().count() - 1

    def get_all_widget_col_names(self) -> list[str]:
        if self.num_widgets < 1:
            return []
        names = []
        for i in range(self.num_widgets):
            names.append(self.central_widget.layout().itemAt(i).widget().col_name)
        return names

    @QtCore.pyqtSlot(ColumnWidget)
    def add_widget(self, widget: ColumnWidget):
        # add the widget to the end. The layout index position will be equal to the current number of widgets
        widget.setParent(self.central_widget)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        if self.list_mode == ColumnWidgetList.ListMode.SORTED:
            self.central_widget.layout().sorted_insert_widget(widget)
        else:
            self.central_widget.layout().insertWidget(self.num_widgets, widget)

        # self.central_widget.adjustSize()
        self.min_height += widget.minimumHeight() + 4
        self.central_widget.setMinimumHeight(self.min_height)

        self.connect_signals_for_widget(widget)

        widget.show()

    @QtCore.pyqtSlot()
    def drag_left_widget(self):
        self.hide_insert_indicator()

    def connect_signals_for_widget(self, widget: ColumnWidget):
        widget.signal_btn.connect(self.on_widget_add_remove_btn)
        widget.signal_move_up.connect(self.move_widget_up)
        widget.signal_move_down.connect(self.move_widget_down)
        widget.signal_widget_being_dragged.connect(self.widget_being_dragged)
        widget.signal_drag_cancelled.connect(self.drag_cancelled)
        widget.signal_drag_hovering.connect(self.on_drag_hover)
        widget.signal_drag_enter.connect(self.insert_indicator_at_widget)
        widget.signal_widget_dropped_other_list.connect(self.on_widget_drop_other_list)
        widget.signal_widget_dropped_same_list.connect(self.on_widget_drop_same_list)
        widget.signal_drag_leave.connect(self.drag_left_widget)

    def remove_widget(self, widget: ColumnWidget, **kwargs):
        delete: bool = kwargs.get('delete', False)

        self.central_widget.layout().removeWidget(widget)
        self.min_height -= widget.minimumHeight() - 4
        self.central_widget.setMinimumHeight(self.min_height)
        widget.hide()
        self.disconnect_signals_from_widget(widget)

        widget.setParent(None)
        if delete:
            del widget
            return None

        return widget

    def disconnect_signals_from_widget(self, widget: ColumnWidget):
        widget.signal_btn.disconnect()
        widget.signal_move_up.disconnect()
        widget.signal_move_down.disconnect()
        widget.signal_widget_being_dragged.disconnect()
        widget.signal_drag_cancelled.disconnect()
        widget.signal_drag_hovering.disconnect()
        widget.signal_drag_enter.disconnect()
        widget.signal_widget_dropped_other_list.disconnect()
        widget.signal_widget_dropped_same_list.disconnect()
        widget.signal_drag_leave.disconnect()

    @QtCore.pyqtSlot()
    def delete_dragged_widget(self):
        self.dragged_widget_idx = None

    def on_drag_hover(self, widget: ColumnWidget):
        self.scroll_area.ensureWidgetVisible(widget, 0, 10)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        event.ignore()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        pass

    @QtCore.pyqtSlot()
    def on_cw_drag_leave_event(self):
        self.hide_insert_indicator()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        pass

    @QtCore.pyqtSlot(ColumnWidget)
    def on_cw_drop_event(self, widget: ColumnWidget):
        if self.list_mode == ColumnWidgetList.ListMode.ORDERED:
            widget.set_mode(ColumnWidget.WidgetMode.ADD)
        else:
            widget.set_mode(ColumnWidget.WidgetMode.REMOVE)
        widget.setParent(self.central_widget)
        self.connect_signals_for_widget(widget)
        if self.list_mode == ColumnWidgetList.ListMode.SORTED:
            self.central_widget.layout().sorted_insert_widget(widget)
        else:
            if self.indicator_index is not None:
                self.central_widget.layout().insertWidget(self.indicator_index, widget)
                self.hide_insert_indicator()
            else:
                self.central_widget.layout().insertWidget(self.num_widgets, widget)
        widget.show()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        event.ignore()

    @QtCore.pyqtSlot(ColumnWidget)
    def on_widget_add_remove_btn(self, widget: ColumnWidget):
        self.remove_widget(widget)
        if widget.mode == ColumnWidget.WidgetMode.REMOVE:
            widget.set_mode(ColumnWidget.WidgetMode.ADD)
        else:
            widget.set_mode(ColumnWidget.WidgetMode.REMOVE)
        self.signal_widget_pass_off.emit(widget)

    @QtCore.pyqtSlot(uuid.UUID, uuid.UUID)
    def move_widget_to_position(self, widget_to_move: uuid.UUID, widget_destination: uuid.UUID):
        if widget_to_move not in self.widgets or widget_destination not in self.widgets:
            raise KeyError('One or both of the widget IDs are not in the dictionary')
        current_idx_widget_to_move = self.widgets[widget_to_move]
        current_idx_destination = self.widgets[widget_destination]
        if current_idx_destination > current_idx_widget_to_move:
            current_idx_destination -= 1
        widget_obj = self.central_widget.layout().takeAt(current_idx_widget_to_move).widget()
        self.central_widget.layout().invalidate()
        self.central_widget.layout().insertWidget(current_idx_destination, widget_obj)
        self.central_widget.layout().invalidate()
        self.reset_widget_dict()

    @QtCore.pyqtSlot(ColumnWidget)
    def move_widget_up(self, widget: ColumnWidget):
        widget_idx = self.central_widget.layout().indexOf(widget)
        if widget_idx == 0:
            return
        self.central_widget.layout().removeWidget(widget)
        self.central_widget.layout().insertWidget(widget_idx - 1, widget)

    @QtCore.pyqtSlot(ColumnWidget)
    def move_widget_down(self, widget: ColumnWidget):
        widget_idx = self.central_widget.layout().indexOf(widget)
        if widget_idx == self.num_widgets - 1:
            return
        self.central_widget.layout().removeWidget(widget)
        self.central_widget.layout().insertWidget(widget_idx + 1, widget)

    @QtCore.pyqtSlot(QtWidgets.QWidget, QtWidgets.QWidget)
    def on_widget_drop_other_list(self, widget_being_dropped: QtWidgets.QWidget, widget_dropped_onto: QtWidgets.QWidget):
        if self.indicator_index is not None:
            idx = self.indicator_index
            self.hide_insert_indicator()
            self.central_widget.layout().insertWidget(idx, widget_being_dropped)

        else:
            if self.list_mode == ColumnWidgetList.ListMode.SORTED:
                self.central_widget.layout().sorted_insert_widget(widget_being_dropped)
            else:
                self.central_widget.layout().insertWidget(self.num_widgets - 1, widget_being_dropped)
        if widget_being_dropped.mode == ColumnWidget.WidgetMode.ADD:
            widget_being_dropped.set_mode(ColumnWidget.WidgetMode.REMOVE)
        else:
            widget_being_dropped.set_mode(ColumnWidget.WidgetMode.ADD)
        self.connect_signals_for_widget(widget_being_dropped)
        widget_being_dropped.show()
        self.signal_widget_drop_other_list_success.emit()


    @QtCore.pyqtSlot(QtWidgets.QWidget, QtWidgets.QWidget)
    def on_widget_drop_same_list(self, widget_being_dropped: QtWidgets.QWidget, widget_dropped_onto: QtWidgets.QWidget):
        if self.indicator_index is not None:
            idx = self.indicator_index
            self.hide_insert_indicator()
            self.central_widget.layout().insertWidget(idx, widget_being_dropped)

        else:
            if self.list_mode == ColumnWidgetList.ListMode.SORTED:
                self.central_widget.layout().sorted_insert_widget(widget_being_dropped)
            else:
                self.central_widget.layout().insertWidget(self.num_widgets - 1, widget_being_dropped)
        # if widget_being_dropped.mode == ColumnWidget.WidgetMode.ADD:
        #     widget_being_dropped.set_mode(ColumnWidget.WidgetMode.REMOVE)
        # else:
        #     widget_being_dropped.set_mode(ColumnWidget.WidgetMode.ADD)
        self.connect_signals_for_widget(widget_being_dropped)
        widget_being_dropped.show()

    @QtCore.pyqtSlot(ColumnWidget)
    def widget_being_dragged(self, widget: ColumnWidget):
        self.dragged_widget_idx = self.central_widget.layout().indexOf(widget)
        show_indicator = self.dragged_widget_idx != self.num_widgets - 1
        self.central_widget.layout().removeWidget(widget)
        widget.hide()
        self.disconnect_signals_from_widget(widget)
        widget.setParent(None)
        if self.list_mode == ColumnWidgetList.ListMode.ORDERED and show_indicator:
            self.add_move_insert_indicator(self.dragged_widget_idx)

    @QtCore.pyqtSlot(ColumnWidget)
    def drag_cancelled(self, widget: ColumnWidget):
        if self.indicator_index is not None:
            self.hide_insert_indicator()
        widget.setParent(self.central_widget)
        self.central_widget.layout().insertWidget(self.dragged_widget_idx, widget)
        widget.show()
        self.dragged_widget_idx = None

    @QtCore.pyqtSlot(int)
    def add_move_insert_indicator(self, idx: int):
        if self.indicator_index is not None:
            if idx == self.indicator_index:
                return # do nothing
            ind_widget = self.central_widget.layout().takeAt(self.indicator_index).widget()
            self.central_widget.layout().invalidate()
            self.central_widget.layout().insertWidget(idx, ind_widget)
            self.indicator_index = idx
        else:
            ind_widget = IndicatorWidget(parent=self.central_widget)
            self.central_widget.layout().insertWidget(idx, ind_widget)
            self.indicator_index = idx
            ind_widget.show()

    @QtCore.pyqtSlot()
    def hide_insert_indicator(self):
        if self.indicator_index is not None:
            ind_widget = self.central_widget.layout().takeAt(self.indicator_index).widget()
            ind_widget.hide()
            ind_widget.setParent(None)
            del ind_widget
            self.indicator_index = None

    @QtCore.pyqtSlot(ColumnWidget, bool)
    def insert_indicator_at_widget(self, widget: ColumnWidget, above: bool):
        if self.list_mode == ColumnWidgetList.ListMode.ORDERED:
            widget_idx = self.central_widget.layout().indexOf(widget)
            if self.indicator_index is not None and self.indicator_index < widget_idx:
                widget_idx -= 1
            if above:
                ind_idx = widget_idx
            else:
                ind_idx = widget_idx + 1

            self.add_move_insert_indicator(ind_idx)

    def clear_all_widgets(self):
        for i in reversed(range(self.num_widgets)):
            widget = self.central_widget.layout().takeAt(i).widget()
            widget.hide()
            widget.setParent(None)
            self.disconnect_signals_from_widget(widget)
            del widget


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    file = QtCore.QFile(":/dark-green/stylesheet.qss")
    file.open(QtCore.QFile.OpenModeFlag.ReadOnly | QtCore.QFile.OpenModeFlag.Text)
    stream = QtCore.QTextStream(file)
    app.setStyleSheet(stream.readAll())

    win = SmartCustomizationDialog(parent=None, tbl_name='SKU Table')
    win.show_window(['One', 'Two', 'Four'], ['Three', 'Five'])



    app.quit()

    # wid = ColumnWidget(col_name='Bouncing Boobs')
    # wid.show()
    # list = ColumnWidgetList()
    # item1 = ColumnWidget(col_name='BOOM', mode=ColumnWidget.WidgetMode.REMOVE)
    # item1.btn_add_remove.setStyleSheet('')
    # item2 = ColumnWidget(col_name='JUMP')
    # item3 = ColumnWidget(col_name='PUMP')
    # #
    # list.add_widget(item1)
    # list.add_widget(item2)
    # list.add_widget(item3)
    # list.add_spcr()
    # list.show()


    sys.exit(app.exec())

