# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 15:08:20 2016

@author: matei

This method converts the RX-202A thermometer resistance value to calibrated temperature in Kelvin.
This thermometer is usually on the dilution refrigerator (Faraday Cage) at the cold plate level 
(in the field region -> thus when applying significantly large magnitic fields this thermometer is not reliable anymore).
"""

from numpy import log10 as log10
from numpy import cos as cos
from numpy import arccos as acos

import numpy as np

# the function for the calibration can be found in the documentation from
# Lakeshore Cryogenics


def R_to_T(resistance):

    # resistance must be in Ohm
    if resistance < 2843.53 and resistance >= 2243.15:  # between 5K and 40K
        ZL = 3.27800000000  # minimum log10 of results
        ZU = 3.46671731726  # maximum log10 of results
        A0 = 102.338126
        A1 = -161.190611
        A2 = 94.158738
        A3 = -43.080048
        A4 = 15.317949
        A5 = -3.881270
        A6 = 0.540313
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
        # compute temperature from coefficients above (Chebychev polynomial)
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(
            4 * acos(k)) + A5 * cos(5 * acos(k)) + A6 * cos(6 * acos(k))

    elif resistance < 5166.86 and resistance >= 2843.53:  # between 650mK and 5K
        ZL = 3.44161440913  # minimum log10 of results
        ZU = 3.74909980595  # maximum log10 of results
        A0 = 2.129752
        A1 = -2.281779
        A2 = 0.981996
        A3 = -0.386190
        A4 = 0.143467
        A5 = -0.050844
        A6 = 0.017569
        A7 = -0.006164
        A8 = 0.002311
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
        # compute temperature from coefficients above (Chebychev polynomial)
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(4 * acos(k)) + A5 * cos(
            5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k))
            
    elif resistance <= 69191.1 and resistance >= 5166.86:  # between 50mK and 650mK
        ZL = 3.67248634198  # minimum log10 of results
        ZU = 5.08000000000  # maximum log10 of results
        A0 = 0.216272
        A1 = -0.297572
        A2 = 0.146302
        A3 = -0.083696
        A4 = 0.026669
        A5 = -0.019932
        A6 = 0.003085
        A7 = -0.004804
        A8 = 0.000177
        A9 = -0.001218
        A10 = 0.000286
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
        # compute temperature from coefficients above (Chebychev polynomial)
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(4 * acos(
            k)) + A5 * cos(5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k)) + A9 * cos(9 * acos(k)) + A10 * cos(10 * acos(k))

    else:
        temperature = 99999

    return temperature  # we return the list "temperature"


def T_to_R(T):

    Res_max = 69191.1
    Res_min = 2243.15
    Res_step = .5

    Res_range = np.arange(Res_max, Res_min - Res_step, -Res_step)
    convert_vector = np.vectorize(R_to_T)

    T_range = convert_vector(Res_range)

    resistance = np.interp(T, T_range, Res_range)
    return resistance

if __name__ == "__main__":
#    print(R_to_T(2191.98))
    print(T_to_R(40))
