# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 11:25:22 2013

Copyright (C) 10th april 2015 Benjamin Schmidt
License: see LICENSE.txt file
"""

import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtCore import SIGNAL
from matplotlibwidget import MatplotlibWidget
import numpy as np
import matplotlib as mpl
import logging

from QtTools import ZOOM_MODE, PAN_MODE, SELECT_MODE


class MatplotlibZoomWidget(MatplotlibWidget):

    def __init__(self, parent=None, title='', xlabel='', ylabel='',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=4, height=3, dpi=100, hold=True, usingR=True):
        super(MatplotlibZoomWidget, self).__init__(parent, title, xlabel, ylabel,
                                                   xlim, ylim, xscale, yscale, width, height, dpi, hold)

        self.usingR = usingR

        if usingR:
            self.axesR = self.axes.twinx()
        else:
            # hacky way to avoid some errors
            self.axesR = self.axes

        self.axes.tick_params(axis='x', labelsize=8)
        self.axes.tick_params(axis='y', labelsize=8)

        if usingR:
            self.axesR.tick_params(axis='x', labelsize=8)
            self.axesR.tick_params(axis='y', labelsize=8)

        self.rect_zoom_on = True

        self.control_X_on = True
        self.control_Y_on = True
        self.control_R_on = usingR

        self.ZOOM_MODE = ZOOM_MODE
        self.PAN_MODE = PAN_MODE
        self.SELECT_MODE = SELECT_MODE
        self.select_rectangle = mpl.patches.Rectangle([0, 0], 1, 1)
        self.select_rectangle.set_fill(False)
        self.select_rectangle.set_edgecolor('k')
        self.select_rectangle.set_linestyle('dashed')
        self.selection_showing = False

        self.mouseMode = self.PAN_MODE

        self.autoscale_X_on = True
        self.autoscale_L_on = True
        self.autoscale_R_on = True

        # Shrink current axis by 20%
        #box = self.axes.get_position()
        #axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        #self.legend = self.axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def set_mouse_mode(self, mode):
        """ Set the mouse mode to zoom, pan or select
        
        Args:
            mode: can be ZOOM_MODE, PAN_MODE or SELECT_MODE
        """
        
        self.mouseMode = mode
        if mode == self.ZOOM_MODE:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        elif mode == self.PAN_MODE:
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        elif mode == self.SELECT_MODE:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def setActiveAxes(self, control_X_on=True, control_Y_on=True, control_R_on=False):
        self.control_X_on = control_X_on
        self.control_Y_on = control_Y_on
        self.control_R_on = control_R_on

    def autoscale_axes(self, axes=None, scale_x=True, scale_y=True, span_x=0,
                       margin_x=0, margin_y=0.05):
        """ Autoscale the axes such that the x data spans from the left edge
        to the right edge of the plot, but the y data leaves a margin at the 
        top and bottom. 
        """
        # default to adjusting the left axes
        if axes == None:
            axes = self.axes
            
        x_max = -np.inf
        x_min = np.inf

        y_max = -np.inf
        y_min = np.inf

        has_data = False

        for line in axes.get_lines():
            xdata = line.get_xdata()

            if len(xdata) > 0:

                x_max = max(x_max, np.nanmax(xdata))
                x_min = min(x_min, np.nanmin(xdata))
                has_data = True

            ydata = line.get_ydata()

            if len(ydata) > 0:
                y_max = max(y_max, np.nanmax(ydata))
                y_min = min(y_min, np.nanmin(ydata))
                has_data = True

        if scale_x and has_data:
            if x_max == x_min:
                # if there's only a single point, centre that point in the middle
                # of a window of width 1
                x_min = x_max - 0.5
                x_max = x_min + 1
                
            if span_x == 0:
                axes.set_xlim(x_min, x_max)
            else:
                axes.set_xlim(x_max - span_x, x_max)

        if scale_y and has_data:
            if y_max == y_min:
                # if there's only a single point, centre that point in the middle
                # of a window with 0 at the bottom
                y_min = 0
                y_max = y_max * 2
                margin = 0
            else:
                margin = (y_max - y_min) * margin_y

            axes.set_ylim(y_min - margin, y_max + margin)

    def set_autoscale_x(self, setting):
        self.autoscale_X_on = setting
        if setting:
            self.rescale_and_draw()

    def set_autoscale_y(self, setting):
        """ this appears to be here for back-compatibility """
        self.set_autoscale_yL(setting)

    def set_autoscale_yL(self, setting):
        self.autoscale_L_on = setting
        if setting:
            self.rescale_and_draw()

    def set_autoscale_yR(self, setting):
        self.autoscale_R_on = setting
        if setting:
            self.rescale_and_draw()

    def rescale_and_draw(self):

        self.autoscale_axes(axes=self.axes, scale_x=self.autoscale_X_on,
                            scale_y=self.autoscale_L_on)

        if self.usingR:
            self.autoscale_axes(axes=self.axesR, scale_x=False,
                                scale_y=self.autoscale_R_on)

        selection_limits = [self.axes.get_xlim(), self.axes.get_ylim()]
        self.emit(QtCore.SIGNAL("limits_changed(int,PyQt_PyObject)"),
                  3, np.array(selection_limits))

        self.redraw()

    def redraw(self):
        self.figure.canvas.draw()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.mouseMode == self.PAN_MODE:
                if self.mouseMode == self.PAN_MODE:
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                self.__mousePressX = event.x()
                self.__mousePressY = event.y()

                self.__XLim_0 = get_axis_limits(self.axes.xaxis)
                self.__YLim_0_L = get_axis_limits(self.axes.yaxis)
                self.__YLim_0_R = get_axis_limits(self.axesR.yaxis)

                self.__xScale = calculate_scaling(self.__XLim_0, -self.width())
                self.__yScale_L = calculate_scaling(
                    self.__YLim_0_L, self.height())
                self.__yScale_R = calculate_scaling(
                    self.__YLim_0_R, self.height())
                self.emit(QtCore.SIGNAL("mousePressed(PyQt_PyObject)"), [
                          self.__mousePressX, self.__mousePressY])

            elif self.mouseMode == self.ZOOM_MODE or self.mouseMode == self.SELECT_MODE:
                inv = self.axes.transAxes.inverted()
                self.zoom_click_X, self.zoom_click_Y = inv.transform(
                    (event.x(), self.height() - event.y()))
                #self.grab_line_closest_to(event.x(), event.y())
                # draw a rectangle indicating the new zoom area
                self.zoom_rectangle = self.axes.add_patch(mpl.patches.Rectangle(
                    (self.zoom_click_X, self.zoom_click_Y), 0, 0, transform=self.axes.transAxes))
                self.zoom_rectangle.set_fill(False)
                self.zoom_rectangle.set_edgecolor('k')
                self.zoom_rectangle.set_linestyle('dashed')
#            self.emit(QtCore.SIGNAL("mousePressed(PyQt_PyObject)"), [self.__mousePressX, self.__mousePressY])
        super(MatplotlibZoomWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:

            if self.mouseMode == self.PAN_MODE:
                if self.control_X_on:
                    new_lim = convert_lim(
                        self.axes.xaxis, self.__XLim_0 + self.__xScale * (event.x() - self.__mousePressX))
                    self.axes.set_xlim(new_lim)
                if self.control_Y_on:
                    new_lim = convert_lim(
                        self.axes.yaxis, self.__YLim_0_L + self.__yScale_L * (event.y() - self.__mousePressY))
                    self.axes.set_ylim(new_lim)
                if self.control_R_on and self.usingR:
                    new_lim = convert_lim(
                        self.axesR.yaxis, self.__YLim_0_R + self.__yScale_R * (event.y() - self.__mousePressY))
                    self.axesR.set_ylim(new_lim)
                self.rescale_and_draw()

            elif self.mouseMode == self.ZOOM_MODE or self.mouseMode == self.SELECT_MODE:
                inv = self.axes.transAxes.inverted()
                X, Y = inv.transform((event.x(), self.height() - event.y()))

                self.zoom_rectangle.set_bounds(
                    X, Y, self.zoom_click_X - X, self.zoom_click_Y - Y)
                self.figure.canvas.draw()

        super(MatplotlibZoomWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # if self.__mousePressPos is not None:
        super(MatplotlibZoomWidget, self).mouseReleaseEvent(event)
        if True:  # event.buttons() == QtCore.Qt.LeftButton:

            if self.mouseMode == self.PAN_MODE:
                self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
                selection_limits = [self.axes.get_xlim(), self.axes.get_ylim()]

            if self.mouseMode == self.ZOOM_MODE or self.mouseMode == self.SELECT_MODE:
                inv = self.axes.transAxes.inverted()
                X, Y = inv.transform((event.x(), self.height() - event.y()))

                [x_min, x_max, y_min, y_max] = self.get_selection_limits(X, self.zoom_click_X,
                                                                         Y, self.zoom_click_Y)

                selection_limits = [[x_min, x_max], [y_min, y_max]]

                if self.mouseMode == self.ZOOM_MODE:
                    ax = self.axes
                    ax.set_xlim(x_min, x_max)
                    ax.set_ylim(y_min, y_max)

                    self.zoom_rectangle.remove()
                    self.figure.canvas.draw()

                elif self.mouseMode == self.SELECT_MODE:
                    self.zoom_rectangle.remove()
                    self.select_rectangle.set_bounds(
                        x_min, y_min, x_max - x_min, y_max - y_min)
                    if not self.selection_showing:
                        self.selection_showing = True
                        self.axes.add_patch(self.select_rectangle)

                    self.figure.canvas.draw()

                    self.emit(QtCore.SIGNAL("area_selected(PyQt_PyObject)"),
                              [x_min, x_max, y_min, y_max])
        self.emit(QtCore.SIGNAL("limits_changed(int,PyQt_PyObject)"),
                  self.mouseMode, np.array(selection_limits))



    def transform_axes_to_fig(self, val, lim):
        return (lim[0] + val * (lim[1] - lim[0]))

    def get_selection_limits(self, x1, x2, y1, y2):
        ax = self.axes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        if ax.xaxis.get_scale() == 'log':
            xlim = np.log10(xlim)
        if ax.yaxis.get_scale() == 'log':
            ylim = np.log10(ylim)

        # x_min etc. are in the figure coordinates (or the exponent coordinates
        # for log scale)

        x_min = self.transform_axes_to_fig(min(x1, x2), xlim)
        y_min = self.transform_axes_to_fig(min(y1, y2), ylim)

        x_max = self.transform_axes_to_fig(max(x1, x2), xlim)
        y_max = self.transform_axes_to_fig(max(y1, y2), ylim)

        if ax.xaxis.get_scale() == 'log':
            x_min = 10**x_min
            x_max = 10**x_max
        if ax.yaxis.get_scale() == 'log':
            y_min = 10**y_min
            y_max = 10**y_max
        return [x_min, x_max, y_min, y_max]

    def wheelEvent(self, event):
        # zoom 10% for each "click" of scroll wheel
        zoom = 1 - event.delta() / 1200.0

        # correct for difference in coordinate systems (note Y is top left in widget, bottom left in figure)
        # X, Y in axes coordinates (0 to 1, 0,0 in lower left corner)
        ax = self.axes
        inv = ax.transAxes.inverted()
        X_0, Y_0 = inv.transform((event.x(), self.height() - event.y()))

        mouse_on_plot = (X_0 > 0 and X_0 < 1) and (Y_0 > 0 and Y_0 < 1)

        if mouse_on_plot:
            do_scale_X = self.control_X_on or event.buttons() == QtCore.Qt.LeftButton
            do_scale_Y = self.control_Y_on
            do_scale_R = self.control_R_on
        else:
            do_scale_X = (X_0 > 0 and Y_0 < 0)
            do_scale_Y = (X_0 < 0 and Y_0 > 0)
            do_scale_R = (X_0 > 1 and Y_0 > 0)

        if do_scale_X:
            if ax.yaxis.get_scale() == 'log':
                xlim = np.log10(ax.get_xlim())
                X = (xlim[0] + X_0 * (xlim[1] - xlim[0]))
                ax.set_xlim(
                    10**(X - zoom * (X - xlim[0])), 10**(X - zoom * (X - xlim[1])))
            else:
                xlim = ax.get_xlim()
                X = (xlim[0] + X_0 * (xlim[1] - xlim[0]))
                ax.set_xlim(X - zoom * (X - xlim[0]), X - zoom * (X - xlim[1]))

        for ax, on in zip([self.axes, self.axesR], [do_scale_Y, do_scale_R]):
            if on:
                if ax.yaxis.get_scale() == 'log':
                    # scale the exponents of the scale linearly instead when
                    # it's a log scale
                    ylim = np.log10(ax.get_ylim())
                    Y = (ylim[0] + Y_0 * (ylim[1] - ylim[0]))
                    ax.set_ylim(
                        10**(Y - zoom * (Y - ylim[0])), 10**(Y - zoom * (Y - ylim[1])))
                else:
                    ylim = ax.get_ylim()
                    Y = (ylim[0] + Y_0 * (ylim[1] - ylim[0]))
                    ax.set_ylim(
                        Y - zoom * (Y - ylim[0]), Y - zoom * (Y - ylim[1]))

        self.rescale_and_draw()
        #this might be superfluous as rescale_and_draw() already sends this with code 3
        self.emit(QtCore.SIGNAL("limits_changed(int,PyQt_PyObject)"), -1,
                  np.array([self.axes.get_xlim(), self.axes.get_ylim()]))
        super(MatplotlibZoomWidget, self).wheelEvent(event)

    def keyPressEvent(self, event):
        print ("hmmm")
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            x_min, x_max = self.active_axes.get_xlim()
            full_scale = x_max - x_min
            self.active_axes.set_xlim(
                xmin - 0.1 * full_scale, xmax - 0.1 * full_scale)
        elif key == QtCore.Qt.Key_Right:
            x_min, x_max = self.active_axes.get_xlim()
            full_scale = x_max - x_min
            self.active_axes.set_xlim(
                xmin + 0.1 * full_scale, xmax + 0.1 * full_scale)
        elif key == QtCore.Qt.Key_Up:
            y_min, y_max = self.active_axes.get_ylim()
            full_scale = y_max - y_min
            self.active_axes.set_xlim(
                ymin + 0.1 * full_scale, ymax + 0.1 * full_scale)
        elif key == QtCore.Qt.Key_Down:
            y_min, y_max = self.active_axes.get_ylim()
            full_scale = y_max - y_min
            self.active_axes.set_xlim(
                ymin + 0.1 * full_scale, ymax + 0.1 * full_scale)
        else:
            return

        self.rescale_and_draw()

        super(MatplotlibZoomWidget, self).keyEvent(event)

    def focusInEvent(self, event):
        print ("focus!")
        super(MatplotlibZoomWidget, self).focusInEvent(event)

    def grab_line_closest_to(self, x, y):
        y = self.height() - y
        trans = self.axes.transData.inverted()
        x, y = trans.transform([x, y])
        selected = -1
        min_distance = np.inf

        for idx, line in enumerate(self.axes.lines):
            if len(line.get_xdata()) > 0:
                y_line = np.interp(x, line.get_xdata(), line.get_ydata())
                #dist = y-y_line
                print(y_line)
                line_point = self.axes.transData.transform([x, y_line])
                my_point = self.axes.transData.transform([x, y])

                distance = abs(line_point[1] - my_point[1])
                print(distance)
                if distance < min_distance and distance < 10:
                    min_distance = distance
                    selected = idx
        print("line " + str(selected) + " selected!")


class ActionManager():
    def __init__(self, parent):
        self.parent = parent
        
        self.plotToggleLControlAction = self.create_action(parent, "Toggle &Left Axes Control", slot=self.toggleLControl, shortcut=QtGui.QKeySequence("Ctrl+L"),
                                                              icon="toggleLeft", tip="Toggle whether the mouse adjusts Left axes pan and zoom", checkable=True)

        self.plotToggleRControlAction = self.create_action(parent, "Toggle &Right Axes Control", slot=self.toggleRControl, shortcut=QtGui.QKeySequence("Ctrl+R"),
                                                              icon="toggleRight", tip="Toggle whether the mouse adjusts right axes pan and zoom", checkable=True)

        self.plotToggleXControlAction = self.create_action(parent, "Toggle &X Axes Control", slot=self.toggleXControl, shortcut=QtGui.QKeySequence("Ctrl+X"),
                                                              icon="toggleX", tip="Toggle whether the mouse adjusts x axis pan and zoom", checkable=True)

        self.plotAutoScaleXAction = self.create_action(parent, "Auto Scale X", slot=self.toggleAutoScaleX, shortcut=QtGui.QKeySequence("Ctrl+A"),
                                                          icon="toggleAutoScaleX", tip="Turn autoscale X on or off", checkable=True)

        self.plotAutoScaleLAction = self.create_action(parent, "Auto Scale L", slot=self.toggleAutoScaleL, shortcut=QtGui.QKeySequence("Ctrl+D"),
                                                          icon="toggleAutoScaleL", tip="Turn autoscale Left Y on or off", checkable=True)

        self.plotAutoScaleRAction = self.create_action(parent, "Auto Scale R", slot=self.toggleAutoScaleR, shortcut=QtGui.QKeySequence("Ctrl+E"),
                                                          icon="toggleAutoScaleR", tip="Turn autoscale Right Y on or off", checkable=True)

        self.plotDragZoomAction = self.create_action(parent, "Drag to zoom", slot=self.toggleDragZoom, shortcut=QtGui.QKeySequence("Ctrl+Z"),
                                                        icon="zoom", tip="Turn drag to zoom on or off", checkable=True)

        self.plotPanAction = self.create_action(parent, "Drag to Pan", slot=self.togglePan, shortcut=QtGui.QKeySequence("Ctrl+P"),
                                                   icon="pan", tip="Turn drag to Pan on or off", checkable=True)

        self.plotSelectAction = self.create_action(parent, "Drag to Select", slot=self.toggleSelect, shortcut=QtGui.QKeySequence("Ctrl+L"),
                                                      icon="select", tip="Turn drag to Select on or off", checkable=True)

        self.plotClearSelectAction = self.create_action(parent, "Hide selection box", slot=self.hide_selection_box,
                                                           icon="clear_select", tip="Hide Selection box", checkable=False)

        self.changeXscale = self.create_action(parent, "Set X log", slot=self.setXscale, shortcut=None,
                                                  icon="logX", tip="Set the x scale to log")
        self.changeYscale = self.create_action(parent, "Set Y log", slot=self.setYscale, shortcut=None,
                                                  icon="logY", tip="Set the y scale to log")
        self.changeYRscale = self.create_action(parent, "Set YR log", slot=self.setYRscale, shortcut=None,
                                                   icon="logY", tip="Set the yr scale to log")

        #self.clearPlotAction = self.create_action(parent, "Clear Plot", slot=self.clear_plot, shortcut=None,
        #                                            icon="clear_plot", tip="Clears the data arrays")

                 
        self.actions = [self.plotToggleXControlAction, self.plotToggleLControlAction, 
                        self.plotToggleRControlAction, self.plotAutoScaleXAction, 
                        self.plotAutoScaleLAction, self.plotAutoScaleRAction,
                        self.plotDragZoomAction, self.plotDragZoomAction,
                        self.plotPanAction, self.plotSelectAction,
                        self.plotClearSelectAction, self.plotClearSelectAction,
                        self.changeXscale, self.changeYscale, self.changeYRscale]
                       # self.clearPlotAction]

        self.saveFigAction = self.create_action(parent, "&Save Figure", slot=self.save_fig, shortcut=QtGui.QKeySequence.Save,
                                                       icon=None, tip="Save the current figure")
                                                       
    def create_action(self, parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
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
        
    def update_current_widget(self, current_widget):
        self.current_widget = current_widget
        
        self.plotToggleXControlAction.setChecked(current_widget.control_X_on)
        self.plotToggleLControlAction.setChecked(current_widget.control_Y_on)
        self.plotToggleRControlAction.setChecked(current_widget.control_R_on)
        
        mode = current_widget.mouseMode
        self.plotDragZoomAction.setChecked(mode==current_widget.ZOOM_MODE)
        self.plotPanAction.setChecked(mode==current_widget.PAN_MODE)
        self.plotSelectAction.setChecked(mode==self.current_widget.SELECT_MODE)
        
        self.plotAutoScaleXAction.setChecked(current_widget.autoscale_X_on)
        self.plotAutoScaleLAction.setChecked(current_widget.autoscale_L_on)
        self.plotAutoScaleRAction.setChecked(current_widget.autoscale_R_on)

    def toggleLControl(self):
        if self.plotToggleLControlAction.isChecked():
            self.plotAutoScaleLAction.setChecked(False)
        self.updateZoomSettings()

    def toggleRControl(self):
        if self.plotToggleRControlAction.isChecked():
            self.plotAutoScaleRAction.setChecked(False)
        self.updateZoomSettings()

    def toggleXControl(self):
        if self.plotToggleXControlAction.isChecked():
            self.plotAutoScaleXAction.setChecked(False)
        self.updateZoomSettings()

    def toggleAutoScaleX(self):
        if self.plotAutoScaleXAction.isChecked():
            self.plotToggleXControlAction.setChecked(False)
        else:
            self.plotToggleXControlAction.setChecked(True)
        self.updateZoomSettings()

    def toggleAutoScaleL(self):
        if self.plotAutoScaleLAction.isChecked():
            self.plotToggleLControlAction.setChecked(False)
        else:
            self.plotToggleLControlAction.setChecked(True)
        self.updateZoomSettings()

    def toggleAutoScaleR(self):
        if self.plotAutoScaleRAction.isChecked():
            self.plotToggleRControlAction.setChecked(False)
        else:
            self.plotToggleRControlAction.setChecked(True)
        self.updateZoomSettings()

    def toggleDragZoom(self):
        if self.plotPanAction.isChecked():
            self.plotPanAction.setChecked(False)
        if self.plotSelectAction.isChecked():
            self.plotSelectAction.setChecked(False)
        self.updateZoomSettings()    

    def togglePan(self):
        if self.plotDragZoomAction.isChecked():
            self.plotDragZoomAction.setChecked(False)
        if self.plotSelectAction.isChecked():
            self.plotSelectAction.setChecked(False)
        self.updateZoomSettings()

    def toggleSelect(self):
        if self.plotDragZoomAction.isChecked():
            self.plotDragZoomAction.setChecked(False)
        if self.plotPanAction.isChecked():
            self.plotPanAction.setChecked(False)
        self.updateZoomSettings()

    def hide_selection_box(self):
        if self.current_widget.selection_showing:
            self.current_widget.select_rectangle.remove()
            self.current_widget.selection_showing = False
            self.current_widget.figure.canvas.draw()
            self.current_widget.emit(SIGNAL("removed_selection_box()"))

    def setXscale(self):
        self.set_Xaxis_scale(self.current_widget.axes)

    def setYscale(self):
        self.set_Yaxis_scale(self.current_widget.axes)

    def setYRscale(self):
        self.set_Yaxis_scale(self.current_widget.axesR)

    def clear_plot(self):
        self.data_array = np.array([])
        self.current_widget.emit(SIGNAL("data_array_updated(PyQt_PyObject)"),
                                 self.data_array)

        
    # change the x axis scale to linear if it was log and reverse
    def set_Xaxis_scale(self, axis):
        curscale = axis.get_xscale()
#        print curscale
        if curscale == 'log':
            axis.set_xscale('linear')
        elif curscale == 'linear':
            axis.set_xscale('log')

    # change the y axis scale to linear if it was log and reverse
    def set_Yaxis_scale(self, axis):
        curscale = axis.get_yscale()
#        print curscale
        if curscale == 'log':
            axis.set_yscale('linear')
        elif curscale == 'linear':
            axis.set_yscale('log')

    def save_fig(self):
        fname = str(QtGui.QFileDialog.getSaveFileName(
            self.parent, 'Open settings file', './'))
        if fname:
            self.current_widget.figure.savefig(fname, dpi = 600)
    
    def remove_fit(self):
        self.current_widget.emit(SIGNAL("remove_fit()"))

    def updateZoomSettings(self):
        self.current_widget.setActiveAxes(self.plotToggleXControlAction.isChecked(),
                                     self.plotToggleLControlAction.isChecked(),
                                     self.plotToggleRControlAction.isChecked())
        if self.plotDragZoomAction.isChecked():
            self.current_widget.set_mouse_mode(self.current_widget.ZOOM_MODE)
        elif self.plotPanAction.isChecked():
            self.current_widget.set_mouse_mode(self.current_widget.PAN_MODE)
        elif self.plotSelectAction.isChecked():
            self.current_widget.set_mouse_mode(self.current_widget.SELECT_MODE)

        self.current_widget.set_autoscale_x(self.plotAutoScaleXAction.isChecked())
        self.current_widget.set_autoscale_yL(self.plotAutoScaleLAction.isChecked())
        self.current_widget.set_autoscale_yR(self.plotAutoScaleRAction.isChecked())
        
        
        
def get_axis_limits(axis):
    x_min, x_max = axis.get_view_interval()
    if axis.get_scale() == 'log':
        x_min = np.log10(x_min)
        x_max = np.log10(x_max)
    return [x_min, x_max]


def calculate_scaling(lim, total_size):
    return (lim[1] - lim[0]) / total_size


def convert_lim(axis, lim):
    if axis.get_scale() == 'log':
        return [10**lim[0], 10**lim[1]]
    else:
        return lim

class Printer(QtGui.QWidget):
    def to_print(self,mode, limits):
        print(mode, limits)


class ExamplePlotDisplay(QtGui.QMainWindow):
    def __init__(self, xdata=None, ydata=None):
        super(ExamplePlotDisplay, self).__init__()
        
        self.action_manager = ActionManager(self)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Plot')
        self.toolbar = self.addToolBar('Plot')
        for action in self.action_manager.actions:
            fileMenu.addAction(action)
            self.toolbar.addAction(action)
            
        self.centralZone = QtGui.QMdiArea()
        self.centralZone.subWindowActivated.connect(
            self.update_current_widget)
        self.setCentralWidget(self.centralZone)
        self.create_dw("Window 1", xdata=xdata, ydata=ydata)
        self.create_dw("Window 2", xdata=xdata, ydata=ydata)
        
    def create_dw(self, name, xdata=None, ydata=None):
        dw = MatplotlibZoomWidget()
        if not (xdata is None or ydata is None):
            dw.axes.plot(xdata,ydata)
        
        self.centralZone.addSubWindow(dw)
        dw.show()
    
    def update_current_widget(self):
        current_window = self.centralZone.activeSubWindow()
        if current_window:
            self.action_manager.update_current_widget(current_window.widget())

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    x = np.arange (0, 10)
    y = x **2
    
    ex = ExamplePlotDisplay(xdata=x, ydata=y)
    ex.show()
    sys.exit(app.exec_())