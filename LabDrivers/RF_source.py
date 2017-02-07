#!/usr/bin/env python

'''
class to talk to SCPI-compliant RF sources. Tested on Agilent E4400B
'''

try:
    from . import Tool
except:
    import Tool

param = {'': ''}

INTERFACE = Tool.INTF_GPIB

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'RF_source', debug=debug,
                                         interface = INTERFACE, **kwargs)
        if not self.DEBUG:
            self.POW_MIN = self.inst.ask(':SOUR:POW? MIN')
            self.POW_MAX = self.inst.ask(':SOUR:POW? MAX')

    def set_freq(self, freq):
        if not self.DEBUG:
            self.write(':SOUR:FREQ:CW ' + str(freq))

    def set_power(self, power):
        if not self.DEBUG:
            self.write(':POW:LEV:IMM:AMPL ' + str(power))
