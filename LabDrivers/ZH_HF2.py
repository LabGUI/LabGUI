#!/usr/bin/env python
#import visa
from . import Tool
import numpy as np
import time
from collections import OrderedDict
try:
    import zhinst.ziPython
    import zhinst.utils
except:
    pass
#print("Zurich Instruments drivers unavailable")
# use an ordered dictionary so that the parameters show up in a pretty order :)
param = OrderedDict([('X', 'V'), ('Y', 'V'), ('X2', 'V'),
                     ('Y2', 'V'), ('X3', 'V'), ('Y3', 'V')])

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):
    def __init__(self, name, debug=False):
        super(Instrument, self).__init__(
            None, name='ZH_HF2', debug=debug, interface=INTERFACE)
        # self.ID_name=name
       # self.debug=debug
       # self.resource_name = name

        if name != 'default':

            #            module_name=import_module("."+name,package=LABDRIVER_PACKAGE_NAME)
            #            else:
            #                module_name=import_module("."+name,package=LABDRIVER_PACKAGE_NAME)
            self.channels = []
            for chan, u in list(param.items()):
                # initializes the first measured value to 0 and the channels' names
                self.channels.append(chan)
                self.units[chan] = u
                self.last_measure[chan] = 0
                self.channels_names[chan] = chan

            if not self.DEBUG:
                self.daq = zhinst.ziPython.ziDAQServer('localhost', 8005)

    def measure(self, channel):

        if channel in param:
            if channel == 'X':
                sample = self.get_sample('/dev855/demods/0/sample')
                answer = sample['x'][0]
            elif channel == 'Y':
                sample = self.get_sample('/dev855/demods/0/sample')
                answer = sample['y'][0]
            elif channel == 'X2':
                sample = self.get_sample('/dev855/demods/1/sample')
                answer = sample['x'][0]
            elif channel == 'Y2':
                sample = self.get_sample('/dev855/demods/1/sample')
                answer = sample['y'][0]
            elif channel == 'X3':
                sample = self.get_sample('/dev855/demods/2/sample')
                answer = sample['x'][0]
            elif channel == 'Y3':
                sample = self.get_sample('/dev855/demods/2/sample')
                answer = sample['y'][0]
            self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def get_sample(self, stri):
        if not self.DEBUG:
            try:
                return self.daq.getSample(stri)
            except:
                time.sleep(0.1)
                print("Zurich has died for a moment!")
                return self.daq.getSample(stri)
        else:
            return np.random.random()

# Plan to move to using Instrument as the name within, but for back-compatibility
# include this (so you can still use SRS830.SRS830 instead of SRS830.Instrument)
#SRS830 = Instrument

    # if run as own program
    # if (__name__ == '__main__'):

     #   lockin = device('dev9')
     #   lockin.set_ref_internal  # no averaging
     #   lockin.close()
