# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 14:02:36 2016

@author: schmidtb
"""

#!/usr/bin/env python
from collections import OrderedDict
import random
import logging


try:
    from . import Tool
except:
    import Tool


# use an ordered dictionary so that the parameters show up in a pretty order :)
param = OrderedDict([('Roll', '')])

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__('Dice', name='DICE',
                                         debug=debug, interface=INTERFACE, **kwargs)

    def measure(self, channel='Roll'):
        logging.debug("DICE measure %s" % (channel))
        if channel in param:
            if channel == 'Roll':
                answer = random.randint(1, 6)
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer


if (__name__ == '__main__'):

    from utils import command_line_test

    command_line_test(Instrument)
