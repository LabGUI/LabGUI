# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:02:46 2015

@author: pfduc
"""

#!/usr/bin/env python

'''
class to talk to SCPI-compliant RF sources. Tested on Agilent E4400B
'''

try:
    from . import Tool
except:
    import Tool

from numpy import power

param = {'V': 'V', 'P': 'mbar'}

INTERFACE = Tool.INTF_GPIB


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'A34401A', debug=debug,
                                         interface=INTERFACE, **kwargs)
        if not self.DEBUG:
            chan_names = ['Voltage', 'Pressure']
            for chan, chan_name in zip(self.channels, chan_names):
                self.last_measure[chan] = 0
                self.channels_names[chan] = chan_name

    def measure(self, channel='V'):
        if self.last_measure.has_key(channel):
            if not self.DEBUG:
                if channel == 'V':
                    answer = self.get_voltage()
                elif channel == 'P':
                    # conversion factor from Torr to mbar : 1.333224
                    # source
                    # http://www.nist.gov/pml/div685/grp01/unit_conversions.cfm
                    answer = power(10, self.get_voltage() - 5) * 1.333224
            else:
                answer = 1337
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def get_voltage(self):
        v = self.ask("MEAS:VOLT:DC?")
        mantissa, exponent = v.split("E")
        answer = float(mantissa) * power(10, float(exponent))
        return answer
#    MEASure[:VOLTage][:DC]? [{<
# range
#>|AUTO|MIN|MAX|DEF} [,{<
# resolution
#>|MIN|MAX|DEF}] ]


# if run as own program
if (__name__ == '__main__'):

    i = Instrument('GPIB0::23')
    print(i.identify())
    print (i.measure('V'))
#    print i.measure('P')
    i.close()
