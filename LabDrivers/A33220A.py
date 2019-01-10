# -*- coding: utf-8 -*-
"""
Created on Fri Apr 06 09:17:04 2018

@author: pfduc
"""

import random
import numpy as np
import logging

try:
    from . import Tool
except:
    import Tool

param = {'Voltage': 'V'}


INTERFACE = Tool.INTF_GPIB


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):

        # manage the presence of the keyword interface which will determine
        # which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE

        super(Instrument, self).__init__(resource_name, 'A33220A', debug=debug,
                                         interface=interface, **kwargs)

    def measure(self, channel):

        if channel in self.last_measure:
            if not self.DEBUG:

                if channel == 'Voltage':
                    return float(self.ask('VOLT?'))
                else:
                    answer = None
#
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = np.nan
        return answer


if (__name__ == '__main__'):

    i = Instrument("GPIB0::5", False, interface=Tool.INTF_PROLOGIX)

    print(i.ask("*IDN?"))
    print(i.measure('Voltage'))
    i.close()
