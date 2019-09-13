# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 12:24:15 2014

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""
from numpy import arange, mod
fs = 35
fsl = 25
marker_size = 18

marker_set = ["None", "o", "v", "^", ">",
              "<", "s", "d", "h", "x", "+", "|", "_"]
line_set = ['-', '--', '-.', ':', 'None']

color_blind_max_set = ['#332288', '#6699CC', '#88CCEE', '#44AA99', '#117733',
                       '#999933', '#DDCC77', '#661100', '#CC6677', '#AA4466', '#882255', '#AA4499']


def color_blind_friendly_colors(nb_lines=None):
    if nb_lines == 1:
        return ['#4477AA']
    elif nb_lines == 2:
        return ['#4477AA', '#CC6677']
    elif nb_lines == 3:
        return ["#4477AA", "#DDCC77", "#CC6677"]
    elif nb_lines == 4:
        return ["#4477AA", "#117733", "#DDCC77", "#CC6677"]
    elif nb_lines == 5:
        return ['#332288', '#88CCEE', '#117733', '#DDCC77', '#CC6677']
    elif nb_lines == 6:
        return ['#332288', '#88CCEE', '#117733', '#DDCC77', '#CC6677', '#AA4499']
    elif nb_lines == 7:
        return ['#332288', '#88CCEE', '#44AA99', '#117733', '#DDCC77', '#CC6677', '#AA4499']
    elif nb_lines == 8:
        return ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#AA4499']
    elif nb_lines == 9:
        return ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
    elif nb_lines == 10:
        return ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#661100', '#CC6677', '#882255', '#AA4499']
    elif nb_lines == 11:
        return ['#332288', '#6699CC', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#661100', '#CC6677', '#882255', '#AA4499']
    elif nb_lines == 12:
        return color_blind_max_set
    else:
        return [color_blind_max_set[mod(i, 12)] for i in range(nb_lines)]


def generate_log_scale_tick_lines(expo, display="odd"):

    if display == "odd":
        parity = 1
    elif display == "even":
        parity = 0
    ticks = []
    ticks_lab = []
    for e in expo:
        for i in arange(1, 10, 1):
            if abs(mod(e, 2)) == parity and i == 1:
                ticks_lab.append(r"$10^{%i}$" % (e))
            else:
                ticks_lab.append(r"")
            ticks.append(i * pow(10, e))

    return ticks, ticks_lab


if __name__ == "__main__":
    print((color_blind_friendly_colors(50)))
#    import pylab as plt
#    import numpy as np
#    x=np.arange(10)
#
#    fontProperties = {'family':'serif','serif':['normal'],'weight' : 'normal', 'size' : 30}
#    plt.rc('text', usetex=True)
#    plt.rc('font', **fontProperties)
#    plt.rcParams['axes.linewidth'] = 1.5 #set the value globally
#    fig=plt.figure()
#    ax=fig.add_subplot(111)
#    ax.plot(x)
#    ax.tick_params(axis='x', pad=10)
#    plt.show()
