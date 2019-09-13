# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 13:39:12 2016

@author: matei

This method converts the RX-102A thermometer resistance value to calibrated temperature in Kelvin.
This thermometer is usually on the dilution refrigerator (Faraday Cage) at multiple stages -> 1KPot, Still, Intermetidate Cold Plate and Mixing Chamber.
"""

from numpy import log10 as log10
from numpy import cos as cos
from numpy import arccos as acos

import numpy as np

# the function for the calibration can be found in the documentation from
# Lakeshore Cryogenics


def R_to_T(resistance):

    # resistance must be in Ohm
    if resistance < 1239.03 and resistance >= 1049.08:  # between 6.76K and 40K
        ZL = 2.95500000000  # minimum log10 of results
        ZU = 3.10855552727  # maximum log10 of results
        A0 = 3074.395992
        A1 = -5680.735415
        A2 = 4510.873058
        A3 = -3070.206226
        A4 = 1775.293345
        A5 = -857.606658
        A6 = 336.220971
        A7 = -101.617491
        A8 = 21.390256
        A9 = -2.407847
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
        # compute temperature from coefficients above (Chebychev polynomial)
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(
            4 * acos(k)) + A5 * cos(5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k)) + A9 * cos(9 * acos(k))

    elif resistance < 2391.58 and resistance >= 1239.03:  # between 992mK and 6.76K
        ZL = 3.08086045368  # minimum log10 of results
        ZU = 3.44910010859  # maximum log10 of results
        A0 = 2.813252
        A1 = -2.976371
        A2 = 1.299095
        A3 = -0.538334
        A4 = 0.220456
        A5 = -0.090969
        A6 = 0.037095
        A7 = -0.015446
        A8 = 0.005104
        A9 = -0.004254
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
        # compute temperature from coefficients above (Chebychev polynomial)
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(4 * acos(k)) + A5 * cos(
            5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k)) + A9 * cos(9 * acos(k))

    elif resistance <= 63765.1 and resistance >= 2391.58:  # between 50mK and 992mK
        ZL = 3.35453159798  # minimum log10 of results
        ZU = 5.00000000000  # maximum log10 of results
        A0 = 0.300923
        A1 = -0.401714
        A2 = 0.220055
        A3 = -0.098891
        A4 = 0.046804
        A5 = -0.017379
        A6 = 0.009090
        A7 = -0.002703
        A8 = 0.002170
        Z = log10(resistance)  # make sure you have log base 10
        k = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
        # compute temperature from coefficients above (Chebychev polynomial)
        temperature = A0 * cos(0 * acos(k)) + A1 * cos(1 * acos(k)) + A2 * cos(2 * acos(k)) + A3 * cos(3 * acos(k)) + A4 * cos(4 * acos(
            k)) + A5 * cos(5 * acos(k)) + A6 * cos(6 * acos(k)) + A7 * cos(7 * acos(k)) + A8 * cos(8 * acos(k))

    else:
        temperature = 99999

    return temperature  # we return the list "temperature"


def T_to_R(T):

    Res_max = 63765.1
    Res_min = 1049.08
    Res_step = .5

    Res_range = np.arange(Res_max, Res_min - Res_step, -Res_step)
    convert_vector = np.vectorize(R_to_T)

    T_range = convert_vector(Res_range)

    resistance = np.interp(T, T_range, Res_range)
    return resistance


if __name__ == "__main__":
    print(R_to_T(2391.58))
#    print(T_to_R(0.99155))
