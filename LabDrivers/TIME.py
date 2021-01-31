# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 05:09:37 2013

@author: pf, zackorenberg
"""

import LabDrivers.Tool as Tool
from PyQt5.QtCore import pyqtSignal
import time
import logging
param = {'Time': 's', 'dt': 's'}

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):

    time_change = None
    def __init__(self, resource_name=None, debug=False, **kwargs):
        resource_name = 'ComputerTime'
        super(Instrument, self).__init__(resource_name, name='TIME',
                                         debug=debug, interface=INTERFACE,
                                         **kwargs)

        self.t_start = 0
#------------------------------------------------------------------------------

    def initialize(self):
        """reset the time to the current time"""
        self.t_start = time.time()
        if callable(self.time_change): # set t_start in instr_hub
            self.time_change(self.t_start)

    def measure(self, channel='Time'):

        logging.debug("TIME measure %s" % (channel))

        if channel in self.last_measure:

            if channel == 'dt':

                answer = round(time.time() - self.t_start, 2)
            else:

                answer = time.time()
        else:

            print(("you are trying to measure a non existent channel : " + channel))
            print(("existing channels :", self.channels))
            answer = None
        self.last_measure[channel] = answer
        return answer
