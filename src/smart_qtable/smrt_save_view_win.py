from PyQt6 import QtCore, QtWidgets, QtGui


from frameless_dialog import frmls_dialog, frmls_msgbx


class SmartSaveViewDialog(frmls_dialog.FramelessDialog):

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent=parent)
        self.setup_dialog_ui()

        self.other_view_names: list[str] = []

        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)

    def setup_dialog_ui(self):
        self.cw = QtWidgets.QWidget(self)
        self.set_central_widget(self.cw)
        self.set_titlebar_mode(frmls_dialog.TitleMode.CLEAN_TITLE)
        self.main_layout = QtWidgets.QVBoxLayout(self.cw)
        self.setWindowTitle('Save current view')

        self.lbl_name_your_view = QtWidgets.QLabel('Provide a name for this view:', parent=self.cw)
        self.main_layout.addWidget(self.lbl_name_your_view)

        self.line_edit_view_name = QtWidgets.QLineEdit(parent=self.cw)
        self.line_edit_view_name.setPlaceholderText('Limit 15 chrs')
        self.line_edit_view_name.setClearButtonEnabled(True)
        self.line_edit_view_name.setMaxLength(15)
        self.main_layout.addWidget(self.line_edit_view_name)

        self.btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            parent=self.cw)
        self.main_layout.addWidget(self.btn_box)

    def show_me(self, other_view_names: list[str]):
        self.other_view_names = other_view_names
        self.line_edit_view_name.clear()

        return self.exec()

    def accept(self):

        msgbx = frmls_msgbx.FramelessMsgBx(parent=self)
        msgbx.setWindowTitle('Invalid name')
        msgbx.setIcon(frmls_msgbx.FramelessMsgBx.Icon.Warning)
        possible_view_name = self.line_edit_view_name.text().strip().lower()
        if possible_view_name == "":
            msgbx.setText('You cannot have a blank view name.')
            msgbx.exec()
            self.line_edit_view_name.clear()
            return
        for existing_name in self.other_view_names:
            if possible_view_name == existing_name.lower():
                msgbx.setText('You cannot use a name of an existing view.')
                msgbx.exec()
                self.line_edit_view_name.clear()
                return
        super().accept()

