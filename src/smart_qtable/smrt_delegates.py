import typing
import dataclasses
import logging

from PyQt6 import QtGui, QtCore, QtWidgets

from smart_qtable import smrt_consts
from smart_qtable import smrt_data_model


class CircleStatusDelegate(QtWidgets.QStyledItemDelegate):

    CIRCLE_SIZE = 10

    def paint(self, painter, option, index):

        # get the correct color from the 'status role'
        painter.save()
        status = index.data(role=smrt_consts.ACTION_STATUS_ROLE)
        if status:
            color = smrt_consts.ACTION_STATUS_COLORS[status]
            painter.setBrush(color)
            painter.drawEllipse(option.rect.center(), self.CIRCLE_SIZE, self.CIRCLE_SIZE)

        painter.restore()


class ProgressDelegate(QtWidgets.QStyledItemDelegate):

    PIXEL_BUFFER = 4

    def paint(self, painter, option, index):

        # get the color from the status role
        status = index.data(role=smrt_consts.ACTION_STATUS_ROLE)
        if not status:
            color ='#2dccff'
        else:
            color = smrt_consts.ACTION_STATUS_COLORS[status]
            color = color.name()

        # draw the progress bar
        progress = index.data(role=smrt_consts.ACTION_PROGRESS_ROLE)
        if progress is not None:
            progressBar = QtWidgets.QProgressBar()
            progressBar.setMinimum(0)
            progressBar.setMaximum(100)
            progressBar.setValue(progress)
            progressBar.setFormat('%p%')
            progressBar.setTextVisible(True)
            progressBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            style = "QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; margin-right: 0.2em;}"
            style += f"QProgressBar::chunk {{ background-color: {color}; width: 20px; }}"
            progressBar.setStyleSheet(style)
            progressBar.resize(option.rect.width() - (2 * self.PIXEL_BUFFER), option.rect.height() - (2 * self.PIXEL_BUFFER))
            painter.save()
            painter.translate(option.rect.x() + self.PIXEL_BUFFER, option.rect.y() + self.PIXEL_BUFFER)
            progressBar.render(painter)
            painter.restore()


class ButtonDelegate(QtWidgets.QStyledItemDelegate):

    signal_apply = QtCore.pyqtSignal(QtCore.QModelIndex)
    signal_cancel = QtCore.pyqtSignal(QtCore.QModelIndex)
    PIXEL_BUFFER = 4

    def __init__(self):
        super().__init__(parent=None)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        if index.data(role=smrt_consts.ACTION_PENDING_ROLE):
            # option.backgroundBrush = QtGui.QBrush(QtCore.Qt.GlobalColor.transparent)
            status = index.data(role=smrt_consts.ACTION_STATUS_ROLE)
            if status == smrt_consts.ActionStatus.PENDING:
                apply_btn_rect = QtCore.QRect(
                    option.rect.x() + self.PIXEL_BUFFER,
                    option.rect.y() + self.PIXEL_BUFFER,
                    (option.rect.width() / 2) - (2 * self.PIXEL_BUFFER),
                    option.rect.height() - (2 + self.PIXEL_BUFFER)
                )
                apply_btn = QtWidgets.QPushButton()
                apply_btn.setText('Apply')
                apply_btn.setStyleSheet(
                    "QPushButton {background-color: #9ea7ad; color: black; border-radius: 7px; font-size: 10px; padding: 2px;}")
                apply_btn.resize(apply_btn_rect.width(), apply_btn_rect.height())
                painter.save()
                painter.translate(apply_btn_rect.x(), apply_btn_rect.y())
                apply_btn.render(painter, QtCore.QPoint(), QtGui.QRegion(), QtWidgets.QWidget.RenderFlag.DrawChildren)
                painter.restore()
            if status == smrt_consts.ActionStatus.PENDING or status == smrt_consts.ActionStatus.IN_PROGRESS:
                cancel_btn_rect = QtCore.QRect(
                    option.rect.center().x() + self.PIXEL_BUFFER,
                    option.rect.y() + self.PIXEL_BUFFER,
                    (option.rect.width() / 2) - (2 * self.PIXEL_BUFFER),
                    option.rect.height() - (2 + self.PIXEL_BUFFER)
                )
                cancel_btn = QtWidgets.QPushButton()
                if status == smrt_consts.ActionStatus.IN_PROGRESS:
                    cancel_btn.setText('Abort')
                else:
                    cancel_btn.setText('Cancel')
                cancel_btn.setStyleSheet(
                    "QPushButton {background-color: #9ea7ad; color: black; border-radius: 7px; font-size: 10px; padding: 2px;}")
                cancel_btn.resize(cancel_btn_rect.width(), cancel_btn_rect.height())
                painter.save()
                painter.translate(cancel_btn_rect.x(), cancel_btn_rect.y())
                cancel_btn.render(painter, QtCore.QPoint(), QtGui.QRegion(), QtWidgets.QWidget.RenderFlag.DrawChildren)
                painter.restore()


    def createEditor(self, parent, option, index):
        editor = QtWidgets.QWidget(parent)
        editor.setGeometry(option.rect)
        return editor

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            status = index.data(role=smrt_consts.ACTION_STATUS_ROLE)
            if status == smrt_consts.ActionStatus.PENDING:
                apply_btn_rect = QtCore.QRect(
                    option.rect.x() + self.PIXEL_BUFFER,
                    option.rect.y() + self.PIXEL_BUFFER,
                    (option.rect.width() / 2) - (2 * self.PIXEL_BUFFER),
                    option.rect.height() - (2 + self.PIXEL_BUFFER)
                )

                if apply_btn_rect.contains(event.pos()):
                    self.signal_apply.emit(index)
                    return True
            if status == smrt_consts.ActionStatus.PENDING or status == smrt_consts.ActionStatus.IN_PROGRESS:
                cancel_btn_rect = QtCore.QRect(
                    option.rect.center().x() + self.PIXEL_BUFFER,
                    option.rect.y() + self.PIXEL_BUFFER,
                    (option.rect.width() / 2) - (2 * self.PIXEL_BUFFER),
                    option.rect.height() - (2 + self.PIXEL_BUFFER)
                )

                if cancel_btn_rect.contains(event.pos()):
                    self.signal_cancel.emit(index)
                    return True
            return False

        return False


