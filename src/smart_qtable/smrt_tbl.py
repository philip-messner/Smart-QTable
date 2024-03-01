from PyQt6 import QtCore, QtWidgets, QtGui, QtPrintSupport
import pandas as pd
import win32com.client

import datetime
import logging
import pickle
import pathlib
import typing
import os

from smart_qtable import smrt_consts

from smart_qtable import smrt_tbl_view
from smart_qtable import smrt_hdr_view
from smart_qtable import smrt_custom_view
from smart_qtable import smrt_filter_win
from smart_qtable import smrt_data_model
from smart_qtable import smrt_save_view_win
from smart_qtable import smrt_adv_sort
from smart_qtable import smrt_support
from frameless_dialog import frmls_msgbx
from smart_qtable import smrt_summary_widget
from smart_qtable import smrt_proxy_model
from smart_qtable import smrt_dataframe


class SmartTable(QtWidgets.QWidget):
    """
    An instrumented table widget that can be used for data analysis.

    Properties
    ----------
    smrt_df: (SmartDataFrame) - the data container for the SmartTable
    refresh_dt: (datetime) - the datetime of when the data was valid

    Methods
    -------
    start_refresh_btn_animation(): starts the animated refresh button
    stop_refresh_btn_animation(): stops the animated refresh button
    set_table_mode(SmartTableMode): changes the behavior of the table instrumentation based on SmartTableMode provided
        (Not typically needed after instantiation)
    add_action_to_alt_toolbar(QAction): adds the provided QAction to the alternate toolbar
    add_seperator_to_alt_toolbar(QAction): adds a separator to the alternate toolbar before the provided QAction object
    add_spcr_to_alt_toolbar(int): adds the provided number of QSpacer objects to the alt toolbar
    add_table_action(QAction): adds the provided QAction to the table action toolbar
    add_seperator_to_table_actions(QAction): adds a seperator to the action toolbar before the provided QAction object
    add_spcr_to_table_actions(int): adds the provided number of QSpacer objects to the action toolbar
    """

    tbl_count = 0
    logger = logging.getLogger('smart_qtable')
    signal_start_refresh = QtCore.pyqtSignal()

    def __init__(self, smrt_df: smrt_dataframe.SmartDataFrame,  **kwargs):
        """
        Initializer for SmartTable object
        Args:
            smrt_df: (SmartDataFrame) the data container used by this table.
            **kwargs: optional keyword arguments:
                parent: (QWidget) the parent widget for this table (default = None)
                table_name: (str) an optional name for this table (default = 'Table_{id}')
                data_df: (Dataframe) initial table data (default = empty dataframe with columns derived by the dtypes
                    keys)
                table_flags: (SmartTableFlags) any SmartTableFlags set for this table (default = NO_FLAGS)
                editors: (dict[str, QStyledItemDelegate]) a dictionary mapping column names to specified item
                    delegates (default = empty dict)
                table_mode: (SmartTableMode) the specified mode for this table (default = DATA_MODE)
                alt_toolbar_actions: (list[QAction]) actions to be added to the alternative toolbar - only used when
                    table mode is ACTION_MODE (default = empty list)
                alt_toolbar_alignment: (str) the desired layout of actions added to the alternative toolbar. Options
                    are 'right', 'left' or 'center'. Invalid values result in right alignment (default = 'right')
                table_actions: (list[QAction]) actions to be added to the action toolbar (default = empty list)
                table_actions_alignment: (str) the desired layout of the action toolbar actions. Options are 'right',
                    'left' or 'center'. Invalid options result in center alignment. (default = 'center')
                summary_columns: (list[str]) a list of columns desired to be totalled/subtotalled in the summary widget.
                    Columns must be numeric datatypes. A max of 2 columns can be summarized unless the total sum option
                    is false, where the max is then 3 columns. (default = empty list)
                sum_record_count: (bool) flag to indicate whether to summarize the total number of records in the table.
                    This counts as 1 of the 3 max summary columns for the table. (default = True)
        """
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self._setup_table_ui()
        self._table_id = SmartTable.tbl_count
        SmartTable.tbl_count += 1

        # define/initialize member variables
        self.__smrt_df: smrt_dataframe.SmartDataFrame = smrt_df
        self.table_name: str = f'Table_{self._table_id}'
        self.summary_columns: list[smrt_summary_widget.Attribute] = []
        self.table_flags: smrt_consts.SmartTableFlags = smrt_consts.SmartTableFlags.NO_FLAG
        self.col_value_attrs: dict[str, smrt_consts.SmartValueAttributes] = kwargs.get('col_value_attrs', None) or {}
        self.editors: dict[str, QtWidgets.QStyledItemDelegate] = {}
        self.current_view: smrt_tbl_view.SmartTableView = None
        self.default_view: smrt_tbl_view.SmartTableView = None
        self.view_dict: dict[str, smrt_tbl_view.SmartTableView] = {}
        self.flag_respond_to_view_cmb: bool = False
        self.flag_respond_to_col_move: bool = True
        self.flag_excel_available: bool = True
        self.table_hdr = smrt_hdr_view.ExcelHeaderView(parent=self.table_view, sections_moveable=True)
        self.table_model = QtCore.QAbstractTableModel = None
        self.proxy_model: smrt_proxy_model.SmartProxyModel = None
        self.table_sel_model: QtCore.QItemSelectionModel = None
        self.custom_view_dialog = smrt_custom_view.SmartCustomizationDialog(parent=self)
        self.filter_dialog = smrt_filter_win.SmartFilterDialog(parent=self)
        self.view_save_dialog = smrt_save_view_win.SmartSaveViewDialog(parent=self)
        self.adv_sort_dialog = smrt_adv_sort.AdvSortDialog(parent=self)
        self.unavail_msgbox = smrt_support.UnavailDialog(parent=self)
        self.export_option_dialog = smrt_support.ExportOptionsDialog(parent=self)
        self.selected_idxs: list[typing.Any] = []
        self.refresh_dt: datetime.datetime = self.smrt_df.refresh_dt
        self.table_mode: smrt_consts.SmartTableMode = smrt_consts.SmartTableMode.DATA_MODE
        self.alt_toolbar_alignment = kwargs.get('alt_toolbar_alignment', 'right').lower()
        self.alt_toolbar_actions: list[QtGui.QAction] = kwargs.get('alt_toolbar_actions', None)
        if self.alt_toolbar_actions is None:
            self.alt_toolbar_actions = []
        self.table_actions_alignment = kwargs.get('table_actions_alignment', 'center').lower()
        self.table_actions: list[QtGui.QAction] = kwargs.get('table_actions', None)
        if self.table_actions is None:
            self.table_actions = []
        self.set_table_mode(kwargs.get('table_mode', smrt_consts.SmartTableMode.DATA_MODE))
        self._init_table_actions()

        self.table_name = kwargs.get('table_name', f'Table_{self._table_id}')

        self.default_view: smrt_tbl_view.SmartTableView = smrt_tbl_view.SmartTableView(
            'Default',
            [],
            list(self.smrt_df.dtypes.keys())
        )
        self.view_dict[self.default_view.name] = self.default_view
        saved_views: dict[str, smrt_tbl_view.SmartTableView] = self._load_view_dict_from_file()
        if saved_views:
            for v_name, v_obj in saved_views.items():
                self.view_dict[v_name] = v_obj
        self._populate_view_select_combo()

        self.current_view = self.default_view
        self.custom_view_dialog.set_window_data(self.current_view)
        self.cbo_view_select.setCurrentText(self.current_view.name)
        self.flag_respond_to_view_cmb: bool = True

        self.table_flags = kwargs.get('table_flags', smrt_consts.SmartTableFlags.NO_FLAG)
        if self.table_flags & smrt_consts.SmartTableFlags.EDITABLE_DATA:
            self.editors: dict[str, QtWidgets.QStyledItemDelegate] = kwargs.get('editors', None)
            if not self.editors:
                self.editors = {}
                # if no columns are set to be editable, clear the editable flags
                self.table_flags &= ~smrt_consts.SmartTableFlags.EDITABLE_DATA

        # validate the editable column names are column names in table
        for col_name in self.editors.keys():
            if col_name not in self.smrt_df.dtypes.keys():
                raise ValueError(f'Editor column \'{col_name}\' is not a column in this data table.')

        self.table_view.setHorizontalHeader(self.table_hdr)
        self.table_model = smrt_data_model.SmartDataModel(
            smrt_df=smrt_df,
            editable_cols=list(self.editors.keys()),
            col_value_attrs=self.col_value_attrs,
            parent=self
        )
        self.proxy_model = smrt_proxy_model.SmartProxyModel(parent=self)
        self.proxy_model.set_hidden_cols(self.current_view.hidden_cols)
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.on_model_reset()
        self.table_view.setModel(self.proxy_model)


        sum_record_count = kwargs.get('sum_record_count', True)
        if sum_record_count:
            sum_attr = smrt_summary_widget.Attribute(name=smrt_consts.RECORD_COUNT_NAME, dtype=smrt_consts.SmartDataTypes.INT)
            self.summary_columns.append(sum_attr)
        summary_columns: list[str] = kwargs.get('summary_columns', None)
        if summary_columns is None:
            summary_columns = []
        for summary_column in summary_columns:
            if summary_column not in self.smrt_df.dtypes.keys():
                raise ValueError(f'Cannot add summary column {summary_column}. It is not a member of this table.')
            selected_dtype = self.smrt_df.dtypes[summary_column]
            if selected_dtype != smrt_consts.SmartDataTypes.INT and selected_dtype != smrt_consts.SmartDataTypes.FLOAT and selected_dtype != smrt_consts.SmartDataTypes.ACCT:
                raise ValueError(f'Cannot add summary column {summary_column}. Data type must be numeric.')
            new_attr = smrt_summary_widget.Attribute(name=summary_column, dtype=selected_dtype)
            self.summary_columns.append(new_attr)
        self._setup_summary_widget()
        self.update_summary_totals()

        self.set_item_delegates()
        self.resize_table_cols()

        self.table_sel_model = self.table_view.selectionModel()

        # connect signals and slots
        self.cbo_view_select.currentTextChanged.connect(self.on_view_cbo_selection_change)
        self.table_hdr.clicked.connect(self.on_hdr_button)
        self.table_hdr.sectionMoved.connect(self.on_header_section_moved)
        self.btn_default_view.triggered.connect(lambda: self.set_current_view(self.default_view))
        self.btn_custom_view.triggered.connect(self.on_custom_view_btn)
        self.btn_save_view.clicked.connect(self.on_save_view_btn)
        self.btn_print_export.triggered.connect(self.on_print_table_btn)
        self.btn_custom_sort.triggered.connect(self.on_adv_sort_dialog_btn)
        self.btn_clear_filter.triggered.connect(self.on_clr_filters_button)
        self.btn_custom_filter.triggered.connect(self.on_advanced_filter_button)
        self.btn_export_excel.triggered.connect(self.on_export_to_excel_button)
        self.table_sel_model.selectionChanged.connect(self.on_selection_changed)
        self.btn_refresh_data.clicked.connect(lambda: self.signal_start_refresh.emit())
        self.table_model.modelReset.connect(self.proxy_model.on_model_reset)
        self.proxy_model.signal_filter_changed.connect(self.update_filter_totals)
        self.proxy_model.signal_filter_changed.connect(self.draw_column_icons)
        self.proxy_model.signal_sort_changed.connect(self.draw_column_icons)
        self.proxy_model.signal_hidden_columns_changed.connect(self.draw_column_icons)
        self.table_view.doubleClicked.connect(self.on_cell_double_clicked)
        self.table_model.dataChanged.connect(self.update_summary_totals)
        self.table_model.dataChanged.connect(self.update_summary_selected)
        self.table_model.dataChanged.connect(self.update_filter_totals)
        self.table_model.rowsRemoved.connect(self.update_summary_totals)
        self.table_model.rowsRemoved.connect(self.update_summary_selected)
        self.table_model.rowsRemoved.connect(self.update_filter_totals)

    @property
    def refresh_dt(self) -> datetime.datetime:
        return self.__smrt_df.refresh_dt

    @refresh_dt.setter
    def refresh_dt(self, new_dt: datetime.datetime) -> None:
        self.__smrt_df.refresh_dt = new_dt
        if self.__smrt_df.refresh_dt is not None:
            self.lbl_last_data_refresh.setText(f'Last refreshed: {self.__smrt_df.refresh_dt.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            self.lbl_last_data_refresh.setText('Last refreshed: ---> Never <---')

    @property
    def smrt_df(self) -> smrt_dataframe.SmartDataFrame:
        return self.__smrt_df

    @smrt_df.setter
    def smrt_df(self, new_smrt_df: smrt_dataframe.SmartDataFrame) -> None:

        self.__smrt_df = new_smrt_df
        self.proxy_model.clear_sort()
        self.proxy_model.clear_filters()
        self.proxy_model.beginResetModel()
        self.table_model.set_smrt_df(new_smrt_df)
        self.proxy_model.on_model_reset()
        self.proxy_model.endResetModel()
        self.refresh_dt = new_smrt_df.refresh_dt
        self.update_summary_totals()

    def start_refresh_btn_animation(self):
        self.btn_refresh_data.start()

    def stop_refresh_btn_animation(self):
        self.btn_refresh_data.stop()

    def set_action_toolbar(self, new_action_toolbar: QtWidgets.QToolBar) -> QtWidgets.QToolBar:
        old_action_toolbar = self.layout().replaceWidget(self.toolbar_table_actions, new_action_toolbar).widget()
        self.toolbar_table_actions = new_action_toolbar
        self.table_actions.clear()
        for new_action in new_action_toolbar.actions():
            self.table_actions.append(new_action)

        return old_action_toolbar

    def set_alt_toolbar(self, new_alt_toolbar: QtWidgets.QToolBar) -> QtWidgets.QToolBar:
        if self.table_mode != smrt_consts.SmartTableMode.ACTION_MODE:
            raise ValueError('You cannot set the alternate toolbar with the table_mode not in SmartTableMode.ACTION_MODE')
        old_alt_toolbar = self.layout().replaceWidget(self.alt_toolbar_actions, new_alt_toolbar).widget()
        self.toolbar_alternate = new_alt_toolbar
        self.alt_toolbar_actions.clear()
        for new_action in new_alt_toolbar.actions():
            self.alt_toolbar_actions.append(new_action)

        return old_alt_toolbar

    def set_table_mode(self, mode: smrt_consts.SmartTableMode):
        if self.table_mode == mode:
            return

        if mode == smrt_consts.SmartTableMode.ACTION_MODE:
            self.frm_data_refresh.setVisible(False)

            self.toolbar_alternate = QtWidgets.QToolBar(self)
            self.toolbar_alternate.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
            self.toolbar_alternate.setIconSize(QtCore.QSize(30, 30))

            old_tb = self.layout().replaceWidget(self.toolbar_default, self.toolbar_alternate).widget()
            old_tb.deleteLater()

            self.table_hdr.setSectionsMovable(False)
            self._init_alt_toolbar_actions()

        elif mode == smrt_consts.SmartTableMode.DATA_MODE:
            self.frm_data_refresh.setVisible(True)

            self.toolbar_default = QtWidgets.QToolBar(self)
            self.toolbar_default.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
            self.toolbar_default.setIconSize(QtCore.QSize(30, 30))

            old_tb = self.layout().replaceWidget(self.toolbar_alternate, self.toolbar_default).widget()
            old_tb.deleteLater()

            self.table_hdr.setSectionsMovable(True)
            self._init_default_toolbar()

    def add_action_to_alt_toolbar(self, new_action: QtGui.QAction):
        if not new_action:
            return

        if self.alt_toolbar_alignment == 'center':
            if not self.toolbar_alternate.actions():
                self.add_spcr_to_atl_toolbar()
            self.toolbar_alternate.addAction(new_action)
            self.add_spcr_to_atl_toolbar()

        elif self.alt_toolbar_alignment == 'right':
            if not self.toolbar_alternate.actions():
                self.add_spcr_to_atl_toolbar(2)
            self.toolbar_alternate.addAction(new_action)
        else:
            self.toolbar_alternate.clear()
            for alt_action in self.alt_toolbar_actions:
                self.toolbar_alternate.addAction(alt_action)
            self.toolbar_alternate.addAction(new_action)
            self.add_spcr_to_atl_toolbar(2)

        self.alt_toolbar_actions.append(new_action)

    def add_seperator_to_atl_toolbar(self, before_action: QtGui.QAction = None):
        current_action_list = self.toolbar_alternate.actions()
        if len(current_action_list) == 0:
            raise ValueError('You cannot add a seperator without any actions added.')
        if self.alt_toolbar_alignment == 'center':
            if current_action_list:
                self.toolbar_alternate.insertSeparator(current_action_list[0])
            else:
                self.toolbar_alternate.addSeparator()
                spcr = QtWidgets.QWidget(self.toolbar_alternate)
                spcr.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
                self.toolbar_alternate.addWidget(spcr)
        else:
            self.toolbar_alternate.addSeparator()

    def add_spcr_to_atl_toolbar(self, count: int = 1):
        for _ in range(count):
            spcr = QtWidgets.QWidget(self.toolbar_alternate)
            spcr.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
            self.toolbar_alternate.addWidget(spcr)

    def add_table_action(self, new_action: QtGui.QAction):
        if not new_action:
            return

        if self.table_actions_alignment == 'center':
            if not self.toolbar_table_actions.actions():
                self.add_spcr_to_table_actions()
            self.toolbar_table_actions.addAction(new_action)
            self.add_spcr_to_table_actions()

        elif self.table_actions_alignment == 'right':
            if not self.toolbar_table_actions.actions():
                self.add_spcr_to_table_actions(2)
            self.add_spcr_to_table_actions()
            self.toolbar_table_actions.addAction(new_action)
        else:
            self.toolbar_table_actions.clear()
            for tbl_action in self.table_actions:
                self.toolbar_table_actions.addAction(tbl_action)
                self.add_spcr_to_table_actions()
            self.toolbar_table_actions.addAction(new_action)
            self.add_spcr_to_table_actions(2)

        self.table_actions.append(new_action)

    def add_seperator_to_table_actions(self, before_action: QtGui.QAction = None):
        current_action_list = self.toolbar_table_actions.actions()
        if len(current_action_list) == 0:
            raise ValueError('You cannot add a seperator to a toolbar with no actions.')
        if self.table_actions_alignment == 'center':
            if current_action_list:
                self.toolbar_table_actions.insertSeparator(current_action_list[0])
            else:
                self.toolbar_table_actions.addSeparator()
                spcr = QtWidgets.QWidget(self.toolbar_table_actions)
                spcr.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
                self.toolbar_table_actions.addWidget(spcr)
        else:
            self.toolbar_table_actions.addSeparator()

    def add_spcr_to_table_actions(self, count: int = 1):
        for _ in range(count):
            spcr = QtWidgets.QWidget(self.toolbar_table_actions)
            spcr.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
            self.toolbar_table_actions.addWidget(spcr)

    def on_selection_changed(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        self.selected_idxs.clear()
        for idx in self.table_sel_model.selectedRows():
            model_idx = self.proxy_model.mapToSource(idx)
            df_idx = self.smrt_df.data_df.iloc[model_idx.row()].name
            self.selected_idxs.append(df_idx)
        self.update_summary_selected()

    def get_value_at_idx_and_col(self, idx: typing.Any, col_name: str):
        return self.smrt_df.data_df.loc[idx, col_name]

    def update_summary_selected(self):
        if not self.summary_columns:
            return

        for col in self.summary_columns:
            if self.smrt_df.data_df is None:
                self.summary_widget.update_attr_selected(col.name, 0)
            elif col.name.lower() == smrt_consts.RECORD_COUNT_NAME.lower():
                self.summary_widget.update_attr_selected(col.name, len(self.table_sel_model.selectedRows()))
            elif col.name in self.current_view.hidden_cols:
                self.summary_widget.update_attr_selected(col.name, 0)
            else:
                if not self.table_sel_model.selectedRows():
                    self.summary_widget.update_attr_selected(col.name, 0)
                else:
                    total = 0
                    for idx in self.selected_idxs:
                        val = self.smrt_df.data_df.loc[idx, col.name]
                        if pd.isnull(val):
                            val = 0
                        total += val
                    self.summary_widget.update_attr_selected(col.name, total)

    def update_summary_totals(self):
        if not self.summary_columns:
            return

        for col in self.summary_columns:
            if self.smrt_df.data_df is None:
                self.summary_widget.update_attr_total(col.name, 0)
            else:
                if col.name.lower() == smrt_consts.RECORD_COUNT_NAME.lower():
                    self.summary_widget.update_attr_total(col.name, self.smrt_df.data_df.shape[0])
                else:
                    self.summary_widget.update_attr_total(col.name, self.smrt_df.data_df[col.name].sum())

    def update_filter_totals(self):
        if not self.summary_columns:
            return

        for col in self.summary_columns:
            if self.smrt_df.data_df is None:
                self.summary_widget.update_attr_filtered(col.name, 0)
            elif not self.proxy_model.table_filters:
                self.summary_widget.update_attr_filtered(col.name, 0)
            elif col.name.lower() == smrt_consts.RECORD_COUNT_NAME.lower():
                self.summary_widget.update_attr_filtered(col.name, self.proxy_model.rowCount())
            elif col.name not in self.current_view.col_order:
                self.summary_widget.update_attr_filtered(col.name, 0)
            else:
                col_num = self.current_view.col_order.index(col.name)
                tot_val = 0
                for row_num in range(self.proxy_model.rowCount()):
                    mod_idx = self.proxy_model.index(row_num, col_num)
                    val = self.proxy_model.data(mod_idx, QtCore.Qt.ItemDataRole.EditRole)
                    if pd.isnull(val):
                        val = 0
                    tot_val += val
                self.summary_widget.update_attr_filtered(col.name, tot_val)

    def create_data_view(self) -> pd.DataFrame:

        data_view = self.smrt_df.data_df.copy(deep=True)

        data_view = data_view.loc[:, self.current_view.col_order]

        if self.proxy_model.table_sort_order:
            cols = []
            sort_orders = []
            for col_name, sort_order in self.proxy_model.table_sort_order.items():
                cols.append(col_name)
                if sort_order == QtCore.Qt.SortOrder.AscendingOrder:
                    sort_orders.append(True)
                else:
                    sort_orders.append(False)
            data_view = data_view.sort_values(
                by=cols,
                ascending=sort_orders,
                na_position='last'
            )

        # apply the dataframe filters
        if self.proxy_model.table_filters:
            for col_name, df_filter in self.proxy_model.table_filters.items():
                if None in df_filter:
                    df_filter.remove(None)
                    filt = pd.isnull(data_view[col_name]) | data_view[col_name].isin(df_filter)
                    df_filter.append(None)
                else:
                    filt = data_view[col_name].isin(df_filter)
                data_view = data_view[filt]

        return data_view

    @QtCore.pyqtSlot()
    def draw_column_icons(self):
        for logical_idx, col_name in enumerate(self.smrt_df.data_df.columns):
            if col_name in self.current_view.hidden_cols:
                return

            if col_name in self.proxy_model.table_filters and col_name in self.proxy_model.table_sort_order:
                if self.proxy_model.table_sort_order[col_name] == QtCore.Qt.SortOrder.AscendingOrder:
                    self.table_hdr.set_column_icon(logical_idx, smrt_consts.HdrBtnIcons.FILTER_SORT_ASCENDING)
                else:
                    self.table_hdr.set_column_icon(logical_idx, smrt_consts.HdrBtnIcons.FILTER_SORT_DESCENDING)
            elif col_name in self.proxy_model.table_filters:
                self.table_hdr.set_column_icon(logical_idx, smrt_consts.HdrBtnIcons.FILTER)
            elif col_name in self.proxy_model.table_sort_order:
                if self.proxy_model.table_sort_order[col_name] == QtCore.Qt.SortOrder.AscendingOrder:
                    self.table_hdr.set_column_icon(logical_idx, smrt_consts.HdrBtnIcons.SORT_ASCENDING)
                else:
                    self.table_hdr.set_column_icon(logical_idx, smrt_consts.HdrBtnIcons.SORT_DESCENDING)
            else:
                self.table_hdr.set_column_icon(logical_idx, smrt_consts.HdrBtnIcons.DEFAULT)

    def set_item_delegates(self):
        for idx, col_name in enumerate(self.current_view.col_order):
            if col_name in self.editors:
                self.table_view.setItemDelegateForColumn(idx, self.editors[col_name])
            else:
                self.table_view.setItemDelegateForColumn(idx, None)

    def resize_table_cols(self):
        if self.smrt_df.data_df is not None:
            num_cols = len(self.current_view.col_order)
            if self.table_view.verticalScrollBar().isVisible():
                calc_width = int((self.table_view.width() - self.table_view.verticalScrollBar().width()) / num_cols)
            else:
                calc_width = int(self.table_view.width() / num_cols)
            if calc_width < smrt_consts.MIN_COLUMN_WIDTH:
                calc_width = smrt_consts.MIN_COLUMN_WIDTH
            for i in range(num_cols):
                self.table_hdr.resizeSection(i, calc_width)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.resize_table_cols()
        super().resizeEvent(a0)

    @QtCore.pyqtSlot(str)
    def on_view_cbo_selection_change(self, current_txt: str):
        if not self.flag_respond_to_view_cmb:
            return

        # if the custom... entry is in the cbo, remove it.
        idx = self.cbo_view_select.findText(smrt_consts.CUSTOM_VIEW_NAME)
        if idx != -1:
            self.cbo_view_select.removeItem(idx)

        selected_view: smrt_tbl_view.SmartTableView = self.cbo_view_select.currentData()
        self.logger.debug(f'Selected view: {selected_view.name}')
        self.set_current_view(selected_view)

    def set_current_view(self, new_view: smrt_tbl_view.SmartTableView):
        if new_view == self.current_view:
            return

        # check to see if the new view is the same as any other saved view. If so, set that as the current view, else mark as custom...
        self.flag_respond_to_view_cmb = False
        view_found = False
        for view_name, view_obj in self.view_dict.items():
            if new_view == view_obj:
                self.cbo_view_select.setCurrentText(view_name)
                view_found = True
                new_view = view_obj
                idx = self.cbo_view_select.findText(smrt_consts.CUSTOM_VIEW_NAME)
                if idx != -1:
                    self.cbo_view_select.removeItem(idx)
                self.btn_save_view.setEnabled(False)
                break

        if not view_found:
            new_view.name = smrt_consts.CUSTOM_VIEW_NAME
            idx = self.cbo_view_select.findText(smrt_consts.CUSTOM_VIEW_NAME)
            if idx == -1:
                self.cbo_view_select.addItem(new_view.name, new_view)
                self.cbo_view_select.setCurrentText(new_view.name)
                self.btn_save_view.setEnabled(True)
            else:
                self.cbo_view_select.setItemData(idx, new_view)
        self.flag_respond_to_view_cmb = True

        self.proxy_model.set_hidden_cols(new_view.hidden_cols)
        self.current_view = new_view
        self.reorder_table_cols()
        # self.reset_item_delegates()
        self.custom_view_dialog.set_window_data(new_view)

    def reorder_table_cols(self):
        self.proxy_model.clear_hidden_cols()

        # for logical_idx, col_name in enumerate(self.data_df.columns):
        #     if col_name in self.current_view.hidden_cols:
        #         continue
        #     current_visual_idx = self.hdr_view.visualIndex(logical_idx)
        #     new_visual_idx = self.current_view.col_order.index(col_name)
        #     if new_visual_idx != current_visual_idx:
        #         self.flag_respond_to_col_move = False
        #         self.hdr_view.moveSection(current_visual_idx, new_visual_idx)
        #         self.flag_respond_to_col_move = True
        for new_pos, col in enumerate(self.current_view.col_order):
            # find the logical index for each desired element
            logical_idx = list(self.smrt_df.data_df.columns).index(col)

            # find the current visual index for each element
            curr_idx = self.table_hdr.visualIndex(logical_idx)
            if new_pos != curr_idx:
                self.flag_respond_to_col_move = False
                self.table_hdr.moveSection(curr_idx, new_pos)
                self.flag_respond_to_col_move = True

        self.proxy_model.set_hidden_cols(self.current_view.hidden_cols)

    @QtCore.pyqtSlot()
    def on_custom_view_btn(self):
        accepted = self.custom_view_dialog.show_window()
        if accepted:
            self.set_current_view(self.custom_view_dialog.get_view_on_state())

    @QtCore.pyqtSlot()
    def on_print_table_btn(self, **kwargs):
        printer_obj = QtPrintSupport.QPrinter()
        page_layout_obj = printer_obj.pageLayout()
        page_layout_obj.setOrientation(QtGui.QPageLayout.Orientation.Landscape)
        print_dialog = QtPrintSupport.QPrintDialog(printer_obj, parent=self)

        export_df = self.create_data_view()

        replace_tokens = kwargs.get('replace_tokens', True)
        if replace_tokens:
            export_df = export_df.replace(smrt_consts.UNKNOWN_DATE, 'UNKNOWN')
            export_df = export_df.replace(smrt_consts.INVALID_DATE, 'INVALID')

            # export table data to excel
        data_folder = SmartTable.get_default_app_data_path()
        temp_file = pathlib.Path.joinpath(data_folder, 'temp.xlsx')
        export_df.to_excel(
            temp_file,
            index=False,
            engine='xlsxwriter'
        )
        self.logger.debug('Dataframe exported to temporary excel file.')

        excel_app = win32com.client.DispatchEx('Excel.Application')
        self.logger.debug('Excel application loaded.')

        excel_app.Visible = False
        wb = excel_app.Workbooks.Open(temp_file)
        self.logger.debug('Temp file is loaded into excel')
        ws = wb.Sheets('Sheet1')
        wb.Sheets('Sheet1').Activate()
        ws.Columns.AutoFit()
        ws.UsedRange.Select()
        ws.ListObjects.Add().TableStyle = "TableStyleMedium7"
        ws.UsedRange.VerticalAlignment = smrt_consts.ExcelVerticalAlignment.CENTER
        ws.UsedRange.HorizontalAlignment = smrt_consts.ExcelHorizontalAlignment.CENTER
        ws.PageSetup.Zoom = False
        ws.PageSetup.FitToPagesWide = 1
        ws.PageSetup.FitToPagesTall = False
        ws.PageSetup.Orientation = smrt_consts.ExcelPageOrientation.LANDSCAPE

        num_printed_pages = ws.PageSetup.Pages.Count
        print_dialog.setMinMax(1, num_printed_pages)
        print_dialog.setFromTo(1, num_printed_pages)

        accepted = print_dialog.exec()
        if accepted:
            if printer_obj.printRange() == QtPrintSupport.QPrinter.PrintRange.PageRange:
                ws.PrintOut(From=printer_obj.fromPage(), To=printer_obj.toPage(), ActivePrinter=printer_obj.printerName())
            else:
                ws.PrintOut(ActivePrinter=printer_obj.printerName())

            self.logger.debug(f'Table has been sent to printer: {printer_obj.printerName()}')
        wb.Close(True)
        excel_app.Quit()
        pathlib.Path.unlink(temp_file)
        self.logger.debug('Excel application closed.')

    @QtCore.pyqtSlot()
    def on_adv_sort_dialog_btn(self):
        visible_cols: list[str] = []
        visible_cols += self.current_view.col_order
        column_dict: dict[int, str] = {}
        full_column_list: list[str] = list(self.current_view.col_order)
        for column_name in visible_cols:
            column_dict[full_column_list.index(column_name)] = column_name

        column_dtypes = self.smrt_df.dtypes

        sort_list: list[tuple[int, QtCore.Qt.SortOrder]] = []
        for entry, so in self.proxy_model.table_sort_order.items():
            sort_list.append((full_column_list.index(entry), so))

        accepted = self.adv_sort_dialog.show_dialog(column_dict, sort_list, column_dtypes)
        if accepted:
            new_sort_tuple_list = self.adv_sort_dialog.get_current_sort()

            self.proxy_model.clear_sort()
            for col_idx, sort_order in new_sort_tuple_list:
                self.proxy_model.set_sort_for_column(full_column_list[col_idx], sort_order)

    @QtCore.pyqtSlot()
    def on_clr_filters_button(self):
        self.proxy_model.clear_filters()

    @QtCore.pyqtSlot()
    def on_export_to_excel_button(self, **kwargs):
        if self.smrt_df.data_df is None or self.smrt_df.data_df.shape[0] == 0:
            msgbx = frmls_msgbx.FramelessMsgBx(parent=self)
            msgbx.setWindowTitle('No data to export')
            msgbx.setText('There is no data available to export')
            msgbx.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msgbx.exec()
            return

        export_df: pd.DataFrame

        if not self.proxy_model.table_filters and not self.proxy_model.table_sort_order and not self.current_view.hidden_cols:
            export_df = self.create_data_view()

        else:
            accepted = self.export_option_dialog.exec()
            if not accepted:
                return
            if self.export_option_dialog.selection == smrt_support.ExportOptionsDialog.SelectionOption.EXPORT_FULL:
                export_df = self.smrt_df.data_df.copy(deep=True)
            elif self.export_option_dialog.selection == smrt_support.ExportOptionsDialog.SelectionOption.EXPORT_CURRENT:
                export_df = self.create_data_view()
            else:
                return

        replace_tokens = kwargs.get('replace_tokens', True)
        if replace_tokens:
            export_df = export_df.replace(smrt_consts.UNKNOWN_DATE, 'UNKNOWN')
            export_df = export_df.replace(smrt_consts.INVALID_DATE, 'INVALID')

        file_dialog = QtWidgets.QFileDialog(parent=self)
        file_dialog.setDefaultSuffix('xlsx')
        file_name, _ = file_dialog.getSaveFileName(self, "Select a save location", "table_data.xlsx",
                                         "Excel Files (*.xlsx *.xls)")

        if file_name:
            file_path = pathlib.Path(file_name)
            export_df.to_excel(file_path, index=False, engine='xlsxwriter')

            excel_app = win32com.client.DispatchEx('Excel.Application')
            self.logger.debug('Excel application loaded.')
            excel_app.Visible = False
            wb = excel_app.Workbooks.Open(file_path)
            self.logger.debug('Temp file is loaded into excel')
            ws = wb.Sheets('Sheet1')
            wb.Sheets('Sheet1').Activate()
            ws.Columns.AutoFit()
            ws.UsedRange.Select()
            ws.ListObjects.Add().TableStyle = "TableStyleMedium7"
            ws.UsedRange.VerticalAlignment = smrt_consts.ExcelVerticalAlignment.CENTER
            ws.UsedRange.HorizontalAlignment = smrt_consts.ExcelHorizontalAlignment.CENTER
            ws.PageSetup.Zoom = False
            ws.PageSetup.FitToPagesWide = 1
            ws.PageSetup.FitToPagesTall = False
            ws.PageSetup.Orientation = smrt_consts.ExcelPageOrientation.LANDSCAPE

            wb.Close(True)
            excel_app.Quit()


    @QtCore.pyqtSlot()
    def on_advanced_filter_button(self):
        self.unavail_msgbox.exec()


    @QtCore.pyqtSlot(int)
    def on_hdr_button(self, col_num: int):
        col_num = self.table_hdr.visualIndex(col_num)
        # self.proxy_model.sort(2)
        # return
        col_name = self.current_view.col_order[col_num]
        self.logger.debug(f'\'on_hdr_button method\': Column {col_num} Column Name: {col_name}')
        if col_name in self.proxy_model.table_filters:
            curr_filter = self.proxy_model.table_filters[col_name]
        else:
            curr_filter = None
        if col_name in self.proxy_model.table_sort_order:
            curr_sort = self.proxy_model.table_sort_order[col_name]
        else:
            curr_sort = None
        filt_width = self.filter_dialog.width()
        filt_height = self.filter_dialog.height()
        header_x = self.table_view.horizontalHeader().mapToGlobal(QtCore.QPoint(0, 0)).x()
        header_y = self.table_view.horizontalHeader().mapToGlobal(QtCore.QPoint(0, 0)).y()
        x_pos = header_x + self.table_hdr.sectionViewportPosition(self.table_hdr.logicalIndex(col_num))
        y_pos = header_y + self.table_hdr.geometry().y() + self.table_hdr.height()
        max_x = header_x + self.table_view.width()
        if x_pos + filt_width > max_x:
            x_pos = max_x - filt_width
        self.filter_dialog.setGeometry(x_pos, y_pos, filt_width, filt_height)
        temp_filters = self.proxy_model.table_filters.copy()
        if col_name in temp_filters:
            del temp_filters[col_name]
            # temp_filters.pop(col_name)

        filtered_df = self.smrt_df.data_df.copy(deep=True)
        if temp_filters:
            for cn, df_filter in temp_filters.items():
                if None in df_filter:
                    df_filter.remove(None)
                    filt = pd.isnull(filtered_df[cn]) | filtered_df[cn].isin(df_filter)
                    df_filter.append(None)
                else:
                    filt = filtered_df[cn].isin(df_filter)
                filtered_df = filtered_df[filt]

        # show the filter window
        if self.smrt_df.dtypes[col_name] == smrt_consts.SmartDataTypes.DATE_TIME:
            time_res = True
        else:
            time_res = False
        if self.table_mode == smrt_consts.SmartTableMode.ACTION_MODE:
            self.filter_dialog.btn_hide_col.setVisible(False)
        else:
            self.filter_dialog.btn_hide_col.setVisible(True)

        value_attrs = self.col_value_attrs.get(col_name, smrt_consts.SmartValueAttributes())
        accepted = self.filter_dialog.show_window(
            column_data=filtered_df[col_name],
            column_name=col_name,
            dtype=self.smrt_df.dtypes[col_name],
            current_filter=curr_filter,
            current_sort_order=curr_sort,
            time_resolution=time_res,
            value_attrs=value_attrs
        )
        self.logger.debug(f'Accepted? {accepted}')
        if accepted and self.filter_dialog.action_requested == smrt_consts.SmartFilterAction.NEW_FILTER:
            self.proxy_model.set_filter_for_column(col_name, self.filter_dialog.new_filter)
        elif self.filter_dialog.action_requested == smrt_consts.SmartFilterAction.CLR_FILTER:
            self.proxy_model.set_filter_for_column(col_name, None)
        elif self.filter_dialog.action_requested == smrt_consts.SmartFilterAction.CLR_SORT:
            self.proxy_model.clear_sort()
        elif self.filter_dialog.action_requested == smrt_consts.SmartFilterAction.SORT_ASCENDING:
            self.proxy_model.clear_sort(apply_sort=False)
            self.proxy_model.set_sort_for_column(col_name, QtCore.Qt.SortOrder.AscendingOrder)
        elif self.filter_dialog.action_requested == smrt_consts.SmartFilterAction.SORT_DESCENDING:
            self.proxy_model.clear_sort(apply_sort=False)
            self.proxy_model.set_sort_for_column(col_name, QtCore.Qt.SortOrder.DescendingOrder)
        elif self.filter_dialog.action_requested == smrt_consts.SmartFilterAction.HIDE_COL:
            new_hidden_cols = self.current_view.hidden_cols.copy()
            new_hidden_cols.append(col_name)
            new_col_ord = self.current_view.col_order.copy()
            new_col_ord.remove(col_name)
            new_view = smrt_tbl_view.SmartTableView(
                name=smrt_consts.CUSTOM_VIEW_NAME,
                hidden_cols=new_hidden_cols,
                col_order=new_col_ord
            )
            self.set_current_view(new_view)
        else:
            return None


    @QtCore.pyqtSlot(int, int, int)
    def on_header_section_moved(self, col_num: int, old_pos: int, new_pos: int):
        if not self.flag_respond_to_col_move:
            return
        self.logger.debug(f'Column header {col_num} moved from {old_pos} to {new_pos}')

        new_col_order = []
        for i in range(self.table_hdr.count()):
            logical_idx = self.table_hdr.logicalIndex(i)
            col_name = self.proxy_model.headerData(logical_idx, QtCore.Qt.Orientation.Horizontal)
            new_col_order.append(col_name)

        new_view = smrt_tbl_view.SmartTableView(
            name=smrt_consts.CUSTOM_VIEW_NAME,
            hidden_cols=self.current_view.hidden_cols.copy(),
            col_order=new_col_order
        )
        self.set_current_view(new_view)

    def _populate_view_select_combo(self) -> None:
        for v_name, v_obj in self.view_dict.items():
            self.cbo_view_select.addItem(v_name, v_obj)
        
    def _load_view_dict_from_file(self) -> dict[str, smrt_tbl_view.SmartTableView]:
        user_data_folder = SmartTable.get_default_app_data_path()
        table_pickle = pathlib.Path.joinpath(user_data_folder, self.table_name + '.pkl')
        if table_pickle.is_file():
            with open(table_pickle, 'rb') as f:
                try:
                    return pickle.load(f)
                except pickle.PickleError:
                    self.logger.debug('Pickle read error')
        return {}

    def _save_view_dict_to_file(self) -> bool:
        user_data_folder = SmartTable.get_default_app_data_path()
        success = False
        table_pickle = pathlib.Path.joinpath(user_data_folder, self.table_name + '.pkl')
        dict_without_default = self.view_dict.copy()
        dict_without_default.pop(self.default_view.name)
        with open(table_pickle, 'wb') as f:
            try:
                pickle.dump(dict_without_default, f)
                return True
            except pickle.PickleError:
                self.logger.debug('Pickle error')
        return False

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_cell_double_clicked(self, idx: QtCore.QModelIndex):
        # model_idx = self.proxy_model.mapToSource(idx)
        val = self.proxy_model.data(idx)
        # val = self.table_model.smrt_df.data_df.iloc[model_idx.row(), model_idx.column()]
        app = QtGui.QGuiApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(val)
        # print(model_idx.row(), model_idx.column())
        # idx = self.proxy_model.mapFromSource(idx)
        # print(self.table_model.data(idx, role=QtCore.Qt.ItemDataRole.DisplayRole))

    @QtCore.pyqtSlot()
    def on_save_view_btn(self):
        accepted = self.view_save_dialog.show_me(list(self.view_dict.keys()))
        if accepted:
            new_view = smrt_tbl_view.SmartTableView(
                name=self.view_save_dialog.line_edit_view_name.text().strip().title(),
                hidden_cols=self.current_view.hidden_cols,
                col_order=self.current_view.col_order
            )
            self.view_dict[new_view.name] = new_view
            self._save_view_dict_to_file()
            self.cbo_view_select.addItem(new_view.name, new_view)
            self.cbo_view_select.setCurrentText(new_view.name)

    def _init_default_toolbar(self):
        self.frm_view_select = QtWidgets.QFrame(self.toolbar_default)
        self.layout_frm_view_select = QtWidgets.QHBoxLayout(self.frm_view_select)
        self.lbl_view_select = QtWidgets.QLabel('Select view: ', self.frm_view_select)
        self.layout_frm_view_select.addWidget(self.lbl_view_select)
        self.cbo_view_select = QtWidgets.QComboBox(self.frm_view_select)
        self.cbo_view_select.setMinimumContentsLength(15)
        self.cbo_view_select.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.layout_frm_view_select.addWidget(self.cbo_view_select)
        self.btn_save_view = QtWidgets.QToolButton(self.frm_view_select)
        self.btn_save_view.setObjectName('btn_save_view')
        self.btn_save_view.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btn_save_view.setIcon(QtGui.QIcon(':/save-icon.png'))
        self.btn_save_view.setIconSize(QtCore.QSize(18, 18))
        self.btn_save_view.setToolTip('Save view')
        self.btn_save_view.setStyleSheet('#btn_save_view:!hover {border: none;}')
        self.btn_save_view.setEnabled(False)

        self.layout_frm_view_select.addWidget(self.btn_save_view)

        spcr13 = QtWidgets.QWidget(self.toolbar_default)
        spcr13.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr13)
        self.toolbar_default.addWidget(self.frm_view_select)
        spcr14 = QtWidgets.QWidget(self.toolbar_default)
        spcr14.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr14)
        self.toolbar_default.addSeparator()

        spcr11 = QtWidgets.QWidget(self.toolbar_default)
        spcr11.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr11)

        self.btn_print_export = QtGui.QAction(self.toolbar_default)
        self.btn_print_export.setIcon(QtGui.QIcon(':/print.png'))
        self.btn_print_export.setToolTip('Print Table')
        self.toolbar_default.addAction(self.btn_print_export)

        spcr12 = QtWidgets.QWidget(self.toolbar_default)
        spcr12.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr12)

        self.toolbar_default.addSeparator()

        spcr = QtWidgets.QWidget(self.toolbar_default)
        spcr.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr)

        self.btn_export_excel = QtGui.QAction(self.toolbar_default)
        self.btn_export_excel.setIcon(QtGui.QIcon(':/excel.png'))
        self.btn_export_excel.setToolTip('Export Excel')
        self.toolbar_default.addAction(self.btn_export_excel)
        spcr2 = QtWidgets.QWidget(self.toolbar_default)
        spcr2.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr2)
        self.toolbar_default.addSeparator()
        spcr3 = QtWidgets.QWidget(self.toolbar_default)
        spcr3.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr3)

        self.btn_custom_sort = QtGui.QAction(self.toolbar_default)
        self.btn_custom_sort.setIcon(QtGui.QIcon(':/advanced_sort.PNG'))
        self.btn_custom_sort.setToolTip('Custom Sort')
        self.toolbar_default.addAction(self.btn_custom_sort)
        spcr4 = QtWidgets.QWidget(self.toolbar_default)
        spcr4.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr4)
        self.toolbar_default.addSeparator()
        spcr5 = QtWidgets.QWidget(self.toolbar_default)
        spcr5.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr5)
        self.btn_custom_filter = QtGui.QAction(self.toolbar_default)
        self.btn_custom_filter.setIcon(QtGui.QIcon(':/filter.PNG'))
        self.btn_custom_filter.setToolTip('Custom Filter')
        self.toolbar_default.addAction(self.btn_custom_filter)
        spcr6 = QtWidgets.QWidget(self.toolbar_default)
        spcr6.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr6)
        self.btn_clear_filter = QtGui.QAction(self.toolbar_default)
        self.btn_clear_filter.setIcon(QtGui.QIcon(':/clear_filter.PNG'))
        self.btn_clear_filter.setToolTip('Clear ALL Filters')
        self.toolbar_default.addAction(self.btn_clear_filter)
        spcr7 = QtWidgets.QWidget(self.toolbar_default)
        spcr7.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr7)
        self.toolbar_default.addSeparator()
        spcr8 = QtWidgets.QWidget(self.toolbar_default)
        spcr8.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr8)
        self.btn_custom_view = QtGui.QAction(self.toolbar_default)
        self.btn_custom_view.setIcon(QtGui.QIcon(':/custom_view.png'))
        self.btn_custom_view.setToolTip('Custom View')
        self.toolbar_default.addAction(self.btn_custom_view)
        spcr9 = QtWidgets.QWidget(self.toolbar_default)
        spcr9.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr9)
        self.btn_default_view = QtGui.QAction(self.toolbar_default)
        self.btn_default_view.setIcon(QtGui.QIcon(':/default_view.png'))
        self.btn_default_view.setToolTip('Default View')
        self.toolbar_default.addAction(self.btn_default_view)
        spcr10 = QtWidgets.QWidget(self.toolbar_default)
        spcr10.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.toolbar_default.addWidget(spcr10)

    def _init_alt_toolbar_actions(self):
        if not self.alt_toolbar_actions:
            return

        if self.alt_toolbar_alignment == 'center':
            for alt_action in self.alt_toolbar_actions:
                self.add_spcr_to_atl_toolbar()
                self.toolbar_alternate.addAction(alt_action)
            self.add_spcr_to_atl_toolbar()
        elif self.alt_toolbar_alignment == 'left':
            for alt_action in self.alt_toolbar_actions:
                self.toolbar_alternate.addAction(alt_action)
            self.add_spcr_to_atl_toolbar(2)
        else:
            self.add_spcr_to_atl_toolbar(2)
            for alt_action in self.alt_toolbar_actions:
                self.toolbar_alternate.addAction(alt_action)

    def _init_table_actions(self):
        if not self.table_actions:
            return
        if self.table_actions_alignment == 'left':
            for tbl_action in self.table_actions:
                self.toolbar_table_actions.addAction(tbl_action)
                self.add_spcr_to_table_actions()
            self.add_spcr_to_table_actions(2)
        elif self.table_actions_alignment == 'right':
            self.add_spcr_to_table_actions(2)
            for tbl_action in self.table_actions:
                self.add_spcr_to_table_actions()
                self.toolbar_table_actions.addAction(tbl_action)
        else:
            for tbl_action in self.table_actions:
                self.add_spcr_to_table_actions()
                self.toolbar_table_actions.addAction(tbl_action)
            self.add_spcr_to_table_actions()

    def _setup_summary_widget(self):
        for sum_attr in self.summary_columns:
            self.summary_widget.add_attr(sum_attr)

    def _determine_excel_available(self) -> None:
        try:
            excel = win32com.client.DispatchEx('Excel.Application')
        except:
            self.flag_excel_available = False
            self.btn_export_excel.setEnabled(False)
            self.btn_print_export.setEnabled(False)
            return
        excel.quit()
        self.flag_excel_available = True
        self.btn_print_export.setEnabled(True)
        return

    @staticmethod
    def get_default_app_data_path() -> pathlib.Path:
        user_data_folder = pathlib.Path(os.getenv('APPDATA'))

        app_name = os.getenv('APP_NAME')
        if not app_name or not isinstance(app_name, str):
            app_name = smrt_consts.DEFAULT_APP_NAME
        else:
            app_name = app_name.replace(' ', '_')

        company_name = os.getenv('COMPANY_NAME')
        if company_name and isinstance(company_name, str):
            company_name = company_name.replace(' ', '_')
            pathlib.Path.joinpath(user_data_folder, company_name).mkdir(exist_ok=True)
            pathlib.Path.joinpath(user_data_folder, company_name, app_name).mkdir(exist_ok=True)
            app_folder_path = pathlib.Path.joinpath(user_data_folder, company_name, app_name)
        else:
            pathlib.Path.joinpath(user_data_folder, app_name).mkdir(exist_ok=True)
            app_folder_path = pathlib.Path.joinpath(user_data_folder, app_name)

        data_folder = os.getenv('DATA_FOLDER')
        if not data_folder or not isinstance(data_folder, str):
            data_folder = smrt_consts.DATA_DIR
        pathlib.Path.joinpath(app_folder_path, data_folder).mkdir(exist_ok=True)
        data_path = pathlib.Path.joinpath(app_folder_path, data_folder)

        return data_path

    def _setup_table_ui(self):
        self.setObjectName(f'smart_qtable')
        layout_smart_tableview = QtWidgets.QVBoxLayout(self)
        layout_smart_tableview.setContentsMargins(0, 0, 0, 0)
        layout_smart_tableview.setSpacing(0)

        self.frm_data_refresh = QtWidgets.QFrame(self)
        self.layout_frm_data_refresh = QtWidgets.QHBoxLayout(self.frm_data_refresh)
        self.btn_refresh_data = smrt_support.AnimatedToolButton(
            animated=':/animated_refresh.gif',
            static=':/static_refresh.png',
            parent=self.frm_data_refresh
        )
        self.btn_refresh_data.setObjectName('btn_refresh_data')
        self.btn_refresh_data.setIconSize(QtCore.QSize(30, 30))
        self.btn_refresh_data.setStyleSheet('#btn_refresh_data:!hover {border: none;}')
        self.btn_refresh_data.setToolTip('Refresh Data')
        self.layout_frm_data_refresh.addWidget(self.btn_refresh_data)
        self.lbl_last_data_refresh = QtWidgets.QLabel(self.frm_data_refresh)
        self.lbl_last_data_refresh.setText('Last refresh: ---> Never <---')
        self.layout_frm_data_refresh.addWidget(self.lbl_last_data_refresh)
        self.layout_frm_data_refresh.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        )
        layout_smart_tableview.addWidget(self.frm_data_refresh)

        # ------------- define the default toolbar ----------------------------------
        self.toolbar_default = QtWidgets.QToolBar(self)
        self.toolbar_default.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.toolbar_default.setIconSize(QtCore.QSize(30, 30))

        self._init_default_toolbar()

        layout_smart_tableview.addWidget(self.toolbar_default)
        # end ------------- define the default toolbar ----------------------------------

        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setObjectName('table_view')
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.verticalHeader().hide()
        self.table_view.setStyleSheet('QTableview#table_view {color: red;}')
        layout_smart_tableview.addWidget(self.table_view)

        self.toolbar_table_actions = QtWidgets.QToolBar(self)
        layout_smart_tableview.addWidget(self.toolbar_table_actions)

        self.summary_widget = smrt_summary_widget.SmartSummaryWidget(parent=self)
        layout_smart_tableview.addWidget(self.summary_widget)
        self.setLayout(layout_smart_tableview)

