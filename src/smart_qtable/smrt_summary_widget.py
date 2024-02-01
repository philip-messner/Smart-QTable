from PyQt6 import QtCore, QtWidgets, QtGui

import dataclasses

from smart_qtable import smrt_consts


@dataclasses.dataclass
class Attribute:

    name: str
    dtype: smrt_consts.SmartDataTypes


class AttrSummaryWidget(QtWidgets.QWidget):
    widget_count = 0

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_attr_summary_ui()
        AttrSummaryWidget.widget_count += 1
        self.widget_id = AttrSummaryWidget.widget_count

        self.attr_name = kwargs.get('attr_name', f'attribute{self.widget_id:02}')
        self.dtype: smrt_consts.SmartDataTypes = kwargs.get('dtype', smrt_consts.SmartDataTypes.INT)
        self.total_val = kwargs.get('total_val', 0)
        self.filtered_val = kwargs.get('filtered_val', 0)
        self.selected_val = kwargs.get('selected_val', 0)

    @property
    def attr_name(self) -> str:
        return self.__attr_name

    @attr_name.setter
    def attr_name(self, name: str) -> None:
        self.__attr_name = name.title()
        self.lbl_attr_hdr.setText(self.__attr_name)

    @property
    def dtype(self) -> smrt_consts.SmartDataTypes:
        return self.__dtype

    @dtype.setter
    def dtype(self, attr_dtype: smrt_consts.SmartDataTypes) -> None:
        self.__dtype = attr_dtype

    @property
    def total_val(self) -> int | float:
        return self.__total_val

    @total_val.setter
    def total_val(self, new_val: int | float):
        self.__total_val = new_val
        if self.dtype == smrt_consts.SmartDataTypes.INT:
            self.lbl_attr_data_total_result.setText(f'{self.__total_val:,}')
        elif self.dtype == smrt_consts.SmartDataTypes.FLOAT:
            self.lbl_attr_data_total_result.setText(f'{self.__total_val:,.2f}')
        elif self.dtype == smrt_consts.SmartDataTypes.ACCT:
            self.lbl_attr_data_total_result.setText(f'$ {self.__total_val:,.2f}')
        else:
            self.lbl_attr_data_total_result.setText(f'{self.__total_val}')

    @property
    def filtered_val(self) -> int | float:
        return self.__filtered_val

    @filtered_val.setter
    def filtered_val(self, new_val: int | float):
        self.__filtered_val = new_val
        if self.dtype == smrt_consts.SmartDataTypes.INT:
            self.lbl_attr_data_filtered_result.setText(f'{self.__filtered_val:,}')
        elif self.dtype == smrt_consts.SmartDataTypes.FLOAT:
            self.lbl_attr_data_filtered_result.setText(f'{self.__filtered_val:,.2f}')
        elif self.dtype == smrt_consts.SmartDataTypes.ACCT:
            self.lbl_attr_data_filtered_result.setText(f'$ {self.__filtered_val:,.2f}')
        else:
            self.lbl_attr_data_filtered_result.setText(f'{self.__filtered_val}')

        self.on_filtered_val_update()

    @property
    def selected_val(self) -> int | float:
        return self.__selected_val

    @selected_val.setter
    def selected_val(self, new_val: int | float):
        self.__selected_val = new_val
        if self.dtype == smrt_consts.SmartDataTypes.INT:
            self.lbl_attr_data_selected_result.setText(f'{self.__selected_val:,}')
        elif self.dtype == smrt_consts.SmartDataTypes.FLOAT:
            self.lbl_attr_data_selected_result.setText(f'{self.__selected_val:,.2f}')
        elif self.dtype == smrt_consts.SmartDataTypes.ACCT:
            self.lbl_attr_data_selected_result.setText(f'$ {self.__selected_val:,.2f}')
        else:
            self.lbl_attr_data_selected_result.setText(f'{self.__selected_val}')

        self.on_selected_value_update()

    def on_filtered_val_update(self):
        if self.filtered_val == 0:
            self.frm_attr_data_filtered.setVisible(False)
        else:
            self.frm_attr_data_filtered.setVisible(True)

    def on_selected_value_update(self):
        if self.selected_val == 0:
            self.frm_attr_data_selected.setVisible(False)
        else:
            self.frm_attr_data_selected.setVisible(True)

    def setup_attr_summary_ui(self):
        self.setObjectName("widget_attr_summary")
        # self.resize(254, 59)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QtCore.QSize(16777215, 60))
        self.layout_widget = QtWidgets.QVBoxLayout(self)
        self.layout_widget.setContentsMargins(1, 1, 1, 1)
        self.layout_widget.setSpacing(1)
        self.layout_widget.setObjectName("layout_widget")
        self.lbl_attr_hdr = QtWidgets.QLabel(parent=self)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setUnderline(True)
        # font.setWeight(75)
        self.lbl_attr_hdr.setFont(font)
        self.lbl_attr_hdr.setText("Attr Hdr")
        self.lbl_attr_hdr.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_hdr.setObjectName("lbl_attr_hdr")
        self.layout_widget.addWidget(self.lbl_attr_hdr)
        self.frm_attr_data = QtWidgets.QFrame(parent=self)
        self.frm_attr_data.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frm_attr_data.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_attr_data.setObjectName("frm_attr_data")
        self.layout_frm_attr_data = QtWidgets.QHBoxLayout(self.frm_attr_data)
        self.layout_frm_attr_data.setContentsMargins(0, 0, 0, 0)
        self.layout_frm_attr_data.setSpacing(6)
        self.layout_frm_attr_data.setObjectName("layout_frm_attr_data")
        self.frm_attr_data_total = QtWidgets.QFrame(parent=self.frm_attr_data)
        self.frm_attr_data_total.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frm_attr_data_total.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_attr_data_total.setObjectName("frm_attr_data_total")
        self.layout_frm_attr_data_total = QtWidgets.QVBoxLayout(self.frm_attr_data_total)
        self.layout_frm_attr_data_total.setContentsMargins(0, 0, 0, 0)
        self.layout_frm_attr_data_total.setSpacing(2)
        self.layout_frm_attr_data_total.setObjectName("layout_frm_attr_data_total")
        self.lbl_attr_data_total = QtWidgets.QLabel(parent=self.frm_attr_data_total)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        # font.setWeight(75)
        self.lbl_attr_data_total.setFont(font)
        self.lbl_attr_data_total.setText("Total:")
        self.lbl_attr_data_total.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_data_total.setObjectName("lbl_attr_data_total")
        self.layout_frm_attr_data_total.addWidget(self.lbl_attr_data_total)
        self.lbl_attr_data_total_result = QtWidgets.QLabel(parent=self.frm_attr_data_total)
        self.lbl_attr_data_total_result.setText("$ 999,999,999")
        self.lbl_attr_data_total_result.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_data_total_result.setObjectName("lbl_attr_data_total_result")
        self.layout_frm_attr_data_total.addWidget(self.lbl_attr_data_total_result)
        self.layout_frm_attr_data.addWidget(self.frm_attr_data_total)
        self.frm_attr_data_filtered = QtWidgets.QFrame(parent=self.frm_attr_data)
        self.frm_attr_data_filtered.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frm_attr_data_filtered.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_attr_data_filtered.setObjectName("frm_attr_data_filtered")
        self.layout_frm_attr_data_filtered = QtWidgets.QVBoxLayout(self.frm_attr_data_filtered)
        self.layout_frm_attr_data_filtered.setContentsMargins(0, 0, 0, 0)
        self.layout_frm_attr_data_filtered.setSpacing(2)
        self.layout_frm_attr_data_filtered.setObjectName("layout_frm_attr_data_filtered")
        self.lbl_attr_data_filtered = QtWidgets.QLabel(parent=self.frm_attr_data_filtered)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        # font.setWeight(75)
        self.lbl_attr_data_filtered.setFont(font)
        self.lbl_attr_data_filtered.setText("Filtered:")
        self.lbl_attr_data_filtered.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_data_filtered.setObjectName("lbl_attr_data_filtered")
        self.layout_frm_attr_data_filtered.addWidget(self.lbl_attr_data_filtered)
        self.lbl_attr_data_filtered_result = QtWidgets.QLabel(parent=self.frm_attr_data_filtered)
        self.lbl_attr_data_filtered_result.setText("$ 999,999,999")
        self.lbl_attr_data_filtered_result.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_data_filtered_result.setObjectName("lbl_attr_data_filtered_result")
        self.layout_frm_attr_data_filtered.addWidget(self.lbl_attr_data_filtered_result)
        self.layout_frm_attr_data.addWidget(self.frm_attr_data_filtered)
        self.frm_attr_data_selected = QtWidgets.QFrame(parent=self.frm_attr_data)
        self.frm_attr_data_selected.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frm_attr_data_selected.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_attr_data_selected.setObjectName("frm_attr_data_selected")
        self.layout_frm_attr_data_selected = QtWidgets.QVBoxLayout(self.frm_attr_data_selected)
        self.layout_frm_attr_data_selected.setContentsMargins(0, 0, 0, 0)
        self.layout_frm_attr_data_selected.setSpacing(2)
        self.layout_frm_attr_data_selected.setObjectName("layout_frm_attr_data_selected")
        self.lbl_attr_data_selected = QtWidgets.QLabel(parent=self.frm_attr_data_selected)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        # font.setWeight(75)
        self.lbl_attr_data_selected.setFont(font)
        self.lbl_attr_data_selected.setText("Selection:")
        self.lbl_attr_data_selected.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_data_selected.setObjectName("lbl_attr_data_selected")
        self.layout_frm_attr_data_selected.addWidget(self.lbl_attr_data_selected)
        self.lbl_attr_data_selected_result = QtWidgets.QLabel(parent=self.frm_attr_data_selected)
        self.lbl_attr_data_selected_result.setText("$ 999,999,999")
        self.lbl_attr_data_selected_result.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_attr_data_selected_result.setObjectName("lbl_attr_data_selected_result")
        self.layout_frm_attr_data_selected.addWidget(self.lbl_attr_data_selected_result)
        self.layout_frm_attr_data.addWidget(self.frm_attr_data_selected)
        self.layout_widget.addWidget(self.frm_attr_data)


        QtCore.QMetaObject.connectSlotsByName(self)

class SmartSummaryWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_summary_widget_ui()

        self.attr_widgets: list[AttrSummaryWidget] = []
        attr_list: list[Attribute] = kwargs.get('attr_list', None)
        if attr_list is None:
            attr_list = []
        if len(attr_list) > smrt_consts.MAX_SUMMARY_WIDGETS:
            raise ValueError(f'You cannot have more than {smrt_consts.MAX_SUMMARY_WIDGETS} summary widgets.')
        for attr in attr_list:
            new_attr_widget = AttrSummaryWidget(
                    attr_name=attr.name,
                    dtype=attr.dtype
                )
            self.attr_widgets.append(new_attr_widget)
            self.main_layout.addWidget(new_attr_widget)

    def add_attr(self, attr: Attribute) -> None:
        if len(self.attr_widgets) == smrt_consts.MAX_SUMMARY_WIDGETS:
            raise ValueError(f'You cannot have more than {smrt_consts.MAX_SUMMARY_WIDGETS} summary widgets.')
        new_attr_widget = AttrSummaryWidget(
            attr_name=attr.name,
            dtype=attr.dtype
        )
        self.attr_widgets.append(new_attr_widget)
        self.main_layout.addWidget(new_attr_widget)


    def update_attr_total(self, attr_name: str, new_val: int | float):
        found = False
        for attr_widget in self.attr_widgets:
            if attr_widget.attr_name.lower() == attr_name.lower():
                found = True
                break

        if not found:
            raise ValueError(f'The desired attribute widget could not be located for name: {attr_name}')

        attr_widget.total_val = new_val

    def update_attr_filtered(self, attr_name: str, new_val: int | float):
        found = False
        for attr_widget in self.attr_widgets:
            if attr_widget.attr_name.lower() == attr_name.lower():
                found = True
                break

        if not found:
            raise ValueError(f'The desired attribute widget could not be located for name: {attr_name}')

        attr_widget.filtered_val = new_val


    def update_attr_selected(self, attr_name: str, new_val: int | float):
        found = False
        for attr_widget in self.attr_widgets:
            if attr_widget.attr_name.lower() == attr_name.lower():
                found = True
                break

        if not found:
            raise ValueError(f'The desired attribute widget could not be located for name: {attr_name}')

        attr_widget.selected_val = new_val

    def setup_summary_widget_ui(self):
        self.setObjectName('smart_summary_widget')
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

