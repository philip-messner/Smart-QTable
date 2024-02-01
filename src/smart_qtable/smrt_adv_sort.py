from PyQt6 import QtCore, QtGui, QtWidgets

import typing

from frameless_dialog import frmls_dialog, frmls_msgbx
from smart_qtable import smrt_consts


class AdvSortCboDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.col_list: list[str] = []

    def update_col_list(self, col_list: list[str]):
        self.col_list = col_list

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor = QtWidgets.QComboBox(parent=parent)
        editor.setFrame(False)

        cbo_type = index.data(role=smrt_consts.CBO_TYPE_ROLE)
        if cbo_type == smrt_consts.ADV_SORT_COL_NAME_VALUE:
            col_list: list[str] = index.data(role=smrt_consts.CBO_COL_LIST_ROLE)
            current_value: str = index.data()
            if current_value != smrt_consts.ADV_SORT_NO_SELECT_FLAG:
                editor.addItem(current_value, current_value)
            for entry in col_list:
                editor.addItem(entry, entry)
        elif cbo_type == smrt_consts.ADV_SORT_SORT_ORD_VALUE:
            dtype = index.data(role=smrt_consts.DTYPE_QUERY_ROLE)
            if dtype == smrt_consts.SmartDataTypes.DATE or dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                editor.addItem('Oldest to Newest', QtCore.Qt.SortOrder.AscendingOrder)
                editor.addItem('Newest to Oldest', QtCore.Qt.SortOrder.DescendingOrder)
            elif dtype == smrt_consts.SmartDataTypes.INT or dtype == smrt_consts.SmartDataTypes.FLOAT or dtype == smrt_consts.SmartDataTypes.ACCT:
                editor.addItem('Smallest to Largest', QtCore.Qt.SortOrder.AscendingOrder)
                editor.addItem('Largest to Smallest', QtCore.Qt.SortOrder.DescendingOrder)
            else:
                editor.addItem('Sort A to Z', QtCore.Qt.SortOrder.AscendingOrder)
                editor.addItem('Sort Z to A', QtCore.Qt.SortOrder.DescendingOrder)
        # editor.currentTextChanged.connect(lambda: self.endEditing(editor))
        return editor

    @QtCore.pyqtSlot(QtWidgets.QComboBox)
    def endEditing(self, editor: QtWidgets.QWidget):
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.EndEditHint.NoHint)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:

        editor.setGeometry(option.rect)

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        editor: QtWidgets.QComboBox
        value = index.data(role=QtCore.Qt.ItemDataRole.EditRole)
        cbo_type = index.data(role=smrt_consts.CBO_TYPE_ROLE)
        if cbo_type == smrt_consts.ADV_SORT_COL_NAME_VALUE:
            if value == smrt_consts.ADV_SORT_NO_SELECT_FLAG:
                editor.setCurrentIndex(0)
            else:
                idx = editor.findText(value)
                if idx == -1:
                    editor.setCurrentIndex(0)
                else:
                    editor.setCurrentIndex(idx)
        elif cbo_type == smrt_consts.ADV_SORT_SORT_ORD_VALUE:
            if value == smrt_consts.ADV_SORT_NO_SELECT_FLAG:
                editor.setCurrentIndex(0)
            else:
                idx = editor.findData(value)
                if idx == -1:
                    editor.setCurrentIndex(0)
                else:
                    editor.setCurrentIndex(idx)
        editor.showPopup()

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        editor: QtWidgets.QComboBox
        value = editor.currentData()
        model.setData(index, value, role=QtCore.Qt.ItemDataRole.EditRole)


