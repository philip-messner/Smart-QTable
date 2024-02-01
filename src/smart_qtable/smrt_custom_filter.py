from PyQt6 import QtCore, QtGui, QtWidgets

import typing

from frameless_dialog import frmls_dialog
from smart_resources import smrt_resources


class CustomFilterDialog(frmls_dialog.FramelessDialog):

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_custom_filter_ui()

    def show_me(self, all_columns: list[str], current_filters: dict[str, list[typing.Any]]) -> QtWidgets.QDialog.DialogCode:

        return self.exec()

    def setup_custom_filter_ui(self):
        self.setObjectName("adv_filter_dialog")
        self.set_titlebar_mode(frmls_dialog.TitleMode.ONLY_CLOSE_BTN)
        self.resize(420, 260)
        self.cent_widget = QtWidgets.QWidget(self)
        self.set_central_widget(self.cent_widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lbl_title.setFont(font)
        self.lbl_title.setMinimumWidth(250)
        self.lbl_title.setText("Customize Filter Options")
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
        # self.btn_options = QtWidgets.QToolButton(self.frm_header_btns)
        # self.btn_options.setMinimumSize(QtCore.QSize(80, 30))
        # self.btn_options.setMaximumSize(QtCore.QSize(80, 30))
        # self.btn_options.setToolTip("")
        # self.btn_options.setText("Options...")
        # self.btn_options.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        # self.btn_options.setObjectName("btn_options")
        # self.layout_frm_header_btns.addWidget(self.btn_options)
        spacerItem = QtWidgets.QSpacerItem(137, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
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
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.layout_adv_option_dialog.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self.cent_widget)




if __name__ == '__main__':
    import sys
    from softeon_front.custom_win import custom_win

    app = QtWidgets.QApplication(sys.argv)

    file = QtCore.QFile(":/dark/stylesheet.qss")
    file.open(QtCore.QFile.OpenModeFlag.ReadOnly | QtCore.QFile.OpenModeFlag.Text)
    stream = QtCore.QTextStream(file)
    app.setStyleSheet(stream.readAll())

    win = CustomFilterDialog(parent=None)
    win.show()

    sys.exit(app.exec())