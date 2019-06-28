# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 17:50:48 2014

@author: pf
"""

from numpy import exp as __exp
from numpy import float64 as __float64
from numpy import array as __array
from numpy import power as __power
#import numpy as np
# np.float32()


def exp_raise(t, Y_inf, tau, t_offset):
    """f(t) = Y_{\u221E}e<sup>{-(t-t<inf>{offset}</inf>)/\u03C4}</sup>"""
    t = __array(t, dtype=__float64)
    return Y_inf * (1 - __exp(-((t-t_offset) / tau)))


def exp_decay(t, Y_inf, dY, tau, t_offset):
    """f(t) = -Y_{\u221E} + \u0394 Y e^{-(t-t_{offset})/\u03C4}"""
    t = __array(t, dtype=__float64)
    return -Y_inf + dY * __exp(-((t-t_offset) / tau))


# def integrate(x, Y):
#    """f(x) = undefined yet"""
#    pass


def linear(x, m, h):
    """f(x) = m x + h"""
    x = __array(x, dtype=__float64)
    return m * x + h


def square(x, a, b, c):
    """f(x) = a x^2 + b x + c"""
    x = __array(x, dtype=__float64)
    return a * x * x + b * x + c


def vcrit(T, vc0, nu, Tl=2.17):
    """f(T) = v_{c0} {(1-\frac{T}{T_{\u03BB}})}<sup>{\u03BD}</sup>"""
    T = __array(T, dtype=__float64)
    return vc0 * __power(1 - T / Tl, nu)
