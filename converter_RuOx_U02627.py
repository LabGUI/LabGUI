# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:30:14 2013
This method converts the U02627 RuOx thermometer resistance value to calibrated temperature in Kelvin
This thermometer is usually on the Helium-3 cryostat cell for nanofluidics

Copyright (C) 10th april 2015 Michel Savard
License: see LICENSE.txt file
"""
from numpy import log10 as log10
from numpy import cos as cos
from numpy import arccos as acos

import numpy as np

# the function for the calibration can be found in the documentation from
# Lakeshore Cryogenics


def R_to_T(resistance):

    # resistance must be in Ohm
    if resistance > 1676:  # between 300mK and 2.2K
        ZL = 3.19922619413  # minimum log10 of results
        ZU = 3.81987282195  # maximum log10 of results
        A0 = .973123
        A1 = -1.004511
        A2 = 0.397604
        A3 = -.144157
        A4 = .050408
        A5 = -.017547
        A6 = .006314
        A7 = -.002121
        A8 = 0.000407
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)

        # compute temperature from coefficients above
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(
            4 * acos(k)) + A5 * cos(5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k))

    elif resistance >= 1154:  # between 2.2K and 11K
        ZL = 3.05398896134  # minimum log10 of results
        ZU = 3.25850099806  # maximum log10 of results
        A0 = 5.23383
        A1 = -4.796975
        A2 = 1.886803
        A3 = -0.726021
        A4 = .278156
        A5 = -.107016
        A6 = .041521
        A7 = -.015844
        A8 = 0.00691
        A9 = -.002499
        A10 = 0.001198

        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)

        # compute temperature from coefficients above
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(4 * acos(k)) + A5 * cos(
            5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k)) + A9 * cos(9 * acos(k)) + A10 * cos(10 * acos(k))
        #temperature = A0*cos(0*acos(k)) + A1*cos(1*acos(k)) + A2*cos(2*acos(k)) + A3*cos(3*acos(k)) + A4*cos(4*acos(k)) + A5*cos(5*acos(k)) + A6*cos(6*acos(k)) + A7*cos(7*acos(k)) + A8*cos(8*acos(k))
    elif resistance >= 1050:  # between 11K and 40K
        ZL = 3.019185975  # minimum log10 of results
        ZU = 3.07391113361  # maximum log10 of results
        A0 = 20.598498
        A1 = -15.703463
        A2 = 5.639488
        A3 = -1.996474
        A4 = 0.697037
        A5 = -.239353
        A6 = .082146
        A7 = -.03352
        A8 = 0.013951
        A9 = -0.007427
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)

        # compute temperature from coefficients above
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(4 * acos(
            k)) + A5 * cos(5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k)) + A9 * cos(9 * acos(k))

    else:
        temperature = 99999

    return temperature  # we return the list "temperature"


def T_to_R(T):

    Res_max = 5767.87
    Res_min = 1050.9
    Res_step = 1

    Res_range = np.arange(Res_max, Res_min - Res_step, -Res_step)
    convert_vector = np.vectorize(R_to_T)

    T_range = convert_vector(Res_range)

    resistance = np.interp(T, T_range, Res_range)
    return resistance

if __name__ == "__main__":
    print(R_to_T(1663.49393))
