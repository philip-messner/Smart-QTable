from PyQt6 import QtCore, QtGui, QtWidgets
import pandas as pd

import re
import datetime
import locale

from smart_qtable import smrt_consts


class SmartFilterDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setup_dialog_ui()

        locale.setlocale(locale.LC_ALL, '')

        self.mode = smrt_consts.SmartFilterMode.TEXT
        self.column_name = 'NAME'
        self.column_data: pd.Series = None
        self.tree_widget_item_changed_enabled = False
        self.current_filter = None
        self.new_filter = None
        self.float_dict = {}
        self.action_requested = smrt_consts.SmartFilterAction.NO_ACTION
        self.select_all = False

        self.model = SmartTreeModel()
        self.tree_view.setModel(self.model)
        self.time_resolution: bool = False

        # connect signals and slots
        self.btnbox.accepted.connect(self.on_okay_clicked)
        self.btnbox.rejected.connect(self.on_cancel_clicked)
        self.cbo_filter_select.currentIndexChanged.connect(self.on_cboFilter_change)
        self.line_edit_filter_string.textChanged.connect(self.on_filter_string_update)
        self.btn_hide_col.clicked.connect(self.on_hide_col_clicked)
        self.btn_sort_az.clicked.connect(self.on_sort_az_clicked)
        self.btn_sort_za.clicked.connect(self.on_sort_za_clicked)
        self.btn_clear_filter.clicked.connect(self.on_clr_filter_clicked)
        # self.model.signal_select_all_changed.connect(self.set_enable_okay_btn)
        self.lbl_warning_text.linkActivated.connect(self.on_clip_link_activated)


    def setup_dialog_ui(self):
        self.setObjectName("SortFilterDialog")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Popup)
        # self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.resize(198, 520)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setPointSize(8)

        self.dialog_layout = QtWidgets.QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)
        self.dialog_layout.setSpacing(1)

        # Hide button
        self.btn_hide_col = QtWidgets.QToolButton(self)
        # self.btn_hide_col.setFixedWidth(198)
        self.btn_hide_col.setFixedHeight(43)
        self.btn_hide_col.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        # self.btn_hide_col.setGeometry(QtCore.QRect(0, 0, 198, 43))
        self.btn_hide_col.setText(f'Hide Column "NAME"')
        self.btn_hide_col.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/HideIcon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btn_hide_col.setIcon(icon)
        self.btn_hide_col.setObjectName("btn_hide_col")
        self.btn_hide_col.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.dialog_layout.addWidget(self.btn_hide_col)

        # add line separator
        self.line_4 = QtWidgets.QFrame(self)
        # self.line_4.setGeometry(QtCore.QRect(0, 36, 198, 16))
        self.line_4.resize(198, 16)
        self.line_4.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.dialog_layout.addWidget(self.line_4)

        # Sort ascending button
        self.btn_sort_az = QtWidgets.QToolButton(self)
        # self.btn_sort_az.setGeometry(QtCore.QRect(0, 44, 198, 43))
        # self.btn_sort_az.setFixedWidth(198)
        self.btn_sort_az.setFont(font)
        self.btn_sort_az.setFixedHeight(43)
        self.btn_sort_az.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.btn_sort_az.setText("Sort A to Z")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/sort_ascending.PNG"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btn_sort_az.setIcon(icon1)
        self.btn_sort_az.setCheckable(True)
        self.btn_sort_az.setObjectName("btn_sort_az")
        self.btn_sort_az.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_sort_az.setIconSize(QtCore.QSize(30, 30))
        self.dialog_layout.addWidget(self.btn_sort_az)

        # Sort descending button
        self.btn_sort_za = QtWidgets.QToolButton(self)
        self.btn_sort_za.setFont(font)
        # self.btn_sort_za.setGeometry(QtCore.QRect(0, 87, 198, 43))
        # self.btn_sort_za.setFixedWidth(198)
        self.btn_sort_za.setFixedHeight(43)
        self.btn_sort_za.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.btn_sort_za.setText("Sort Z to A")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/sort_descending.PNG"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btn_sort_za.setIcon(icon2)
        self.btn_sort_za.setCheckable(True)
        self.btn_sort_za.setObjectName("btn_sort_za")
        self.btn_sort_za.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_sort_za.setIconSize(QtCore.QSize(30, 30))
        self.dialog_layout.addWidget(self.btn_sort_za)

        # add another line
        self.line_3 = QtWidgets.QFrame(self)
        # self.line_3.setGeometry(QtCore.QRect(0, 123, 198, 16))
        self.line_3.resize(198, 16)
        self.line_3.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.dialog_layout.addWidget(self.line_3)

        # Clear filter button
        self.btn_clear_filter = QtWidgets.QToolButton(self)
        self.btn_clear_filter.setFont(font)
        # self.btn_clear_filter.setGeometry(QtCore.QRect(0, 131, 198, 43))
        # self.btn_clear_filter.setFixedWidth(198)
        self.btn_clear_filter.setFixedHeight(43)
        self.btn_clear_filter.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.btn_clear_filter.setText("Clear Filter \"NAME\"")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/clear_filter.PNG"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btn_clear_filter.setIcon(icon3)
        self.btn_clear_filter.setObjectName("btn_clear_filter")
        self.btn_clear_filter.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_clear_filter.setIconSize(QtCore.QSize(25, 25))
        self.dialog_layout.addWidget(self.btn_clear_filter)

        # add another line
        self.line_2 = QtWidgets.QFrame(self)
        # self.line_2.setGeometry(QtCore.QRect(0, 167, 198, 16))
        self.line_2.resize(198, 16)
        self.line_2.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.dialog_layout.addWidget(self.line_2)

        # add filter select cbo box and label
        self.frm_filter_select = QtWidgets.QFrame()
        self.layout_frm_filter_select = QtWidgets.QHBoxLayout(self.frm_filter_select)
        self.layout_frm_filter_select.setContentsMargins(1, 1, 1, 1)
        self.layout_frm_filter_select.setSpacing(2)

        self.lbl_select_filter_type = QtWidgets.QLabel(self)
        self.lbl_select_filter_type.setFont(font)
        # self.lbl_select_filter_type.setGeometry(QtCore.QRect(8, 185, 111, 16))
        # self.lbl_select_filter_type.setFixedWidth(111)
        self.lbl_select_filter_type.setText("Select Filter Type:")
        self.lbl_select_filter_type.setObjectName("lbl_select_filter_type")
        self.layout_frm_filter_select.addWidget(self.lbl_select_filter_type)

        self.cbo_filter_select = QtWidgets.QComboBox(self)
        self.cbo_filter_select.setFont(font)
        # self.cbo_filter_select.setGeometry(QtCore.QRect(5, 205, 181, 22))
        # self.cbo_filter_select.setFixedWidth(181)
        self.cbo_filter_select.setFixedHeight(22)
        self.cbo_filter_select.setObjectName("cbo_filter_select")
        self.cbo_filter_select.addItem('Text Filter')
        self.cbo_filter_select.addItem('Regex Pattern')
        self.layout_frm_filter_select.addWidget(self.cbo_filter_select)
        self.dialog_layout.addWidget(self.frm_filter_select)

        # add another line
        self.line = QtWidgets.QFrame(self)
        # self.line.setGeometry(QtCore.QRect(0, 229, 198, 16))
        self.line.resize(198, 16)
        self.line.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.dialog_layout.addWidget(self.line)

        # Filter line edit box
        self.line_edit_filter_string = QtWidgets.QLineEdit(self)
        self.line_edit_filter_string.setFont(font)
        # self.line_edit_filter_string.setGeometry(QtCore.QRect(3, 244, 191, 31))
        # self.line_edit_filter_string.setFixedWidth(191)
        self.line_edit_filter_string.setFixedHeight(31)
        self.line_edit_filter_string.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.line_edit_filter_string.sizePolicy().hasHeightForWidth())
        # self.line_edit_filter_string.setSizePolicy(sizePolicy)
        self.line_edit_filter_string.setPlaceholderText('Search')
        self.line_edit_filter_string.setClearButtonEnabled(True)
        self.line_edit_filter_string.setObjectName("line_edit_filter_string")
        self.dialog_layout.addWidget(self.line_edit_filter_string)

        # add the tree view
        self.tree_view = QtWidgets.QTreeView(self)
        self.tree_view.setFont(font)
        # self.tree_view.setGeometry(QtCore.QRect(3, 280, 191, 201))
        self.tree_view.resize(191, 201)
        self.tree_view.setObjectName("list_view_filter_options")
        self.tree_view.setHeaderHidden(True)
        self.dialog_layout.addWidget(self.tree_view)

        self.frm_info_clipping = QtWidgets.QFrame(self)
        self.frm_info_clipping.setFixedHeight(31)
        self.frm_info_clipping.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        # self.btn_clear_filter.setIconSize(QtCore.QSize(25, 25))
        self.layout_frm_info_clipping = QtWidgets.QHBoxLayout(self.frm_info_clipping)
        self.layout_frm_info_clipping.setContentsMargins(1, 1, 1, 1)
        self.layout_frm_info_clipping.setSpacing(3)
        self.lbl_warning_symbol = QtWidgets.QLabel(self.frm_info_clipping)
        self.lbl_warning_symbol.setPixmap(QtGui.QPixmap('resources/warning-icon.png'))
        self.lbl_warning_symbol.setScaledContents(True)
        self.lbl_warning_symbol.setFixedHeight(25)
        self.lbl_warning_symbol.setFixedWidth(25)
        self.layout_frm_info_clipping.addWidget(self.lbl_warning_symbol)
        self.lbl_warning_text = QtWidgets.QLabel('<a href=\"smarttable://item_clipping\">Not all items showing', self.frm_info_clipping)
        self.layout_frm_info_clipping.addWidget(self.lbl_warning_text)
        self.dialog_layout.addWidget(self.frm_info_clipping)

        self.btnbox = QtWidgets.QDialogButtonBox(self)
        self.btnbox.setFont(font)
        # self.btnbox.setGeometry(QtCore.QRect(3, 488, 193, 28))
        self.btnbox.resize(193, 28)
        self.btnbox.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.btnbox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.btnbox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel |
                                       QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.btnbox.setObjectName("btnbox")
        self.dialog_layout.addWidget(self.btnbox)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

    @QtCore.pyqtSlot(str)
    def on_clip_link_activated(self, url: str):
        msgbx = QtWidgets.QMessageBox(self)
        msgbx.setWindowTitle('Smart Filter')
        msgbx.setWindowIcon(QtGui.QIcon(':ConMedSwoosh.png'))
        msgbx.setText(f'This column has more than {smrt_consts.FILTER_MAX_ROW_LIMIT:,} unique values. Only the first {smrt_consts.FILTER_MAX_ROW_LIMIT:,} values are shown.')
        msgbx.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msgbx.exec()

    def get_new_filter_vals(self):
        new_filter_vals = self.model.get_checked_nodes(self.current_sort)
        if self.model.is_add_to_current_checked() and self.current_filter:
            for new_val in new_filter_vals:
                if new_val in self.current_filter:
                    self.current_filter.remove(new_val)
            self.new_filter = self.current_filter + new_filter_vals
        else:
            self.new_filter = new_filter_vals

    @QtCore.pyqtSlot(int)
    def set_enable_okay_btn(self, select_all_state: int):
        if select_all_state == QtCore.Qt.CheckState.Unchecked.value:
            self.btnbox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        else:
            if self.current_filter:
                self.btnbox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            else:
                self.btnbox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    @QtCore.pyqtSlot()
    def on_okay_clicked(self):
        self.get_new_filter_vals()
        # if (self.model.is_select_all_checked() and len(self.new_filter) == len(self.column_data)) or not self.new_filter:
        if self.model.is_select_all_checked() and not self.new_filter:
            self.action_requested = smrt_consts.SmartFilterAction.CLR_FILTER
            self.reject()
        elif not self.new_filter:
            self.action_requested = smrt_consts.SmartFilterAction.NO_ACTION
            self.reject()
        else:
            self.action_requested = smrt_consts.SmartFilterAction.NEW_FILTER
            self.accept()

    @QtCore.pyqtSlot()
    def on_cancel_clicked(self):
        self.action_requested = smrt_consts.SmartFilterAction.NO_ACTION
        self.reject()

    @QtCore.pyqtSlot()
    def on_clr_filter_clicked(self):
        self.action_requested = smrt_consts.SmartFilterAction.CLR_FILTER
        self.reject()

    @QtCore.pyqtSlot()
    def on_sort_az_clicked(self):
        if self.btn_sort_az.isChecked():
            if self.btn_sort_za.isChecked():
                self.btn_sort_za.setChecked(False)
            self.action_requested = smrt_consts.SmartFilterAction.SORT_ASCENDING
            self.reject()
        else:
            if not self.btn_sort_za.isChecked():
                self.action_requested = smrt_consts.SmartFilterAction.CLR_SORT
                self.reject()

    @QtCore.pyqtSlot()
    def on_sort_za_clicked(self):
        # print('Sort Descending was clicked!')
        if self.btn_sort_za.isChecked():
            if self.btn_sort_az.isChecked():
                self.btn_sort_az.setChecked(False)
            self.action_requested = smrt_consts.SmartFilterAction.SORT_DESCENDING
            self.reject()
        else:
            if not self.btn_sort_az.isChecked():
                self.action_requested = smrt_consts.SmartFilterAction.CLR_SORT
                self.reject()

    @QtCore.pyqtSlot()
    def on_hide_col_clicked(self):
        # print('Hide column was clicked!')
        self.action_requested = smrt_consts.SmartFilterAction.HIDE_COL
        self.reject()

    def set_window_mode(self, mode: smrt_consts.SmartFilterMode):
        self.mode = mode
        if mode == smrt_consts.SmartFilterMode.DATE or mode == smrt_consts.SmartFilterMode.DATE_TIME:
            self.btn_sort_az.setText('Sort Oldest to Newest')
            self.btn_sort_za.setText('Sort Newest to Oldest')
        elif mode == smrt_consts.SmartFilterMode.NUMBER or mode == smrt_consts.SmartFilterMode.ACCT:
            self.btn_sort_az.setText('Sort Smallest to Largest')
            self.btn_sort_za.setText('Sort Largest to Smallest')
        else:
            self.btn_sort_az.setText('Sort A to Z')
            self.btn_sort_za.setText('Sort Z to A')

    def show_window(self, column_data: pd.Series, column_name: str, dtype: smrt_consts.SmartDataTypes,
                    current_filter=None, current_sort_order: QtCore.Qt.SortOrder=None, **kwargs):
        # see if there is ANY data to populate, if not exit
        if column_data is None or column_data.size < 1:
            self.action_requested = smrt_consts.SmartFilterAction.NO_ACTION
            self.reject()
            return
        self.resize(198, 520)
        self.time_resolution = kwargs.get('time_resolution', False)
        self.action_requested = smrt_consts.SmartFilterAction.NO_ACTION
        self.select_all = False
        # self.tree_widget.clear()
        self.line_edit_filter_string.clear()
        self.float_dict.clear()
        self.column_name = column_name
        self.current_filter = current_filter
        self.current_sort = current_sort_order
        self.new_filter = current_filter
        self.dtype = dtype
        self.btn_hide_col.setText(f'Hide Column "{self.column_name}"')
        self.btn_clear_filter.setText(f'Clear Filter "{self.column_name}"')

        if self.dtype == smrt_consts.SmartDataTypes.FLOAT or self.dtype == smrt_consts.SmartDataTypes.INT:
            self.set_window_mode(smrt_consts.SmartFilterMode.NUMBER)
        elif self.dtype == smrt_consts.SmartDataTypes.ACCT:
            self.set_window_mode(smrt_consts.SmartFilterMode.ACCT)
        elif self.dtype == smrt_consts.SmartDataTypes.DATE:
            self.set_window_mode(smrt_consts.SmartFilterMode.DATE)
        elif self.dtype == smrt_consts.SmartDataTypes.DATE_TIME:
            self.set_window_mode(smrt_consts.SmartFilterMode.DATE_TIME)
        else:
            self.set_window_mode(smrt_consts.SmartFilterMode.TEXT)

        if self.mode == smrt_consts.SmartFilterMode.DATE or self.mode == smrt_consts.SmartFilterMode.DATE_TIME:
            self.column_data = column_data.sort_values(ascending=False).unique()
        else:
            self.column_data = column_data.sort_values(ascending=True).unique()
        self.column_data = pd.Series(self.column_data)
        if current_sort_order is not None:
            if current_sort_order == QtCore.Qt.SortOrder.AscendingOrder:
                self.btn_sort_az.setChecked(True)
                self.btn_sort_za.setChecked(False)
            else:
                self.btn_sort_az.setChecked(False)
                self.btn_sort_za.setChecked(True)
        else:
            self.btn_sort_az.setChecked(False)
            self.btn_sort_za.setChecked(False)

        if current_filter is not None:
            self.btn_clear_filter.setEnabled(True)
        else:
            self.btn_clear_filter.setEnabled(False)

        # populate the tree view
        self.on_filter_string_update()
        # self.model.update_data(self.column_data, dtype, self.current_filter, time_resolution=self.time_resolution)

        return self.exec()

    @QtCore.pyqtSlot()
    def on_filter_string_update(self):
        if self.column_data.size > smrt_consts.FILTER_MAX_ROW_LIMIT:
            self.frm_info_clipping.setVisible(True)
        else:
            self.frm_info_clipping.setVisible(False)
        sliced_column_data = self.column_data.iloc[:smrt_consts.FILTER_MAX_ROW_LIMIT]
        if self.line_edit_filter_string.text() == '':
            self.model.update_data(sliced_column_data, self.dtype, self.current_filter, time_resolution=self.time_resolution)
        else:
            new_tree_data = []
            for match_item in sliced_column_data:
                txt_to_match = ''
                if pd.isnull(match_item):
                    txt_to_match = smrt_consts.BLANKS_TXT.upper()
                elif match_item == smrt_consts.UNKNOWN_DATE or match_item == smrt_consts.UNKNOWN_DATETIME:
                    txt_to_match = smrt_consts.UNKNOWN_TXT.upper()
                elif self.dtype == smrt_consts.SmartDataTypes.DATE or (self.dtype == smrt_consts.SmartDataTypes.DATE_TIME and not self.time_resolution):
                    txt_to_match = pd.to_datetime(match_item).strftime('%Y-%B-%d').upper()
                elif self.dtype == smrt_consts.SmartDataTypes.DATE_TIME and self.time_resolution:
                    txt_to_match = pd.to_datetime(match_item).strftime('%Y-%B-%d %H:%M:%S').upper()
                else:
                    txt_to_match = str(match_item).upper()
                if self.cbo_filter_select.currentText() == 'Text Filter':
                    if self.line_edit_filter_string.text().upper() in txt_to_match:
                        new_tree_data.append(match_item)
                elif self.cbo_filter_select.currentText() == 'Regex Pattern':
                    try:
                        if re.search(self.line_edit_filter_string.text(), txt_to_match, flags=3) is not None:
                            new_tree_data.append(match_item)
                    except re.error:
                        pass
            if new_tree_data:
                new_series = pd.Series(new_tree_data)
            else:
                new_series = pd.Series(dtype='int64')
            self.model.update_data(new_series, self.dtype, self.current_filter, time_resolution=self.time_resolution, user_has_match_data=True)

        # self.get_new_filter_vals()
        # if not self.new_filter:
        #     self.btnbox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        # else:
        #     self.btnbox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    @QtCore.pyqtSlot()
    def on_cboFilter_change(self):
        self.line_edit_filter_string.clear()


