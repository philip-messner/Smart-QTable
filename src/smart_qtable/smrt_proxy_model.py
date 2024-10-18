import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets
import pandas as pd

import typing

from smart_qtable import smrt_consts


class SmartProxyModel(QtCore.QSortFilterProxyModel):

    signal_filter_changed = QtCore.pyqtSignal()
    signal_sort_changed = QtCore.pyqtSignal()
    signal_hidden_columns_changed = QtCore.pyqtSignal()

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)

        self.table_sort_order: dict[str, QtCore.Qt.SortOrder] = {}
        self.table_filters: dict[str, list[typing.Any]] = {}
        self.hidden_cols: list[str] = []
        self.filter_mask: pd.Series = None
        self.setSortRole(smrt_consts.TABLE_SORT_ROLE)


    def lessThan(self, left_idx: QtCore.QModelIndex, right_idx: QtCore.QModelIndex) -> bool:
        left_sort_value = self.sourceModel().data(left_idx, smrt_consts.TABLE_SORT_ROLE)
        right_sort_value = self.sourceModel().data(right_idx, smrt_consts.TABLE_SORT_ROLE)
        # if pd.isnull(left_sort_value) and pd.isnull(right_sort_value):
        #     return False
        # if pd.isnull(left_sort_value):
        #     return True
        # if pd.isnull(right_sort_value):
        #     return False
        return left_sort_value < right_sort_value

    def on_model_reset(self):
        self.create_filter_mask()

    def create_filter_mask(self) -> None:
        model_df = self.sourceModel().smrt_df.data_df
        model_dtypes = self.sourceModel().smrt_df.dtypes
        if model_df is None:
            self.filter_mask = pd.Series()
            return
        self.filter_mask = pd.Series(True, index=model_df.index)
        if not self.table_filters:
            return
        for col_name, df_filter in self.table_filters.items():
            if None in df_filter:
                df_filter.remove(None)
                filt = pd.isnull(model_df[col_name]) | model_df[col_name].isin(df_filter)
                df_filter.append(None)
            else:
                filt = model_df[col_name].isin(df_filter)
            self.filter_mask = self.filter_mask & filt


    def set_hidden_cols(self, new_hidden_cols: list[str]) -> None:
        self.hidden_cols.clear()
        self.hidden_cols += new_hidden_cols
        for col in self.hidden_cols:
            if col in self.table_filters:
                self.set_filter_for_column(col, None)
            if col in self.table_sort_order:
                self.set_sort_for_column(col, None)
        self.invalidateColumnsFilter()
        self.signal_hidden_columns_changed.emit()

    def clear_hidden_cols(self) -> None:
        self.hidden_cols.clear()
        self.invalidateColumnsFilter()
        self.signal_hidden_columns_changed.emit()

    def filterAcceptsColumn(self, source_column, source_parent):
        column_name = self.sourceModel().headerData(section=source_column, orientation=QtCore.Qt.Orientation.Horizontal,
                                                    role=QtCore.Qt.ItemDataRole.DisplayRole)
        if column_name:
            return column_name not in self.hidden_cols
        return False

    def filterAcceptsRow(self, source_row, source_parent):
        return self.filter_mask.iloc[source_row]

    def set_filter_for_column(self, col_name: str, new_filter: list):
        if not new_filter:
            if col_name in self.table_filters:
                self.table_filters.pop(col_name)
                self.create_filter_mask()
                self.invalidateRowsFilter()
                self.signal_filter_changed.emit()
            return

        self.table_filters[col_name] = new_filter
        self.create_filter_mask()
        self.invalidateRowsFilter()
        self.signal_filter_changed.emit()

    def clear_filters(self) -> None:
        self.table_filters.clear()
        self.create_filter_mask()
        self.invalidateRowsFilter()
        self.signal_filter_changed.emit()

    def set_sort_for_column(self, col_name: str, sort_order: QtCore.Qt.SortOrder):
        if not sort_order:
            if col_name in self.table_sort_order:
                self.table_sort_order.pop(col_name)
                self.apply_sort()
                self.signal_sort_changed.emit()
            return

        self.table_sort_order[col_name] = sort_order
        self.apply_sort()
        self.signal_sort_changed.emit()

    def apply_sort(self) -> None:
        # self.sort(-1)
        model_df = self.sourceModel().smrt_df.data_df
        if model_df is None:
            return
        if not self.table_sort_order:
            self.sort(-1)
            return
        adjusted_columns = [col_name for col_name in model_df.columns if col_name not in self.hidden_cols]
        for cn, so in reversed(self.table_sort_order.items()):
            if cn not in adjusted_columns:
                continue
            self.sort(adjusted_columns.index(cn), so)


    def clear_sort(self, **kwargs) -> None:
        apply_sort = kwargs.get('apply_sort', True)
        self.table_sort_order.clear()
        if apply_sort:
            self.apply_sort()
        self.signal_sort_changed.emit()


    def column_num_from_name(self, col_name: str) -> int:
        if not col_name:
            return -1

        if self.sourceModel().smrt_df.data_df is None:
            return -1

        if col_name in self.hidden_cols:
            return -1

        if col_name not in self.sourceModel().smrt_df.data_df.columns:
            return -1

        return list(self.sourceModel().smrt_df.data_df.columns).index(col_name)
