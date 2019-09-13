# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 11:25:29 2016

@author: pfduc
"""
# Curently working inside
# def update_current_window(self, x):
#        ''' this changes what self.<object> refers to so that the same shared toolbars can modify whichever plot window has focus right now '''
#

current_window = self.zoneCentrale.activeSubWindow()

if not current_window == None:
    current_widget = self.zoneCentrale.activeSubWindow().widget()
    widget_type = str(current_widget.windowTitle()[0:4])
    print(widget_type)
    print(widget_type == "Live")
    # check if the activated window is a plot display
    # chose not to check by type because that could get messed up
    # if import/module names or class names get changed

    if widget_type == "Past":
        is_plot = True
        is_past = True
    elif widget_type == "Live":
        is_plot = True
        is_past = False
    else:
        msg = "The type of PlotDisplayWindow '%s' is unknown" % (widget_type)
        raise ValueError(msg)

    self.emit(SIGNAL("plotwindowtype_changed(PyQt_PyObject)"), widget_type)

    if is_plot:
        # The plot menu and file menu actions need local references to
        # these attributes of the currently selected plot window
        self.current_pdw = current_widget
        self.fig = current_widget.fig
        self.ax = current_widget.ax
        self.axR = current_widget.axR
        self.mplwidget = current_widget.mplwidget
        self.radioButton_X = current_widget.channel_objects[
            "groupBox_X"]
        self.checkBox_Y = current_widget.channel_objects["groupBox_Y"]
        # TODO: update actions isChecked() statuses to reflect
        # currently selected window
else:
    # 20130722 it runs this part of the code everytime I click
    # somehwere else that inside the main window
    pass
