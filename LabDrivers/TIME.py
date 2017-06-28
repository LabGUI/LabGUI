# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 05:09:37 2013

@author: pf
"""

import LabDrivers.Tool as Tool
import time
import logging
param = {'Time': 's', 'dt': 's'}

INTERFACE = Tool.INTF_NONE

class Instrument(Tool.MeasInstr):

    # a tag that will be initiallized with the same name than the module
    # const_label=''

    def __init__(self, resource_name = None, debug = False, **kwargs):
        resource_name = 'Time'
        super(Instrument, self).__init__(resource_name, name = 'TIME', debug=debug,
                                         interface = INTERFACE, **kwargs)
        self.t_start = 0
#------------------------------------------------------------------------------

    def initialize(self):
        self.t_start = time.time()

    def measure(self, channel='Time'):
        logging.debug("TIME measure %s"%(channel))
        if channel in self.last_measure:

            if channel == 'dt':
                answer = round(time.time() - self.t_start, 2)
            else:
                answer = time.time()
        else:
            print(("you are trying to measure a non existent channel : " + channel))
            print(("existing channels :", self.channels))
            answer = None
        return answer
