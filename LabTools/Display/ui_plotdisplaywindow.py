# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotdisplaywindow.ui'
#
# Created: Wed May 21 13:19:33 2014
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtGui import QPalette, QBrush, QColor


else:

    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QPalette, QBrush, QColor


from QtTools import clear_layout

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s): return s


class Ui_PlotDisplayWindow(QtCore.QObject):

    def setupUi(self, PlotDisplayWindow, channel_controls={"groupBox_X": ["X", "radioButton"], "groupBox_Y": ["Y", "checkBox"], "groupBox_YR": ["Y", "checkBox"], "groupBox_invert": ["+/-", "checkBox"]}):

        PlotDisplayWindow.setObjectName("PlotDisplayWindow")
        PlotDisplayWindow.resize(959, 611)
        PlotDisplayWindow.setWindowTitle(QtGui.QApplication.translate(
            "PlotDisplayWindow", "MainWindow", None))
        self.centralwidget = QtGui.QWidget(PlotDisplayWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.plot_holder = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.plot_holder.sizePolicy().hasHeightForWidth())
        self.plot_holder.setSizePolicy(sizePolicy)
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active,
                         QPalette.WindowText, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush)
        brush = QBrush(QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush)
        brush = QBrush(QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active,
                         QPalette.BrightText, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active,
                         QPalette.ButtonText, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active,
                         QPalette.AlternateBase, brush)
        brush = QBrush(QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active,
                         QPalette.ToolTipBase, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Active,
                         QPalette.ToolTipText, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.WindowText, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.Midlight, brush)
        brush = QBrush(QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush)
        brush = QBrush(QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.BrightText, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.ButtonText, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.AlternateBase, brush)
        brush = QBrush(QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.ToolTipBase, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive,
                         QPalette.ToolTipText, brush)
        brush = QBrush(QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.WindowText, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.Midlight, brush)
        brush = QBrush(QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush)
        brush = QBrush(QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush)
        brush = QBrush(QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.BrightText, brush)
        brush = QBrush(QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.ButtonText, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.AlternateBase, brush)
        brush = QBrush(QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.ToolTipBase, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled,
                         QPalette.ToolTipText, brush)
        self.plot_holder.setPalette(palette)
        self.plot_holder.setAutoFillBackground(True)
        self.plot_holder.setObjectName("plot_holder")
        self.horizontalLayout_2.addWidget(self.plot_holder)
        PlotDisplayWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(PlotDisplayWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 959, 21))
        self.menubar.setObjectName("menubar")
        PlotDisplayWindow.setMenuBar(self.menubar)
        self.dockWidget = QtGui.QDockWidget(PlotDisplayWindow)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.groupBoxes = {}
#        print channel_controls.items()
#        print channel_controls

        for name, lbl in list(channel_controls.items()):
            self.groupBoxes[name] = QtGui.QGroupBox(self.dockWidgetContents)
            sizePolicy = QtGui.QSizePolicy(
                QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.groupBoxes[name].sizePolicy().hasHeightForWidth())
            self.groupBoxes[name].setSizePolicy(sizePolicy)
            if lbl[1] == "lineEdit":
                self.groupBoxes[name].setMinimumSize(QtCore.QSize(100, 0))
            if lbl[1] == "comboBox":
                self.groupBoxes[name].setMinimumSize(QtCore.QSize(50, 0))
            self.groupBoxes[name].setTitle(QtGui.QApplication.translate(
                "PlotDisplayWindow", lbl[0], None))
            self.groupBoxes[name].setObjectName(name)
            self.horizontalLayout.addWidget(self.groupBoxes[name])

        self.dockWidget.setWidget(self.dockWidgetContents)
        PlotDisplayWindow.addDockWidget(
            QtCore.Qt.DockWidgetArea(2), self.dockWidget)
        self.actionSave_figure = QtGui.QAction(PlotDisplayWindow)
        self.actionSave_figure.setText(QtGui.QApplication.translate(
            "PlotDisplayWindow", "Save figure", None))
        self.actionSave_figure.setObjectName("actionSave_figure")
        self.actionQuit = QtGui.QAction(PlotDisplayWindow)
        self.actionQuit.setText(QtGui.QApplication.translate(
            "PlotDisplayWindow", "Quit", None))
        self.actionQuit.setObjectName("actionQuit")

        self.retranslateUi(PlotDisplayWindow)
        QtCore.QMetaObject.connectSlotsByName(PlotDisplayWindow)

    def __delete_layouts__(self):
        """iterate through the layout and destroys the widgets properly"""
        clear_layout(self.horizontalLayout)
        clear_layout(self.horizontalLayout_2)

    def retranslateUi(self, PlotDisplayWindow):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PlotDisplayWindow = QtGui.QMainWindow()
    ui = Ui_PlotDisplayWindow()
    ui.setupUi(PlotDisplayWindow)
    PlotDisplayWindow.show()
    sys.exit(app.exec_())
