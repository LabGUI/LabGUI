# A class to take care of plotting data
# give it the subplot IDs

import matplotlib
from pylab import *

class cr:
    def __init__(self, subplot_num, label="default", sty='.-b', auto_scale=True): 
        self.subplot_num = subplot_num
        self.data_list = []
        self.time_list = []
        self.sty = sty
        self.label = label
        self.auto_scale = auto_scale
        
    def learn_axes(self, fig, rows, cols):
        ax = fig.add_subplot (rows, cols, self.subplot_num)
        self.line, = ax.plot(0, 0, self.sty)  
        self.ax = ax
        self.fig = fig
        self.txt = text(0.1, 0.80, "Text", fontsize = 14, transform =ax.transAxes)
        ax.set_ylabel (self.label)
        return ax
        
    def set_axes(self, fig, ax):
        self.ax = ax
        self.fig = fig
        self.line, = ax.plot(0, 0, self.sty)
        self.txt = text(0.1, 0.80, "Text", fontsize = 14, transform =ax.transAxes)
        ax.set_ylabel (self.label)
        return ax
    
    def auto_scale_y(self):
        data = self.data_list
        span = max(data.max() - data.min(), 0.1 * data.min())
        return (data.min() - span *0.05), (data.max() + span*0.05)

    def add_point(self, t_current, dat):
        self.data_list = append(self.data_list,dat)
        self.time_list = append(self.time_list,t_current)
        self.line.set_data(self.time_list, self.data_list)
        y1, y2 = self.auto_scale_y()
        self.ax.set_ylim(ymin = y1, ymax = y2)
        self.ax.set_xlim(xmin = 0, xmax = t_current+1)
        self.txt.set_text("%.3f"%dat)
        self.fig.canvas.draw()
        
