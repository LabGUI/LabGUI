# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 11:25:22 2013

Copyright (C) 10th april 2015 Benjamin Schmidt
License: see LICENSE.txt file
"""

from PyQt4 import QtCore, QtGui
from matplotlibwidget import MatplotlibWidget
import numpy as np
import matplotlib as mpl
import logging

from QtTools import ZOOM_MODE, PAN_MODE, SELECT_MODE

class SIAxesLabel():
    SI_prefixes = {-21: 'y', -18: 'z', -15: 'a', -12: 'p', -9: 'n', -6: 'u', -3: 'm',
                   0: '', 3: 'k', 6: 'M', 9: 'G', 12: 'T', 15: 'P', 18: 'E', 21: 'Z', 24: 'Y'}

    def __init__(self, axes, quantity=[], units=[], power=[]):
        self.axes = axes
        self.quantity = quantity
        self.units = units
        self.power = power

    def check_scale(self, ax):
        ymin, ymax = ax.get_ylim()
        if max(abs(ymin), abs(ymax)) > 1000:
            return 3
        elif max(abs(ymin), abs(ymax)) < 1:
            return -3
        else:
            return 0

    # buggy, don't call this!!!!
    def adjust_units(self):
        chk = self.check_scale(self.axes)
        if chk != 0:
            self.power += chk
            self.axes.set_ylim(np.array(self.axes.get_ylim()) / 10 ** chk)
            self.adjust_units()
        label_str = ""

        for quant, unit in zip(self.quantity, self.units):
            label_str = label_str + quant
            label_str = label_str + \
                "(%s%s), " % (self.SI_prefixes[self.power], unit)

        label_str.rstrip(', ')

        self.axes.set_ylabel(label_str)


class MatplotlibZoomWidget(MatplotlibWidget):
    #SI_prefixes = {-15: 'a', -12: 'p', -9: 'n', -6: 'u', -3: 'm', 0: '', 3: 'k', 6:'M', 9:'G'}

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

        self.autoscale_x_on = True
        self.autoscale_y_on = True
        self.autoscale_R_on = True

        # Shink current axis by 20%
        #box = self.axes.get_position()
        #axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        #self.legend = self.axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def set_mouse_mode(self, mode):
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

    def check_scale(self, ax):
        ymin, ymax = ax.get_ylim()
        if max(abs(ymin), abs(ymax)) > 1000:
            return 3
        elif max(abs(ymin), abs(ymax)) < 1:
            return -3
        else:
            return 0

    def autoscale_axes(self, axes=None, scale_x=True, scale_y=True, span_x=0,
                       margin_y=0.05):

        if axes == None:
            axes = self.axes
        x_max = -np.inf
        x_min = np.inf

        y_max = -np.inf
        y_min = np.inf

        has_data = False

        for line in axes.get_lines():
            xdata = line.get_xdata()

            if xdata != np.array([]):

                x_max = max(x_max, np.amax(xdata))
                x_min = min(x_min, np.amin(xdata))
                has_data = True
            ydata = line.get_ydata()

            if ydata != np.array([]):
                y_max = max(y_max, np.amax(ydata))
                y_min = min(y_min, np.amin(ydata))
                has_data = True

        if x_max == x_min:
            x_min = x_max - 1

        if scale_x and has_data:
            if span_x == 0:
                axes.set_xlim(x_min, x_max)
            else:
                axes.set_xlim(x_max - span_x, x_max)

        if scale_y and has_data:
            if y_max == y_min:
                y_min = 0
                y_max = y_max * 2
                margin = 0
            else:
                margin = (y_max - y_min) * margin_y

            axes.set_ylim(y_min - margin, y_max + margin)

    def set_autoscale_x(self, setting):
        self.autoscale_x_on = setting
        if setting:
            self.rescale_and_draw()

    # def scale_x():
    def set_autoscale_y(self, setting):
        self.set_autoscale_yL(setting)

    def set_autoscale_yL(self, setting):
        self.autoscale_y_on = setting
        if setting:
            self.rescale_and_draw()

    def set_autoscale_yR(self, setting):
        self.autoscale_R_on = setting
        if setting:
            self.rescale_and_draw()

    # buggy! don't call this!
    def adjust_units(self):
        chk = self.check_scale(self.axes)
        if chk != 0:
            self.left_pow += chk
            self.axes.set_ylim(np.array(self.axes.get_ylim()) / 10 ** chk)
            self.axes.set_ylabel("Voltage (%sV)" %
                                 self.SI_prefixes[self.left_pow])
            self.adjust_units()

    def rescale_and_draw(self):
        # self.adjust_units()
        self.autoscale_axes(axes=self.axes, scale_x=self.autoscale_x_on,
                            scale_y=self.autoscale_y_on)

        if self.usingR:
            self.autoscale_axes(axes=self.axesR, scale_x=False,
                                scale_y=self.autoscale_R_on)
#        self.axes.relim()
#        self.axes.autoscale_view()
#        self.axesR.relim()
#        self.axesR.autoscale_view()
#        self.figure.canvas.draw()
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


# This snippet makes it run as a standalone program
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = MatplotlibZoomWidget()
    form.set_mouse_mode(form.ZOOM_MODE)
    pt=Printer()
    pt.connect(form,QtCore.SIGNAL("limits_changed(int,PyQt_PyObject)"),pt.to_print)
    form.show()
    app.exec_()
