# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 16:01:24 2013

Copyright (C) 10th april 2015 Benjamin Schmidt
License: see LICENSE.txt file
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui

##global variables used to know what mode the mouse is in
# these have moved to mplZoomWidget
#ZOOM_MODE = 0
#PAN_MODE = 1
#SELECT_MODE =2


# A silly little class to replace stdout that both prints and emits the text as a signal
class printerceptor():

    def __init__(self, parent=None):
        self.old_stdout = sys.stdout
        self.parent = parent

    def write(self, stri):
        self.old_stdout.write(stri)
        self.parent.emit(SIGNAL("print_to_console(PyQt_PyObject)"), stri)

    def flush(self):
        self.old_stoud.flush()
        
def create_action(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(QIcon("./images/%s.png" % icon))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        parent.connect(action, SIGNAL(signal), slot)
    if checkable:
        action.setCheckable(True)
    return action


def clear_layout(layout):
    """
    This function loop over a layout objects and delete them properly
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        layout.removeWidget(widget)
        try:
            widget.setParent(None)
        except:
            pass
        if not widget == None:
            widget.close()


# Code from Giovanni Bajo via
# http://www.riverbankcomputing.com/pipermail/pyqt/2008-July/020042.html
class QAutoHideDockWidgets(QToolBar):
    """
    QMainWindow "mixin" which provides auto-hiding support for dock widgets
    (not toolbars).
    """
    DOCK_AREA_TO_TB = {
        Qt.LeftDockWidgetArea: Qt.LeftToolBarArea,
        Qt.RightDockWidgetArea: Qt.RightToolBarArea,
        Qt.TopDockWidgetArea: Qt.TopToolBarArea,
        Qt.BottomDockWidgetArea: Qt.BottomToolBarArea,
    }

    def __init__(self, area, parent, name="AUTO_HIDE"):
        QToolBar.__init__(self, parent)
        assert isinstance(parent, QMainWindow)
        assert area in self.DOCK_AREA_TO_TB
        self._area = area
        self.setObjectName(name)
        self.setWindowTitle(name)

        self.setFloatable(False)
        self.setMovable(False)
        w = QWidget(None)
        w.resize(10, 100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.MinimumExpanding))
        self.addWidget(w)

        self.setAllowedAreas(self.DOCK_AREA_TO_TB[self._area])
        self.parent().addToolBar(self.DOCK_AREA_TO_TB[self._area], self)
        self.parent().centralWidget().installEventFilter(self)

        self.setVisible(False)
        self.hideDockWidgets()

    def _dockWidgets(self):
        mw = self.parent()
        for w in mw.findChildren(QDockWidget):
            if mw.dockWidgetArea(w) == self._area and not w.isFloating():
                yield w

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(Qt.black)
        p.setBrush(Qt.black)
        if self._area == Qt.LeftDockWidgetArea:
            p.translate(QPointF(0, self.height() / 2 - 5))
            p.drawPolygon(QPointF(2, 0), QPointF(8, 5), QPointF(2, 10))
        elif self._area == Qt.RightDockWidgetArea:
            p.translate(QPointF(0, self.height() / 2 - 5))
            p.drawPolygon(QPointF(8, 0), QPointF(2, 5), QPointF(8, 10))

    def _multiSetVisible(self, widgets, state):
        if state:
            self.setVisible(False)

        for w in widgets:
            w.setUpdatesEnabled(False)
        for w in widgets:
            w.setVisible(state)
        for w in widgets:
            w.setUpdatesEnabled(True)

        if not state and widgets:
            self.setVisible(True)

    def enterEvent(self, event):
        self.showDockWidgets()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            assert obj == self.parent().centralWidget()
            self.hideDockWidgets()
        return False

    def setDockWidgetsVisible(self, state):
        self._multiSetVisible(list(self._dockWidgets()), state)

    def showDockWidgets(self): self.setDockWidgetsVisible(True)

    def hideDockWidgets(self): self.setDockWidgetsVisible(False)


class DialogBox(QtGui.QWidget):

    def __init__(self, label="", windowname="", parent=None):
        super(DialogBox, self).__init__(parent)

        self.grid = QtGui.QGridLayout()
        self.lbl = QtGui.QLabel(label, self)
        self.grid.addWidget(self.lbl, 0, 0)
        self.txt = QtGui.QLineEdit(self)
        self.grid.addWidget(self.txt, 1, 0)
        self.bt_ok = QtGui.QPushButton("Ok", self)
        self.grid.addWidget(self.bt_ok, 2, 0)
#        self.setLayout(self.grid)

        self.verticalLayout = QtGui.QVBoxLayout(self)

        self.verticalLayout.setObjectName("verticalLayout")

        self.verticalLayout.addLayout(self.grid)

        self.setLayout(self.verticalLayout)
        self.setWindowTitle(windowname)
        self.resize(200, 120)

        self.connect(self.bt_ok, SIGNAL("clicked()"), self.button_click)

    def button_click(self):
        self.emit(SIGNAL("dialogboxanswer(QString)"), self.txt.text())
        self.txt.setText("")
        self.hide()

def dockWidgetCloseEvent(event):
    event.ignore()