class AdvSortDialog(frmls_dialog.FramelessDialog):

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_dialog_win_ui()
        self.table_model = AdvSortDataModel(parent=self)
        self.table_items.setModel(self.table_model)
        self.sel_model = self.table_items.selectionModel()

        # init btns
        self.btn_move_up.setEnabled(False)
        self.btn_move_down.setEnabled(False)
        self.btn_remove_level.setEnabled(False)

        self.table_items.setItemDelegateForColumn(1, AdvSortCboDelegate(parent=self.table_items))
        self.table_items.setItemDelegateForColumn(2, AdvSortCboDelegate(parent=self.table_items))

        # connect signals and slots
        self.btn_add_level.clicked.connect(self.on_add_row_btn)
        self.btn_remove_level.clicked.connect(self.on_remove_row_btn)
        self.btn_move_up.clicked.connect(self.on_move_up_btn)
        self.btn_move_down.clicked.connect(self.on_move_down_btn)
        self.sel_model.selectionChanged.connect(self.on_selection_model_change)

        self.table_items.horizontalHeader().setStretchLastSection(True)

        # self.table_items.setColumnWidth(0, 33)
        # self.table_items.setColumnWidth(1, 33)
        # self.table_items.setColumnWidth(2, 33)

    def setup_dialog_win_ui(self):
        self.setObjectName("adv_sort_dialog")
        self.set_titlebar_mode(frmls_dialog.TitleMode.ONLY_CLOSE_BTN)
        self.resize(380, 260)
        self.cent_widget = QtWidgets.QWidget(self)
        self.set_central_widget(self.cent_widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lbl_title.setFont(font)
        self.lbl_title.setMinimumWidth(250)
        self.lbl_title.setText("Select Sort Options")
        # self.tbMenu.setIcon(QtGui.QIcon(':/ConMedSwoosh.png'))
        self.layout_adv_option_dialog = QtWidgets.QVBoxLayout(self.cent_widget)
        self.layout_adv_option_dialog.setContentsMargins(5, 5, 5, 5)
        self.layout_adv_option_dialog.setSpacing(5)
        self.layout_adv_option_dialog.setObjectName("layout_adv_option_dialog")
        self.frm_header_btns = QtWidgets.QFrame(self.cent_widget)
        self.frm_header_btns.setToolTip("")
        self.frm_header_btns.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.frm_header_btns.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_header_btns.setObjectName("frm_header_btns")
        self.layout_frm_header_btns = QtWidgets.QHBoxLayout(self.frm_header_btns)
        self.layout_frm_header_btns.setContentsMargins(1, 1, 1, 1)
        self.layout_frm_header_btns.setSpacing(3)
        self.layout_frm_header_btns.setObjectName("layout_frm_header_btns")
        self.btn_add_level = QtWidgets.QToolButton(self.frm_header_btns)
        self.btn_add_level.setMinimumSize(QtCore.QSize(110, 30))
        self.btn_add_level.setMaximumSize(QtCore.QSize(110, 30))
        self.btn_add_level.setToolTip("")
        self.btn_add_level.setText("Add Level")
        self.btn_add_level.setIcon(QtGui.QIcon(':/add_item_icon.png'))

        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/add_item_icon.PNG"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        # self.btn_add_level.setIcon(icon)
        self.btn_add_level.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_add_level.setObjectName("btn_add_level")
        self.btn_add_level.setStyleSheet('#btn_add_level:!hover {border: none;}')
        self.layout_frm_header_btns.addWidget(self.btn_add_level)
        self.btn_remove_level = QtWidgets.QToolButton(self.frm_header_btns)
        self.btn_remove_level.setMinimumSize(QtCore.QSize(130, 30))
        self.btn_remove_level.setMaximumSize(QtCore.QSize(130, 30))
        self.btn_remove_level.setToolTip("")
        self.btn_remove_level.setText("Delete Level")
        self.btn_remove_level.setIcon(QtGui.QIcon(':/remove_item_icon.png'))
        self.btn_remove_level.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_remove_level.setObjectName("btn_remove_level")
        self.btn_remove_level.setStyleSheet('#btn_remove_level:!hover {border: none;}')
        self.layout_frm_header_btns.addWidget(self.btn_remove_level)
        self.btn_move_up = QtWidgets.QToolButton(self.frm_header_btns)
        self.btn_move_up.setMinimumSize(QtCore.QSize(30, 30))
        self.btn_move_up.setMaximumSize(QtCore.QSize(30, 30))
        self.btn_move_up.setToolTip("")
        self.btn_move_up.setText("")
        self.btn_move_up.setIcon(QtGui.QIcon(':/move_up_hover.png'))
        self.btn_move_up.setObjectName("btn_move_up")
        self.btn_move_up.setStyleSheet('#btn_move_up:!hover {border: none;}')
        self.layout_frm_header_btns.addWidget(self.btn_move_up)
        self.btn_move_down = QtWidgets.QToolButton(self.frm_header_btns)
        self.btn_move_down.setMinimumSize(QtCore.QSize(30, 30))
        self.btn_move_down.setMaximumSize(QtCore.QSize(30, 30))
        self.btn_move_down.setToolTip("")
        self.btn_move_down.setText("")
        self.btn_move_down.setIcon(QtGui.QIcon(':/move_down_clicked.png'))
        self.btn_move_down.setObjectName("btn_move_down")
        self.btn_move_down.setStyleSheet('#btn_move_down:!hover {border: none;}')
        self.layout_frm_header_btns.addWidget(self.btn_move_down)
        spacerItem = QtWidgets.QSpacerItem(137, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.layout_frm_header_btns.addItem(spacerItem)
        self.layout_adv_option_dialog.addWidget(self.frm_header_btns)
        self.table_items = QtWidgets.QTableView(self.cent_widget)
        self.table_items.setToolTip("")
        self.table_items.setAlternatingRowColors(True)
        self.table_items.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table_items.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_items.setObjectName("table_items")
        self.table_items.verticalHeader().setVisible(False)
        self.table_items.horizontalHeader().setVisible(True)
        self.table_items.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
        self.layout_adv_option_dialog.addWidget(self.table_items)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.cent_widget)
        self.buttonBox.setToolTip("")
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.layout_adv_option_dialog.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self.cent_widget)

    def show_dialog(self, visible_columns: dict[int, str], current_sort: list[tuple[int, QtCore.Qt.SortOrder]],
                    dtypes: dict[str, smrt_consts.SmartDataTypes]) -> int:

        self.table_model.reset_model(visible_columns, current_sort, dtypes)
        return self.exec()

    def accept(self) -> None:
        if self.table_model.sort_list_valid():
            super().accept()
            return
        msgbx = frmls_msgbx.FramelessMsgBx(parent=self)
        msgbx.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msgbx.setText('You cannot leave incomplete entries in the table.')
        msgbx.exec()

    @QtCore.pyqtSlot()
    def on_add_row_btn(self):
        success = self.table_model.add_sort_entry()

        if success:
            self.table_items.selectRow(self.table_model.rowCount() - 1)
        else:
            msgbx = frmls_msgbx.FramelessMsgBx(parent=self)
            msgbx.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgbx.setText('You must complete the current entries before adding a new one.')
            msgbx.exec()

    @QtCore.pyqtSlot()
    def on_remove_row_btn(self):
        if not self.sel_model.selectedRows():
            return
        selected_row = self.sel_model.selectedRows()[0].row()
        self.table_model.remove_sort_entry(selected_row)

    @QtCore.pyqtSlot()
    def on_move_up_btn(self):
        if not self.sel_model.selectedRows():
            return
        selected_row = self.sel_model.selectedRows()[0].row()
        self.table_model.move_sort_entry(selected_row, True)
        self.table_items.selectRow(selected_row - 1)

    @QtCore.pyqtSlot()
    def on_move_down_btn(self):
        if not self.sel_model.selectedRows():
            return
        selected_row = self.sel_model.selectedRows()[0].row()
        self.table_model.move_sort_entry(selected_row, False)
        self.table_items.selectRow(selected_row + 1)

    @QtCore.pyqtSlot(QtCore.QItemSelection, QtCore.QItemSelection)
    def on_selection_model_change(self, selected, deselected):
        if len(self.sel_model.selectedRows()):
            self.btn_remove_level.setEnabled(True)
            if self.table_model.rowCount() > 1:
                selected_row = self.sel_model.selectedRows()[0].row()
                if selected_row == 0:
                    self.btn_move_up.setEnabled(False)
                    self.btn_move_down.setEnabled(True)
                elif selected_row == self.table_model.rowCount() - 1:
                    self.btn_move_up.setEnabled(True)
                    self.btn_move_down.setEnabled(False)
                else:
                    self.btn_move_up.setEnabled(True)
                    self.btn_move_down.setEnabled(True)
            else:
                self.btn_move_up.setEnabled(False)
                self.btn_move_down.setEnabled(False)
        else:
            self.btn_move_up.setEnabled(False)
            self.btn_move_down.setEnabled(False)
            self.btn_remove_level.setEnabled(False)

    def get_current_sort(self) -> list[tuple[int, QtCore.Qt.SortOrder]]:
        return self.table_model.sort_items

    def resize_table_cols(self):
        num_cols = len(self.table_model.TABLE_COLS)
        if self.table_items.verticalScrollBar().isVisible():
            calc_width = int(
                (self.table_items.width() - self.table_items.verticalScrollBar().width()) / num_cols
            )
        else:
            calc_width = int(self.table_items.width() / num_cols)
        if calc_width < smrt_consts.MIN_COLUMN_WIDTH:
            calc_width = smrt_consts.MIN_COLUMN_WIDTH
        for i in range(num_cols):
            self.table_items.horizontalHeader().resizeSection(i, calc_width)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.resize_table_cols()
        super().resizeEvent(a0)

