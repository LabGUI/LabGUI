# -*- coding: utf-8 -*-
"""
Created on Wed Jun 5 2019
Driver Template, without documentation for easy copy/paste
@author: zackorenberg

Note, all drivers must be placed in LabDrivers/ to work
"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool


param = {
    'Channel': 'Unit'
}

INTERFACE = Tool.INTF_GPIB
NAME = 'name'
""" Options:
INTF_GPIB
INTF_VISA
INTF_SERIAL
INTF_PROLOGIX
INTF_NONE
"""


class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name, debug=False, **kwargs):
        # DYNAMIC INTERFACING/NAME
        # if "interface" in kwargs:
        #     itfc = kwargs.pop("interface")
        # else:
        #     itfc = INTERFACE
        #
        # name='insert device name here, typically the same name as the file'
        # if "name" in kwargs:
        #     name = kwargs.pop("name")
        #     print(name)
        # super(Instrument, self).__init__(resource_name,
        #                                  name=name,
        #                                  debug=debug,
        #                                  interface = itfc,
        #                                  read_termination = '\r', # this is left here to show that it is possible to change read_termination value
        #                                  **kwargs)
        #
        super(Instrument, self).__init__(resource_name,
                                         name=NAME,
                                         debug=debug,
                                         interface=INTERFACE,
                                         **kwargs)

    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'Channel':
                    answer = 'value'
            else:
                answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        self.last_measure[channel] = answer
        return answer


if __name__ == "__main__":
    i = Instrument("GPIB::1", debug=False)
