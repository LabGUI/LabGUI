# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 23:40:40 2014

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""

import sys
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore


class LimitsWidget(QtGui.QWidget):
    """This class handles the selections, axis and data limits"""

    def __init__(self, parent=None):
        super(LimitsWidget, self).__init__(parent)

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("vertical_layout")

        self.areaLayout = QtGui.QHBoxLayout()
        self.plotLayout = QtGui.QHBoxLayout()
        self.axisLayout = QtGui.QHBoxLayout()
        labels = ["Imin :", "", "Imax :", "", "Xmin :", "", "Xmax :", ""]
        self.add_label("AREA")
        self.add_line(self.areaLayout, labels)
        self.add_label("PLOT")
        self.add_line(self.plotLayout, labels)
        self.add_label("AXIS")
        self.add_line(self.axisLayout, labels)
        self.setLayout(self.verticalLayout)

        self.connect(parent, QtCore.SIGNAL("selections_limits(PyQt_PyObject,int,int,int)"), self.updated_selection)

    def add_label(self, label):

        layout = QtGui.QHBoxLayout()
        alabel = QtGui.QLabel(self)
        alabel.setText(label)
        layout.addWidget(alabel)

        self.verticalLayout.addLayout(layout)

    def add_line(self, layout, labels):

        alabel = QtGui.QLabel(self)
        XminIndex = QtGui.QLineEdit(self)
        XmaxIndex = QtGui.QLineEdit(self)
        Xmin = QtGui.QLineEdit(self)
        Xmax = QtGui.QLineEdit(self)
        alabel = QtGui.QLabel(self)
        layout.addWidget(alabel)
        layout.addWidget(XminIndex)
        alabel = QtGui.QLabel(self)
        layout.addWidget(alabel)
        layout.addWidget(XmaxIndex)
        alabel = QtGui.QLabel(self)
        layout.addWidget(alabel)
        layout.addWidget(Xmin)
        alabel = QtGui.QLabel(self)
        layout.addWidget(alabel)
        layout.addWidget(Xmax)
        fill_layout_textbox(layout, labels)

        choiceRB = QtGui.QRadioButton(self)
        choiceRB.setText("Activate")
        layout.addWidget(choiceRB)

        self.verticalLayout.addLayout(layout)

    def updated_selection(self, limits, paramX, paramY, mode):
        #        print "LW.updated_selection :"
        if mode == 2:
            self.update_line("AREA", limits)
        else:
            self.update_line("AXIS", limits)

    def update_line(self, line_name, values):
        #        print "LW.update_line : ",line_name
        labels = ["Imin :", "%i" % (values[0]), "Imax :", "%i" % (
            values[1]), "Xmin :", "%.2f" % (values[2]), "Xmax :", "%.2f" % (values[3]), "Activate"]
        if line_name == "AREA":
            layout = self.areaLayout
        elif line_name == "PLOT":
            layout = self.plotLayout
        elif line_name == "AXIS":
            layout = self.axisLayout
        fill_layout_textbox(layout, labels)


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain
    
    create a QDock widget and store a reference to the widget
    """

    mywidget = LimitsWidget(parent = parent)
    
    #create a QDockWidget
    limitsDockWidget = QtGui.QDockWidget("Limits", parent)
    limitsDockWidget.setObjectName("limitsWidget")
    limitsDockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        
    #fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['LimitsWidget'] = mywidget
    
    limitsDockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, limitsDockWidget)
    
    #Enable the toggle view action
    parent.windowMenu.addAction(limitsDockWidget.toggleViewAction())
    limitsDockWidget.hide()





def fill_layout_textbox(layout, text):
    """
    This function loop over a layout objects set their texts
    """
    for label, i in zip(text, list(range(layout.count()))):
        item = layout.itemAt(i)
        widget = item.widget()
        widget.setText(str(label))

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = LimitsWidget()
    ex.show()

#    ex.remove_all_lines()
    sys.exit(app.exec_())
