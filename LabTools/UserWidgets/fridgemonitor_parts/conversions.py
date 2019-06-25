# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 13:39:12 2016

@author: matei
"""

from numpy import log10 as log10
from numpy import cos as cos
from numpy import arccos as acos




# the function for the calibration can be found in the documentation from
# Lakeshore Cryogenics


def convert_RX102A(resistance):
    '''
    This method converts the RX-102A thermometer resistance value to calibrated temperature in Kelvin. 
    This thermometer is usually on the dilution refrigerator (Faraday Cage) at multiple stages -> 1KPot, Still, Intermetidate Cold Plate and Mixing Chamber.
    '''
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
        temperature = 0

    return temperature  # we return the list "temperature"


def convert_RX202A(resistance):
    '''
    This method converts the RX2102A thermometer resistance value to calibrated temperature in Kelvin. 
    This thermometer is usually on the dilution refrigerator (Faraday Cage) at the Cold Plate.
    '''
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
        temperature = 0

    return temperature  # we return the list "temperature"


def CMN_calc(raw_value):
    return -4.36894/(-raw_value*1000+2.93629)
        