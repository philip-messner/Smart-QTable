from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QModelIndex, Qt
import pandas as pd

import logging
import typing

from smart_qtable import smrt_consts
from smart_qtable import smrt_dataframe


class SmartDataModel(QtCore.QAbstractTableModel):

    logger = logging.getLogger("smart_qtable.model")

    def __init__(self, smrt_df: smrt_dataframe.SmartDataFrame, *args, **kwargs) -> None:
        parent = kwargs.get("parent", None)
        super().__init__(parent=parent)
        self.smrt_df: smrt_dataframe.SmartDataFrame = smrt_df
        self.editable_cols: list[str] = kwargs.get("editable_cols", None) or []
        self.col_value_attrs: dict[str, smrt_consts.SmartValueAttributes] = (
            kwargs.get("col_value_attrs", None) or {}
        )

    def update_df_cell_value(
        self, df_idx: typing.Any, col_name: str, new_val: typing.Any
    ):
        col_num = list(self.smrt_df.data_df.columns).index(col_name)
        row_num = self.smrt_df.data_df.index.get_loc(df_idx)
        model_idx = self.index(row_num, col_num, QtCore.QModelIndex())
        self.smrt_df.data_df.loc[df_idx, col_name] = new_val
        self.dataChanged.emit(model_idx, model_idx)

    def drop_df_row(self, df_idx: typing.Any):
        row_num = self.smrt_df.data_df.index.get_loc(df_idx)
        print(f"Dropping row {row_num}, {df_idx}")
        self.beginRemoveRows(QtCore.QModelIndex(), row_num, row_num)
        self.smrt_df.data_df.drop(df_idx, inplace=True)
        self.endRemoveRows()

    def set_smrt_df(self, new_smrt_df: smrt_dataframe.SmartDataFrame):

        # self.beginResetModel()
        self.smrt_df = new_smrt_df
        # self.endResetModel()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self.smrt_df.data_df.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if self.smrt_df.data_df is None:
            return 0
        return self.smrt_df.data_df.shape[1]

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None
        if index.column() < 0 or index.column() >= self.columnCount():
            return None

        row = index.row()
        col = index.column()
        col_name = self.smrt_df.data_df.columns[col]
        dtype = self.smrt_df.dtypes[col_name]
        value = self.smrt_df.data_df.iloc[row, col]
        val_flags = (
            smrt_consts.SmartValueFlags.NO_FLAG
            if col_name not in self.col_value_attrs
            else self.col_value_attrs[col_name].flags
        )

        if role == QtCore.Qt.ItemDataRole.DisplayRole:

            if dtype == smrt_consts.SmartDataTypes.TEXT:
                if pd.isnull(value):
                    return ""
                return str(value)
            elif dtype == smrt_consts.SmartDataTypes.FLOAT:
                if pd.isnull(value):
                    return ""
                return f"{value:.2f}"
            elif dtype == smrt_consts.SmartDataTypes.ACCT:
                if pd.isnull(value):
                    return ""
                return f"$ {value:,.2f}"
            elif dtype == smrt_consts.SmartDataTypes.INT:
                if pd.isnull(value):
                    return ""
                if value == smrt_consts.SMRT_TBL_BLANK_INT_FLAG:
                    return ""
                return f"{value:,}"
            elif dtype == smrt_consts.SmartDataTypes.DATE:

                if pd.isnull(value):
                    if val_flags & smrt_consts.SmartValueFlags.REQUIRED:
                        return "UNKNOWN"
                    else:
                        return ""
                try:
                    display_val = value.strftime("%Y-%m-%d")
                except ValueError:
                    self.logger.warning(
                        f"An error occurred when interpreting '{value}' as a date."
                    )
                    return "UNKNOWN"

                if val_flags & smrt_consts.SmartValueFlags.MIN_VALID_VALUE:
                    if value < self.col_value_attrs[col_name].min_value:
                        return "INVALID"
                if val_flags & smrt_consts.SmartValueFlags.MAX_VALID_VALUE:
                    if value > self.col_value_attrs[col_name].max_value:
                        return "INVALID"
                if val_flags & smrt_consts.SmartValueFlags.MAX_EXPECTED_VALUE:
                    if value > self.col_value_attrs[col_name].max_value:
                        return ""
                return display_val

            elif dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                if pd.isnull(value):
                    return ""
                if (
                    value == smrt_consts.UNKNOWN_DATETIME
                    or value == smrt_consts.SORT_ASC_UNKNOWN_DATETIME
                ):
                    return "UNKNOWN"
                elif value == smrt_consts.INVALID_DATETIME:
                    return "INVALID"
                else:
                    try:
                        temp = value.strftime("%Y-%m-%d %H:%M:%S")
                        return temp
                    except ValueError:
                        self.logger.warning(
                            f"An error occurred when interpreting '{value}' as a datetime."
                        )
                        return "UNKNOWN"
            elif dtype == smrt_consts.SmartDataTypes.BOOL:
                if pd.isnull(value):
                    return ""
                if value:
                    return "TRUE"
                else:
                    return "FALSE"
            else:
                self.logger.info(
                    "An unknown dtype was coverted to a string (by default)"
                )
                if pd.isnull(value):
                    return ""
                return str(value)

        elif role == smrt_consts.TABLE_SORT_ROLE:

            if pd.isnull(value):
                return ""
            if dtype == smrt_consts.SmartDataTypes.TEXT:
                return str(value)
            elif dtype == smrt_consts.SmartDataTypes.FLOAT:
                return value
            elif dtype == smrt_consts.SmartDataTypes.ACCT:
                return value
            elif dtype == smrt_consts.SmartDataTypes.INT:
                return value
            elif dtype == smrt_consts.SmartDataTypes.DATE:
                return value
            elif dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                return value
            elif dtype == smrt_consts.SmartDataTypes.BOOL:
                if value:
                    return 1
                else:
                    return 0
            else:
                self.logger.info(
                    "An unknown dtype was coverted to a string (by default)"
                )
                return str(value)

        elif role == smrt_consts.TABLE_FILTER_ROLE:
            if pd.isnull(value):
                return ""
            if dtype == smrt_consts.SmartDataTypes.TEXT:
                return str(value)
            elif dtype == smrt_consts.SmartDataTypes.FLOAT:
                return value
            elif dtype == smrt_consts.SmartDataTypes.ACCT:
                return value
            elif dtype == smrt_consts.SmartDataTypes.INT:
                return value
            elif dtype == smrt_consts.SmartDataTypes.DATE:
                return value
            elif dtype == smrt_consts.SmartDataTypes.DATE_TIME:
                return value
            elif dtype == smrt_consts.SmartDataTypes.BOOL:
                if value:
                    return 1
                else:
                    return 0
            else:
                self.logger.info(
                    "An unknown dtype was coverted to a string (by default)"
                )
                return str(value)

        elif role == QtCore.Qt.ItemDataRole.EditRole:
            value = self.smrt_df.data_df.iloc[row, col]
            return value

        elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            return QtCore.Qt.AlignmentFlag.AlignCenter

        elif role == smrt_consts.SPN_MIN_VALUE_ROLE:
            if (
                dtype == smrt_consts.SmartDataTypes.INT
                or dtype == smrt_consts.SmartDataTypes.FLOAT
                or dtype == smrt_consts.SmartDataTypes.ACCT
            ):
                return 0
            return None

        elif role == smrt_consts.SPN_MAX_VALUE_ROLE:
            if (
                dtype == smrt_consts.SmartDataTypes.INT
                or dtype == smrt_consts.SmartDataTypes.FLOAT
                or dtype == smrt_consts.SmartDataTypes.ACCT
            ):
                return value
            return None

        elif role == QtCore.Qt.ItemDataRole.BackgroundRole:
            if col_name in self.editable_cols:
                return smrt_consts.EDITABLE_COLUMN_BG_COLOR

        return None

    def setData(self, index, value, role=...) -> bool:
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()
        if role == QtCore.Qt.ItemDataRole.EditRole:
            self.smrt_df.data_df.iloc[row, col] = value
            self.dataChanged.emit(index, index, [])
            return True
        return False

    def headerData(self, section: int, orientation, role: int = ...) -> typing.Any:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        if 0 <= section < self.smrt_df.data_df.shape[1]:
            return str(self.smrt_df.data_df.columns[section])
        return None

    def flags(self, index: QModelIndex) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        col = index.column()
        flags = QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
        col_name = self.smrt_df.data_df.columns[col]
        if col_name in self.editable_cols:
            flags |= QtCore.Qt.ItemFlag.ItemIsEditable

        return flags

    def column_num_from_name(self, col_name: str) -> int:
        if not col_name:
            return -1

        if self.smrt_df.data_df is None:
            return -1

        if col_name not in self.smrt_df.data_df.columns:
            return -1

        return list(self.smrt_df.data_df.columns).index(col_name)