class TreeItemNode:

    def __init__(self, name, parent=None, **kwargs):
        self.name = name
        self.parent = parent
        self.children = []
        self.date_data: smrt_consts.DateTimeNodeData = kwargs.get('date_data', None)
        self.is_checkable = kwargs.get('is_checkable', True)
        self.check_state: QtCore.Qt.CheckState = kwargs.get('check_state', QtCore.Qt.CheckState.Checked.value)

    def get_or_create_child(self, name, **kwargs):
        date_data = kwargs.get('date_data', None)
        is_checkable = kwargs.get('is_checkable', True)
        check_state = kwargs.get('check_state', QtCore.Qt.CheckState.Checked.value)
        for child in self.children:
            if child.name == name:
                return child
        new_child = TreeItemNode(name, parent=self, date_data=date_data, is_checkable=is_checkable, check_state=check_state)
        self.children.append(new_child)
        return new_child

    def get_child(self, row_num):
        if row_num < 0 or row_num >= len(self.children):
            return None
        return self.children[row_num]

    def row(self):
        if self.parent and self.parent.children:
            try:
                return self.parent.children.index(self)
            except ValueError:
                return 0
        return 0

    def child_count(self):
        return len(self.children)


class SmartTreeModel(QtCore.QAbstractItemModel):

    signal_chk_changed = QtCore.pyqtSignal()
    signal_select_all_changed = QtCore.pyqtSignal(int)

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

        self.data_series: pd.Series = None
        self.dtype: smrt_consts.SmartDataTypes = smrt_consts.SmartDataTypes.TEXT
        self.current_filter: list = None
        self.user_has_match_data: bool = False
        self.time_resolution: bool = False
        self.root: TreeItemNode = TreeItemNode('root', is_checkable=False)
        no_data_node = self.root.get_or_create_child(smrt_consts.NO_MATCHES_TXT, is_checkable=False)
        self.select_all_node = None
        self.add_to_current_node = None
        self.unknown_node = None
        self.blanks_node = None
        self.invalid_node = None
        self.signal_chk_changed.connect(self.update_select_all_node)

    def update_data(self, data: pd.Series, dtype: smrt_consts.SmartDataTypes = smrt_consts.SmartDataTypes.TEXT, current_filter: list = None, **kwargs):

        def update_parent_nodes(node):
            if node == self.root:
                return
            all_checked = True
            all_unchecked = True
            for child in node.children:
                all_checked = all_checked and child.check_state == QtCore.Qt.CheckState.Checked.value
                all_unchecked = all_unchecked and child.check_state == QtCore.Qt.CheckState.Unchecked.value
            if all_checked:
                node.check_state = QtCore.Qt.CheckState.Checked.value
            elif all_unchecked:
                node.check_state = QtCore.Qt.CheckState.Unchecked.value
            else:
                node.check_state = QtCore.Qt.CheckState.PartiallyChecked
            update_parent_nodes(node.parent)

        self.dtype = dtype
        self.time_resolution = kwargs.get('time_resolution', False)
        self.current_filter =  current_filter
        self.user_has_match_data = kwargs.get('user_has_match_data', False)
        self.beginResetModel()

        self.data_series = data
        self.select_all_node = None
        self.add_to_current_node = None
        self.unknown_node = None
        self.blanks_node = None
        self.invalid_node = None
        self.root = TreeItemNode('root',is_checkable=False)

        if data is not None and data.size:
            # add a 'select all' node to the top of the tree
            if self.user_has_match_data:
                select_all_txt = smrt_consts.SELECT_ALL_RESULTS
            else:
                select_all_txt = smrt_consts.SELECT_ALL_TXT
            self.select_all_node = TreeItemNode(select_all_txt, parent=self.root, is_checkable=True, check_state=QtCore.Qt.CheckState.Checked.value)
            self.root.children.append(self.select_all_node)

            # add a 'add to current filter' node if applicable
            if self.current_filter:
                self.add_to_current_node = TreeItemNode(smrt_consts.ADD_CURRENT_TXT, parent=self.root, is_checkable=True, check_state=QtCore.Qt.CheckState.Unchecked.value)
                self.root.children.append(self.add_to_current_node)

            unknowns_present: bool = False
            blanks_present: bool = False
            invalid_present: bool = False

            if self.dtype == smrt_consts.SmartDataTypes.DATE or self.dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                for date in data:
                    if pd.isnull(date):
                        blanks_present = True
                    elif pd.Timestamp(date) == pd.Timestamp(smrt_consts.UNKNOWN_DATE) or \
                            pd.Timestamp(date) == pd.Timestamp(smrt_consts.UNKNOWN_DATETIME) or \
                            pd.Timestamp(date) == pd.Timestamp(smrt_consts.SORT_ASC_UNKNOWN_DATETIME) or \
                            pd.Timestamp(date) == pd.Timestamp(smrt_consts.SORT_ASC_UNKNOWN_DATE):
                        unknowns_present = True
                    elif pd.Timestamp(date) == pd.Timestamp(smrt_consts.INVALID_DATE) or \
                            pd.Timestamp(date) == pd.Timestamp(smrt_consts.INVALID_DATETIME):
                        invalid_present = True
                    else:
                        # date = pd.to_datetime(date)
                        year, month, day = date.year, date.month, date.day
                        year_node = self.root.get_or_create_child(year, date_data=smrt_consts.DateTimeNodeData.YEAR)
                        month_node = year_node.get_or_create_child(month, date_data=smrt_consts.DateTimeNodeData.MONTH)
                        day_node = month_node.get_or_create_child(day, date_data=smrt_consts.DateTimeNodeData.DAY)
                        if self.dtype == smrt_consts.SmartDataTypes.DATE_TIME and self.time_resolution:
                            hour, minute, second = date.hour, date.minute, date.second
                            day_node = month_node.get_or_create_child(day, date_data=smrt_consts.DateTimeNodeData.DAY)
                            hour_node = day_node.get_or_create_child(hour, date_data=smrt_consts.DateTimeNodeData.HOUR)
                            minute_node = hour_node.get_or_create_child(minute, date_data=smrt_consts.DateTimeNodeData.MIN)
                            second_node = minute_node.get_or_create_child(second, date_data=smrt_consts.DateTimeNodeData.SEC)
                        if not self.user_has_match_data and self.current_filter and date not in self.current_filter:
                            if not (self.time_resolution and self.dtype == smrt_consts.SmartDataTypes.DATE_TIME):
                                day_node.check_state = QtCore.Qt.CheckState.Unchecked.value
                                update_parent_nodes(day_node.parent)
                            else:
                                second_node.check_state = QtCore.Qt.CheckState.Unchecked.value
                                update_parent_nodes(second_node.parent)

            else:
                for item in data:
                    if pd.isnull(item):
                        blanks_present = True
                    else:
                        item_node = TreeItemNode(item, parent=self.root, is_checkable=True)
                        self.root.children.append(item_node)
                        if not self.user_has_match_data and self.current_filter and item not in self.current_filter:
                            item_node.check_state = QtCore.Qt.CheckState.Unchecked.value
                        else:
                            item_node.check_state = QtCore.Qt.CheckState.Checked.value
            if unknowns_present:
                self.unknown_node = TreeItemNode(smrt_consts.UNKNOWN_TXT, parent=self.root, is_checkable=True)
                self.root.children.append(self.unknown_node)
                if not self.user_has_match_data and self.current_filter and not (smrt_consts.UNKNOWN_DATE in self.current_filter or smrt_consts.UNKNOWN_DATETIME in self.current_filter):
                    self.unknown_node.check_state = QtCore.Qt.CheckState.Unchecked.value

            if blanks_present:
                self.blanks_node = TreeItemNode(smrt_consts.BLANKS_TXT, parent=self.root, is_checkable=True)
                self.root.children.append(self.blanks_node)
                if not self.user_has_match_data and self.current_filter and None not in self.current_filter:
                    self.blanks_node.check_state = QtCore.Qt.CheckState.Unchecked.value

            if invalid_present:
                self.invalid_node = TreeItemNode(smrt_consts.INVALID_TXT, parent=self.root, is_checkable=True)
                self.root.children.append(self.invalid_node)
                if not self.user_has_match_data and self.current_filter and not (smrt_consts.INVALID_DATE in self.current_filter or smrt_consts.INVALID_DATETIME in self.current_filter):
                    self.invalid_node.check_state = QtCore.Qt.CheckState.Unchecked.value

        else:
            self.root.get_or_create_child(smrt_consts.NO_MATCHES_TXT, is_checkable=False)

        self.update_select_all_node()

        self.endResetModel()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        # print(f'Index method: {row}, {column}, {parent}')
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = self.get_node(parent)
        child_item = parentItem.get_child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        node = self.get_node(index)
        if node == self.root:
            return QtCore.QModelIndex()
        parent = node.parent
        if parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        node = self.get_node(parent)
        return len(node.children)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.CheckStateRole:
            # print(f'Data method: {index.row(), index.column()}')
            node = self.get_node(index)
            if node.is_checkable:
                # print(f'Value: {node.check_state}')
                return node.check_state
            return
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return
        node = self.get_node(index)
        if node.name == smrt_consts.SELECT_ALL_TXT or node.name == smrt_consts.SELECT_ALL_RESULTS or node.name == smrt_consts.ADD_CURRENT_TXT or node.name == smrt_consts.BLANKS_TXT or node.name == smrt_consts.UNKNOWN_TXT:
            return str(node.name)
        if self.dtype == smrt_consts.SmartDataTypes.DATE or self.dtype == smrt_consts.SmartDataTypes.DATE_TIME:
            date_data = node.date_data
            if date_data == smrt_consts.DateTimeNodeData.MONTH:
                return str(smrt_consts.INT_TO_MONTH[node.name])
            else:
                return str(node.name)
        elif self.dtype == smrt_consts.SmartDataTypes.ACCT:
            return locale.currency(node.name, grouping=True)
        elif self.dtype == smrt_consts.SmartDataTypes.FLOAT:
            return f'{node.name:.2f}'
        elif self.dtype == smrt_consts.SmartDataTypes.INT:
            return f'{node.name}'
        elif self.dtype == smrt_consts.SmartDataTypes.STATUS:
            if node.name == smrt_consts.ActionStatus.IDLE:
                return 'Idle'
            elif node.name == smrt_consts.ActionStatus.UNINIT:
                return 'Unitialized'
            elif node.name == smrt_consts.ActionStatus.PENDING:
                return 'Pending'
            elif node.name == smrt_consts.ActionStatus.IN_PROGRESS:
                return 'In-Progress'
            elif node.name == smrt_consts.ActionStatus.COMPLETE:
                return 'Complete'
            elif node.name == smrt_consts.ActionStatus.ERROR:
                return 'Error'
            elif node.name == smrt_consts.ActionStatus.FAILED:
                return 'Fail'
        elif self.dtype == smrt_consts.SmartDataTypes.BOOL:
            if str(node.name).upper() == 'ON':
                return 'True'
            elif str(node.name).upper() == 'OFF':
                return 'False'
            elif str(node.name).upper() == 'YES':
                return 'True'
            elif str(node.name).upper() == 'NO':
                return 'False'
            elif str(node.name).upper() == 'TRUE':
                return 'True'
            elif str(node.name).upper() == 'FALSE':
                return 'False'
            elif node.name:
                return 'True'
            else:
                return 'False'

        return str(node.name)

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        def set_node_and_children(node: TreeItemNode, value: QtCore.Qt.CheckState):
            if node.is_checkable:
                node.check_state = value
                node_index = self.createIndex(node.row(), 0, node)
                self.dataChanged.emit(node_index, node_index, [QtCore.Qt.ItemDataRole.CheckStateRole])
            for child in node.children:
                set_node_and_children(child, value)

        def update_parent_node(node: TreeItemNode):
            if node == self.root:
                return
            all_checked = True
            all_unchecked = True
            for child in node.children:
                all_checked = all_checked and child.check_state == QtCore.Qt.CheckState.Checked.value
                all_unchecked = all_unchecked and child.check_state == QtCore.Qt.CheckState.Unchecked.value
            if all_checked:
                node.check_state = QtCore.Qt.CheckState.Checked.value
            elif all_unchecked:
                node.check_state = QtCore.Qt.CheckState.Unchecked.value
            else:
                node.check_state = QtCore.Qt.CheckState.PartiallyChecked
            node_index = self.createIndex(node.row(), 0, node)
            self.dataChanged.emit(node_index, node_index, [QtCore.Qt.ItemDataRole.CheckStateRole])
            update_parent_node(node.parent)

        if role == QtCore.Qt.ItemDataRole.CheckStateRole:
            node = self.get_node(index)
            if node.is_checkable:
                if node.name == smrt_consts.SELECT_ALL_TXT or node.name == smrt_consts.SELECT_ALL_RESULTS:
                    node.check_state = value
                    node_index = self.createIndex(node.row(), 0, node)
                    self.dataChanged.emit(node_index, node_index, [QtCore.Qt.ItemDataRole.CheckStateRole])
                    self.signal_select_all_changed.emit(value)
                    self.select_all(value)
                else:
                    set_node_and_children(node, value)
                    update_parent_node(node.parent)

                self.signal_chk_changed.emit()
                return True
        return False

    def select_all(self, check_state: QtCore.Qt.CheckState):
        def set_node_and_children(node: TreeItemNode, check_state: QtCore.Qt.CheckState):
            if node != self.root and node.is_checkable and node != self.add_to_current_node:
                node.check_state = check_state
                node_index = self.createIndex(node.row(), 0, node)
                self.dataChanged.emit(node_index, node_index, [QtCore.Qt.ItemDataRole.CheckStateRole])
            for child in node.children:
                set_node_and_children(child, check_state)

        set_node_and_children(self.root, check_state)

    def update_select_all_node(self):
        if self.select_all_node is None:
            return
        if self.current_filter:
            data_start_index = 2
        else:
            data_start_index = 1
        select_all_node = self.root.children[0]
        all_items_checked = True
        all_items_unchecked = True

        for item_node in self.root.children[data_start_index:]:
            all_items_checked = all_items_checked and item_node.check_state == QtCore.Qt.CheckState.Checked.value
            all_items_unchecked = all_items_unchecked and item_node.check_state == QtCore.Qt.CheckState.Unchecked.value

        if all_items_checked:
            select_all_node.check_state = QtCore.Qt.CheckState.Checked.value
            self.signal_select_all_changed.emit(QtCore.Qt.CheckState.Checked.value)
        elif all_items_unchecked:
            select_all_node.check_state = QtCore.Qt.CheckState.Unchecked.value
            self.signal_select_all_changed.emit(QtCore.Qt.CheckState.Unchecked.value)
        else:
            select_all_node.check_state = QtCore.Qt.CheckState.PartiallyChecked.value
        select_all_index = self.createIndex(self.select_all_node.row(), 0, self.select_all_node)
        self.dataChanged.emit(select_all_index, select_all_index, [QtCore.Qt.ItemDataRole.CheckStateRole])

    def flags(self, index):
        node = self.get_node(index)
        if node.is_checkable:
            return QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate
        return QtCore.Qt.ItemFlag.ItemIsEnabled

    def get_node(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def get_checked_nodes(self, current_sort):
        results = []
        for node in self.root.children:
            if self.select_all_node and node == self.select_all_node:
                pass
            elif self.add_to_current_node and node == self.add_to_current_node:
                pass
            elif self.blanks_node and node == self.blanks_node:
                if None not in results and self.blanks_node.check_state == QtCore.Qt.CheckState.Checked.value:
                    results.append(None)
            elif self.unknown_node and node == self.unknown_node:
                if self.unknown_node.check_state == QtCore.Qt.CheckState.Checked.value:
                    if self.dtype == smrt_consts.SmartDataTypes.DATE:
                        results.append(smrt_consts.UNKNOWN_DATE)
                        results.append(smrt_consts.SORT_ASC_UNKNOWN_DATE)
                    elif self.dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                        results.append(smrt_consts.UNKNOWN_DATETIME)
                        results.append(smrt_consts.SORT_ASC_UNKNOWN_DATETIME)
            elif self.invalid_node and node == self.invalid_node:
                if self.invalid_node.check_state == QtCore.Qt.CheckState.Checked.value:
                    if self.dtype == smrt_consts.SmartDataTypes.DATE:
                        results.append(smrt_consts.INVALID_DATE)
                    elif self.dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                        results.append(smrt_consts.INVALID_DATETIME)
            elif node.check_state == QtCore.Qt.CheckState.Unchecked.value:
                pass
            else:
                if self.dtype == smrt_consts.SmartDataTypes.DATE:
                    for month_node in node.children:
                        for day_node in month_node.children:
                            if day_node.check_state == QtCore.Qt.CheckState.Checked.value:
                                date_obj = datetime.datetime(node.name, month_node.name, day_node.name).date()
                                results.append(date_obj)
                elif self.dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                    for month_node in node.children:
                        for day_node in month_node.children:
                            if self.time_resolution:
                                for hour_node in day_node.children:
                                    for minute_node in hour_node.children:
                                        for second_node in minute_node.children:
                                            if second_node.check_state == QtCore.Qt.CheckState.Checked.value:
                                                date_obj = datetime.datetime(node.name, month_node.name, day_node.name,
                                                                             hour_node.name, minute_node.name,
                                                                             second_node.name)
                                                results.append(date_obj)
                            else:
                                raise ValueError('Datetime objects require time resolution at the moment.')
                else:
                    results.append(node.name)

        return results

    def is_add_to_current_checked(self):
        if self.add_to_current_node is None:
            return False
        return self.add_to_current_node.check_state == QtCore.Qt.CheckState.Checked.value

    def is_select_all_checked(self):
        if self.select_all_node is None:
            return False
        return self.select_all_node.check_state == QtCore.Qt.CheckState.Checked.value




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = SmartFilterDialog()
    test_data = [
        ["ONE", 1.0, 1, datetime.datetime(1990, 4, 29), True],
        ["TWO", 2.2, 2, smrt_consts.UNKNOWN_DATE, False],
        ["THREE", 3.3, 3, datetime.datetime(1990, 1, 13), True],
        ["FOUR", 0.9, 4, datetime.datetime(2021, 6, 6), False],
        ["FIVE", 74.3, 5, datetime.datetime(2020, 8, 3), False],
        ["SIX", 6.6, 6, None, True],  # date(1975, 4, 13)
        ["SEVEN", None, 7, datetime.datetime(1980, 7, 4), True],
        ["EIGHT", 82.1, 8, datetime.datetime(1990, 9, 11), False],
        ["NINE", -100.5, 9, datetime.datetime(1980, 8, 30), False],
        ["TEN", 121.2, 10, datetime.datetime(1990, 9, 4), True]
    ]
    cols = ['TEXT', 'NUMBER', 'TEST_INT', 'TEST_DATE', 'BOOL_TEST']
    df = pd.DataFrame(test_data, columns=cols)
    test_col = df['TEST_DATE']
    ret = win.show_window(test_col, test_col.name, smrt_consts.SmartDataTypes.DATE, [datetime.date(1980, 1, 1), None], None)
    result = {
        smrt_consts.SmartFilterAction.NO_ACTION: "Canceled",
        smrt_consts.SmartFilterAction.CLR_SORT: "Clear Sort",
        smrt_consts.SmartFilterAction.CLR_FILTER: "Clear Filter",
        smrt_consts.SmartFilterAction.SORT_ASCENDING: "Sort A to Z",
        smrt_consts.SmartFilterAction.SORT_DESCENDING: "Sort Z to A",
        smrt_consts.SmartFilterAction.NEW_FILTER: "New Filter",
        smrt_consts.SmartFilterAction.HIDE_COL: "Hide Col",
    }
    print(ret)
    print(result[win.action_requested])
    print(win.new_filter)
    # print(win.current_filter)
    app.quit()