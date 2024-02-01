from PyQt6 import QtCore, QtWidgets, QtGui

import enum
import logging

from frameless_dialog import frmls_dialog
from smart_resources import excel_export_resources, under_constr_resources

class UnavailDialog(frmls_dialog.FramelessDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setup_ui()
        self.pushButton.clicked.connect(self.on_pushbutton_click)
        self.set_titlebar_mode(frmls_dialog.TitleMode.NO_TITLE)

    def setup_ui(self):
        self.setObjectName("unavail_dialog")
        self.resize(286, 227)
        self.lbl_title.setText("Feature not yet available")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 10, 251, 111))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/under_construction.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(20, 120, 251, 61))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("This feature is not available in this release. Check back later!")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(110, 190, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText('Okay')
        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_pushbutton_click(self):
        self.close()

class ExportOptionsDialog(frmls_dialog.FramelessDialog):

    class SelectionOption(enum.IntEnum):

        NO_SELECTION = 0
        EXPORT_CURRENT = 1
        EXPORT_FULL = 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setup_export_options()
        self.selection = ExportOptionsDialog.SelectionOption.NO_SELECTION

        self.btn_export_current.clicked.connect(self.on_export_current)
        self.btn_export_full.clicked.connect(self.on_export_full)

    def setup_export_options(self):
        self.setObjectName("export_option")
        self.set_titlebar_mode(frmls_dialog.TitleMode.ONLY_CLOSE_BTN)
        self.status_bar.setVisible(False)
        self.resize(308, 160)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        # self.setSizePolicy(sizePolicy)
        self.lbl_title.setText("Select an option")
        self.export_options_central_widget = QtWidgets.QWidget(self)
        self.set_central_widget(self.export_options_central_widget)
        self.lbl_header = QtWidgets.QLabel(self.export_options_central_widget)
        self.lbl_header.setGeometry(QtCore.QRect(10, 20, 281, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl_header.setFont(font)
        self.lbl_header.setToolTip("")
        self.lbl_header.setText("Select what you would like to export:")
        self.lbl_header.setObjectName("lbl_header")
        self.btn_export_current = QtWidgets.QToolButton(self.export_options_central_widget)
        self.btn_export_current.setGeometry(QtCore.QRect(30, 50, 23, 20))
        self.btn_export_current.setText("")
        self.btn_export_current.setIcon(QtGui.QIcon(':/excel_view_data.png'))
        self.btn_export_current.setObjectName("btn_export_current")
        self.btn_export_full = QtWidgets.QToolButton(self.export_options_central_widget)
        self.btn_export_full.setGeometry(QtCore.QRect(30, 80, 23, 20))
        self.btn_export_full.setText("")
        self.btn_export_full.setIcon(QtGui.QIcon(':/excel_full_report.png'))
        self.btn_export_full.setObjectName("btn_export_full")
        self.lbl_option_1 = QtWidgets.QLabel(self.export_options_central_widget)
        self.lbl_option_1.setGeometry(QtCore.QRect(60, 50, 231, 16))
        self.lbl_option_1.setToolTip("")
        self.lbl_option_1.setText("The current data set (with filters and sorting)")
        self.lbl_option_1.setObjectName("lbl_option_1")
        self.lbl_option_2 = QtWidgets.QLabel(self.export_options_central_widget)
        self.lbl_option_2.setGeometry(QtCore.QRect(60, 80, 231, 16))
        self.lbl_option_2.setToolTip("")
        self.lbl_option_2.setText("The complete data set (unfiltered)")
        self.lbl_option_2.setObjectName("lbl_option_2")

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_export_current(self):
        self.selection = ExportOptionsDialog.SelectionOption.EXPORT_CURRENT
        self.accept()

    @QtCore.pyqtSlot()
    def on_export_full(self):
        self.selection = ExportOptionsDialog.SelectionOption.EXPORT_FULL
        self.accept()


class AnimatedToolButton(QtWidgets.QToolButton):

    logger = logging.getLogger('common.anim_tb')

    def __init__(self, animated, static, parent=None):
        super().__init__(parent=parent)
        self.animated_icon = animated
        self.static_icon = static
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(animated)
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @property
    def animated_icon(self):
        return self.__animated_icon

    @animated_icon.setter
    def animated_icon(self, animated):
        self.__animated_icon = animated

    @property
    def static_icon(self):
        return self.__static_icon

    @static_icon.setter
    def static_icon(self, static):
        self.__static_icon = static

    @QtCore.pyqtSlot()
    def start(self):
        if hasattr(self, "_movie"):
            self._movie.start()

    @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            if self.__static_icon is not None:
                self.setIcon(QtGui.QIcon(self.__static_icon))

    def setGif(self, gif_filename, png_filename):
        self.animated_icon = gif_filename
        self.static_icon = png_filename

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frameNumber):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))