class AdvSortDataModel(QtCore.QAbstractTableModel):

    SORT_INDEX_COL_IDX = 0
    COLUMN_NAME_COL_IDX = 1
    SORT_ORDER_COL_IDX = 2
    TABLE_COLS = [SORT_INDEX_COL_IDX, COLUMN_NAME_COL_IDX, SORT_ORDER_COL_IDX]
    TEMP_COL_NUM = -999
    TEMP_SORT_ORDER = -99

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)

        self.sort_items: list[tuple[int, QtCore.Qt.SortOrder]] = []
        self.column_dict: dict[int, str] = {}
        self.dtype_dict: dict[str, smrt_consts.SmartDataTypes] = {}
        self.unsorted_cols: list[str] = []

    def reset_model(self, column_dict: dict[int, str], current_sort: list[tuple[int, QtCore.Qt.SortOrder]],
                    dtype_dict: dict[str, smrt_consts.SmartDataTypes]):
        self.beginResetModel()
        # self.sort_items.clear()
        # self.column_dict.clear()
        # self.dtype_dict.clear()
        self.sort_items = current_sort.copy()
        self.column_dict = column_dict.copy()
        self.dtype_dict = dtype_dict.copy()
        self._populate_unsorted_cols()
        self.endResetModel()

    def _populate_unsorted_cols(self):
        self.unsorted_cols.clear()
        temp_dict = self.column_dict.copy()
        for col_num, _ in self.sort_items:
            temp_dict.pop(col_num, None)
        self.unsorted_cols += list(temp_dict.values())

    def add_sort_entry(self) -> bool:
        for col_num, _ in self.sort_items:
            if col_num == AdvSortDataModel.TEMP_COL_NUM:
                return False
        entry_num = len(self.sort_items)
        self.beginInsertRows(QtCore.QModelIndex(), entry_num, entry_num)
        self.sort_items.append((AdvSortDataModel.TEMP_COL_NUM, AdvSortDataModel.TEMP_SORT_ORDER))
        self.endInsertRows()

        return True

    def sort_list_valid(self) -> bool:
        for col_num, sort_ord in self.sort_items:
            if col_num == AdvSortDataModel.TEMP_COL_NUM:
                return False
            if sort_ord == AdvSortDataModel.TEMP_SORT_ORDER:
                return False
        return True


    def move_sort_entry(self, row_num: int, move_up: bool):
        if row_num < 0 or row_num >= len(self.sort_items):
            return
        self.beginRemoveRows(QtCore.QModelIndex(), row_num, row_num)
        entry = self.sort_items.pop(row_num)
        self.endRemoveRows()
        if move_up:
            self.beginInsertRows(QtCore.QModelIndex(), row_num - 1, row_num - 1)
            self.sort_items.insert(row_num - 1, entry)
            self.endInsertRows()
        else:
            self.beginInsertRows(QtCore.QModelIndex(), row_num + 1, row_num + 1)
            self.sort_items.insert(row_num + 1, entry)
            self.endInsertRows()

    def remove_sort_entry(self, row_num: int):
        if row_num < 0 or row_num >= len(self.sort_items):
            return
        self.beginRemoveRows(QtCore.QModelIndex(), row_num, row_num)
        val, _ = self.sort_items.pop(row_num)
        self.unsorted_cols.append(self.column_dict.get(val, ''))
        self.endRemoveRows()

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.sort_items)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(AdvSortDataModel.TABLE_COLS)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None
        entry_num = index.row()
        entry_column_num: int
        entry_sort_order: QtCore.Qt.SortOrder
        entry_column_num, entry_sort_order = self.sort_items[entry_num]
        entry_column_name: str = self.column_dict.get(entry_column_num, '')
        entry_column_dtype: smrt_consts.SmartDataTypes = self.dtype_dict.get(entry_column_name, smrt_consts.SmartDataTypes.UNKNOWN)

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if index.column() == AdvSortDataModel.SORT_INDEX_COL_IDX:
                return str(index.row() + 1)
            if index.column() == AdvSortDataModel.COLUMN_NAME_COL_IDX:
                if entry_column_num == AdvSortDataModel.TEMP_COL_NUM:
                    return 'Select column...'
                else:
                    return entry_column_name
            if index.column() == AdvSortDataModel.SORT_ORDER_COL_IDX:
                if entry_sort_order == AdvSortDataModel.TEMP_SORT_ORDER:
                    return 'Select sort order...'
                if entry_column_dtype == smrt_consts.SmartDataTypes.DATE or entry_column_dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                    if entry_sort_order == QtCore.Qt.SortOrder.AscendingOrder:
                        return 'Oldest to Newest'
                    else:
                        return 'Newest to Oldest'
                elif entry_column_dtype == smrt_consts.SmartDataTypes.INT or \
                    entry_column_dtype == smrt_consts.SmartDataTypes.FLOAT or \
                    entry_column_dtype == smrt_consts.SmartDataTypes.ACCT:
                    if entry_sort_order == QtCore.Qt.SortOrder.AscendingOrder:
                        return 'Smallest to Largest'
                    else:
                        return 'Largest to Smallest'
                else:
                    if entry_sort_order == QtCore.Qt.SortOrder.AscendingOrder:
                        return 'Sort A to Z'
                    else:
                        return 'Sort Z to A'

        elif role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == AdvSortDataModel.COLUMN_NAME_COL_IDX:
                if entry_column_num == AdvSortDataModel.TEMP_COL_NUM:
                    return smrt_consts.ADV_SORT_NO_SELECT_FLAG
                else:
                    return entry_column_name
            if index.column() == AdvSortDataModel.SORT_ORDER_COL_IDX:
                if entry_sort_order == AdvSortDataModel.TEMP_SORT_ORDER:
                    return smrt_consts.ADV_SORT_NO_SELECT_FLAG
                return entry_sort_order

        elif role == smrt_consts.DTYPE_QUERY_ROLE:
            return entry_column_dtype

        elif role == smrt_consts.CBO_COL_LIST_ROLE:
            return self.unsorted_cols.copy()

        elif role == smrt_consts.CBO_TYPE_ROLE:
            if index.column() == AdvSortDataModel.COLUMN_NAME_COL_IDX:
                return smrt_consts.ADV_SORT_COL_NAME_VALUE
            elif index.column() == AdvSortDataModel.SORT_ORDER_COL_IDX:
                return smrt_consts.ADV_SORT_SORT_ORD_VALUE

        elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole and index.column() == AdvSortDataModel.SORT_INDEX_COL_IDX:
            return QtCore.Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if section < AdvSortDataModel.SORT_INDEX_COL_IDX or section > AdvSortDataModel.SORT_ORDER_COL_IDX:
            return None
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            return QtCore.Qt.AlignmentFlag.AlignCenter
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if section == AdvSortDataModel.SORT_INDEX_COL_IDX:
                return '#'
            elif section == AdvSortDataModel.COLUMN_NAME_COL_IDX:
                return 'Column'
            elif section == AdvSortDataModel.SORT_ORDER_COL_IDX:
                return 'Sort Order'
        return None

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = QtCore.Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        if index.column() == AdvSortDataModel.SORT_INDEX_COL_IDX:
            return False

        if role != QtCore.Qt.ItemDataRole.EditRole:
            return False

        row_num = index.row()
        if index.column() == AdvSortDataModel.COLUMN_NAME_COL_IDX:
            if value == index.data():
                return False
            _, sort_val = self.sort_items.pop(row_num)
            for idx, dict_name in self.column_dict.items():
                if dict_name == value:
                    break
            self.sort_items.insert(row_num, (idx, sort_val))
            self.dataChanged.emit(index, index)
            self._populate_unsorted_cols()
            return True
        elif index.column() == AdvSortDataModel.SORT_ORDER_COL_IDX:
            col_name, _ = self.sort_items.pop(row_num)
            self.sort_items.insert(row_num, (col_name, value))
            self.dataChanged.emit(index, index)
            return True


    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        flags = QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
        if index.column() == AdvSortDataModel.COLUMN_NAME_COL_IDX or index.column() == AdvSortDataModel.SORT_ORDER_COL_IDX:
            flags |= QtCore.Qt.ItemFlag.ItemIsEditable

        return flags
