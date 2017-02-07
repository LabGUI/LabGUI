# -*- coding: utf-8 -*-
"""
Created on Tue Mar 03 11:13:05 2015

Copyright (C) 10th april 2015 Helene Seiler
License: see LICENSE.txt file
"""

import sys
from PyQt4 import QtGui
import numpy as np
import pyqtgraph as pg


class PyQtGraphWidget(pg.PlotWidget):

    def __init__(self, n_curves=1, parent=None):
        super(PyQtGraphWidget, self).__init__(parent)
        # self.pw=pg.PlotWidget(name="test")

        print("number of curves=%i" % (n_curves))

        self.resize(500, 600)
        self.setWindowTitle("an example")
        self.n_curves = n_curves

        self.pl = []

        for i in range(self.n_curves):
            self.pl.append(self.plot(pen=i))

        self.ROI = []
        # self.graphe=self.win.addPlot(title='myplot')

    # def setXRange(self, x_min, x_max):
     #   self.pw.setXRange(x_min, x_max)

    # def setYRange(self, y_min, y_max):
     #   self.pw.setYRange(y_min, y_max)

    # def setTitle(self,newtitle):
     #   self.pw.setWindowTitle(newtitle)

    def add_datacursor(self, axis, movable):
        if axis == "y":
            line = pg.InfiniteLine(angle=0, movable=True)
        elif axis == "x":
            line = pg.InfiniteLine(angle=90, movable=True)

        self.addItem(line)

        return line

    def update_plot(self, xdata, plot_idx=None, ydata=None):
        print("idx", plot_idx)
        if ydata == None:
            idx = np.arange(0, len(xdata), 1)
            self.pl[plot_idx].setData(x=idx, y=xdata)
        else:
            self.pl[plot_idx].setData(x=xdata, y=ydata)

    def clear_line(self, plot_idx=0):
        self.pl[plot_idx].clear()

    def add_rect_ROI(self, x_1, x_2, y_1, y_2):
        self.ROI.append(pg.RectROI([x_1, x_2], [y_1, y_2], pen=4))
        self.addItem(self.ROI[-1])

    def get_updated_ROI_positions(self, ROI_idx):
        return self.ROI[ROI_idx].pos(), self.ROI[ROI_idx].size()


class PyQtImageWidget(pg.PlotWidget):

    def __init__(self):
        super(PyQtImageWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        #self.img_array = np.zeros((1000, CHUNKSZ/2+1))

        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0, 255, 255, 255], [255, 255, 0, 255], [
                         0, 0, 0, 255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        self.img.setLevels([-50, 40])

        #freq = np.arange((CHUNKSZ/2)+1)/(float(CHUNKSZ)/FS)
        #yscale = 1.0/(self.img_array.shape[1]/freq[-1])
        #self.img.scale((1./FS)*CHUNKSZ, yscale)

        #self.setLabel('left', 'Frequency', units='Hz')

        #self.win = np.hanning(CHUNKSZ)
        # self.show()
    def setImage(self, img_array):
        self.img.setImage(self.img_array, autoLevels=False)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = PyQtGraphWidget()
    ex.show()
    #ex.setTitle("essai de titre")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
