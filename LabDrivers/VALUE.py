# -*- coding: utf-8 -*-
"""
@author: zackorenberg

Adds some fixed value settable by the script.
"""

import LabDrivers.Tool as Tool

param = {'Value': ''}

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):
    def __init__(self, resource_name=None, debug=False, default_value=float('nan'), **kwargs):
        super(Instrument, self).__init__(resource_name, name='VALUE',
                                         debug=debug, interface=INTERFACE,
                                         **kwargs)
        self.default_value = default_value
        self.value = self.default_value
    # ------------------------------------------------------------------------------

    def initialize(self):
        self.value = self.default_value


    def set_value(self, value):
        self.value = value


    def measure(self, channel='Value'):
        # we dont care about the channel, always return iterator
        return self.value


if __name__ == "__main__":
    value = Instrument()
    print(value.measure())
    value.set_value(123.4)
    print(value.measure())