@dataclasses.dataclass
class ComboBoxItem:

    text: str
    user_data: typing.Any = None
    icon: QtGui.QIcon = None


class SmartComboBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        item_list: list[ComboBoxItem] = kwargs.get('item_list', None)
        if item_list is None:
            self.item_list: list[ComboBoxItem] = []
        else:
            self.item_list: list[ComboBoxItem] = item_list
        self.user_data: bool = kwargs.get('user_data', False)
        self.data_role: QtCore.Qt.ItemDataRole = kwargs.get('data_role', QtCore.Qt.ItemDataRole.EditRole)

    def add_item_to_list(self, item: ComboBoxItem):
        if item is not None:
            self.item_list.append(item)

    def clear_item_list(self):
        self.item_list.clear()

    def set_item_list(self, item_list: list[ComboBoxItem]):
        self.item_list = item_list

    def createEditor(self, parent: QtWidgets.QComboBox, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor = QtWidgets.QComboBox(parent)
        editor.setFrame(False)
        
        item: ComboBoxItem
        for idx, item in enumerate(self.item_list):
            editor.addItem(item.text, item.user_data)
            if item.icon is not None:
                editor.setItemIcon(idx, item.icon)
            
        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        editor.setCurrentText(value)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def setModelData(self, editor: QtWidgets.QComboBox, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        if self.user_data:
            value = editor.currentData()
        else:
            value = editor.currentText()
        model.setData(index, value, self.data_role)


class SmartDblSpinBoxDelegate(QtWidgets.QStyledItemDelegate):

    logger = logging.getLogger('smart_qtable.dbl_spn_del')
    DEFAULT_MAX = 99999.9
    DEFAULT_MIN = 0.0

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.controlling_col_name: str = kwargs.get('controlling_col_name', None)
        self.max_value: float = kwargs.get('max_value', SmartDblSpinBoxDelegate.DEFAULT_MAX)
        self.min_value: float = kwargs.get('min_value', SmartDblSpinBoxDelegate.DEFAULT_MIN)

    @property
    def controlling_col_name(self) -> str:
        return self.__controlling_col_name

    @controlling_col_name.setter
    def controlling_col_name(self, name: str) -> None:
        self.__controlling_col_name = name

    @property
    def max_value(self) -> float:
        return self.__max_value

    @max_value.setter
    def max_value(self, val: float) -> None:
        if not isinstance(val, float) or val < 0:
            self.__max_value = SmartDblSpinBoxDelegate.DEFAULT_MAX
            return
        self.__max_value = val

    @property
    def min_value(self) -> float:
        return self.__min_value

    @min_value.setter
    def min_value(self, val: float) -> None:
        if not isinstance(val, float) or val > self.__max_value:
            self.__min_value = SmartDblSpinBoxDelegate.DEFAULT_MIN
            return
        self.__min_value = val

    def createEditor(self, parent: QtWidgets.QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        item_model: smrt_data_model.SmartDataModel = index.model()
        
        editor = QtWidgets.QDoubleSpinBox(parent)
        editor.setMinimum(self.min_value)
        max_val = self.max_value
        if self.controlling_col_name is not None:
            sibling_col_num = item_model.column_num_from_name(self.controlling_col_name)
            sibling_model_index = index.siblingAtColumn(sibling_col_num)
            max_val = item_model.data(sibling_model_index, QtCore.Qt.ItemDataRole.EditRole)
            if max_val is not None:
                try:
                    max_val = float(max_val)
                except ValueError:
                    max_val = self.max_value
                    self.logger.warning('The spinbox delegate had issues setting a maximum for the table')
            else:
                self.logger.warning('The spinbox delegate had issues setting a maximum for the table')
                max_val = self.max_value
        editor.setMaximum(max_val)
        editor.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        return editor

    def setEditorData(self, editor: QtWidgets.QDoubleSpinBox, index: QtCore.QModelIndex) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        editor.setValue(value)

    def updateEditorGeometry(self, editor: QtWidgets.QDoubleSpinBox, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def setModelData(self, editor: QtWidgets.QDoubleSpinBox, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, QtCore.Qt.ItemDataRole.EditRole)


class SmartSpinBoxDelegate(QtWidgets.QStyledItemDelegate):

    logger = logging.getLogger('smart_qtable.spn_del')
    DEFAULT_MAX = 99999
    DEFAULT_MIN = 0

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.controlling_col_name: str = kwargs.get('controlling_col_name', None)
        self.max_value: int = kwargs.get('max_value', SmartSpinBoxDelegate.DEFAULT_MAX)
        self.min_value: int = kwargs.get('min_value', SmartSpinBoxDelegate.DEFAULT_MIN)

    @property
    def controlling_col_name(self) -> str:
        return self.__controlling_col_name

    @controlling_col_name.setter
    def controlling_col_name(self, name: str) -> None:
        self.__controlling_col_name = name

    @property
    def max_value(self) -> int:
        return self.__max_value

    @max_value.setter
    def max_value(self, val: int) -> None:
        if not isinstance(val, int) or val < 0:
            self.__max_value = SmartSpinBoxDelegate.DEFAULT_MAX
            return
        self.__max_value = val

    @property
    def min_value(self) -> int:
        return self.__min_value

    @min_value.setter
    def min_value(self, val: int) -> None:
        if not isinstance(val, int) or val > self.__max_value:
            self.__min_value = SmartSpinBoxDelegate.DEFAULT_MIN
            return
        self.__min_value = val

    def createEditor(self, parent: QtWidgets.QWidget, option: 'QStyleOptionViewItem',
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        item_model: smrt_data_model.SmartDataModel = index.model()

        editor = QtWidgets.QSpinBox(parent)
        editor.setMinimum(self.min_value)
        max_val = self.max_value
        if self.controlling_col_name is not None:
            sibling_col_num = item_model.column_num_from_name(self.controlling_col_name)
            if sibling_col_num == -1:
                max_val = self.max_value
            else:
                sibling_model_index = index.siblingAtColumn(sibling_col_num)
                max_val = item_model.data(sibling_model_index, QtCore.Qt.ItemDataRole.EditRole)
                if max_val is not None:
                    try:
                        max_val = int(max_val)
                    except ValueError:
                        max_val = self.max_value
                        self.logger.warning('The spinbox delegate had issues setting a maximum for the table')
                else:
                    self.logger.warning('The spinbox delegate had issues setting a maximum for the table')
                    max_val = self.max_value
        editor.setMaximum(max_val)
        editor.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        return editor

    def setEditorData(self, editor: QtWidgets.QSpinBox, index: QtCore.QModelIndex) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        editor.setValue(value)

    def updateEditorGeometry(self, editor: QtWidgets.QDoubleSpinBox, option: 'QStyleOptionViewItem',
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def setModelData(self, editor: QtWidgets.QDoubleSpinBox, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, QtCore.Qt.ItemDataRole.EditRole)


class SmartLineEditDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.valid_entries: list[str] = kwargs.get('valid_entries', None)
        if self.valid_entries is None:
            self.valid_entries = []
        self.limit_to_valid_entries: bool = kwargs.get('limit_to_valid_entries', False)
        self.all_caps: bool = kwargs.get('all_caps', False)
        self.is_editing = False
        self.editor_object = None

    def createEditor(self, parent: QtWidgets.QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor = QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)
        editor.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.editor_object = editor
        return editor

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        if self.valid_entries is not None and editor.text() not in self.valid_entries and self.limit_to_valid_entries:
            msgbx = QtWidgets.QMessageBox(self.parent())
            msgbx.setText('Not a valid entry')
            msgbx.exec()
        else:
            if self.all_caps:
                model.setData(index, editor.text().upper(), QtCore.Qt.ItemDataRole.EditRole)
            else:
                model.setData(index, editor.text(), QtCore.Qt.ItemDataRole.EditRole)
        self.is_editing = False

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        self.is_editing = True
        value = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        if self.valid_entries is not None and self.valid_entries:
            my_completer = QtWidgets.QCompleter(self.valid_entries)
            my_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
            editor.setCompleter(my_completer)
        editor.setText(value)

    @property
    def is_editing(self):
        return self.__is_editing

    @is_editing.setter
    def is_editing(self, value: bool):
        self.__is_editing = value
