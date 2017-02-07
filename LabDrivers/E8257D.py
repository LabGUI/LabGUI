# -*- coding: utf-8 -*-
"""
Created on Wed June 12 17:26:26 2014
Agilent E4400B 1GHz signal generator
@author: pfduc
"""

#!/usr/bin/env python
import numpy as np
import time
import Tool # changed from "from . import Tool" (Simon, 2016-09-11)

param = {'V': 'V', 'freq': 'Hz'}

INTERFACE = Tool.INTF_VISA

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, V_step_limit=None):
        super(Instrument, self).__init__(resource_name, 'E4400B', debug=debug, interface = INTERFACE)

    def __del__(self):
        super(Instrument, self).__del__()

    def measure(self, channel='V'):
        if channel in self.last_measure:
            if not self.debug:
                if channel == 'V':
                    # 0 #this is to be defined for record sweep
                    answer = self.ask(':READ?')
                    answer = float(answer.split(',', 1)[0])
                if channel == 'freq':
                    answer = self.get_frequency()
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def reset(self):
        if not self.debug:
            self.write('*RST')
            time.sleep(1)

    def set_frequency(self, f):
        if not self.debug:
            self.write(':FREQ ' + str(f) + 'Hz')

    def get_frequency(self):
        f = self.ask(':FREQ?')
        answer = float(f[1:-5]) * np.power(10, float(f[-2]))
        return answer

    def sweep_frequency(self, fstart, fstop, df, dwell=2e-3):
        # NOTE : df should be multiple of 
        freq_range = np.arange(fstart, fstop + df, df)
        for freq in freq_range:
            self.set_frequency(freq)
            time.sleep(dwell)

if __name__ == "__main__":

    i = Instrument('GPIB0::19', debug=False)
    i.set_frequency(6.12345e+9)
    f = i.measure("freq")
    print(f)
