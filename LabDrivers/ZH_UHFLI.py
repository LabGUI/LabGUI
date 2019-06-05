# -*- coding: utf-8 -*-
"""
Created on Wed Jun 5 2019
Driver for USB only device ZH_UHFLI (Zurich Instruments, UHF Lock-in Amplifier)
@author: zackorenberg


NOTE this instrument has its own USB interface system, as well as software and API

To use this instrument, you MUST have the following installed:

LabONE, downloadable from this website:

    https://www.zhinst.com/downloads

    You must select UHFLI and download the latest version of LabONE

zhinst, the Python API for LabONE

    installable by the following command:

    pip install zhinst

"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool




param = {
    'type1' : 'V'
}

INTERFACE = Tool.INTF_NONE # will be custom
NAME = 'ZH_UHFLI'

class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name, debug=False, **kwargs):

        super(Instrument, self).__init__(resource_name,
                                          name=NAME,
                                          debug=debug,
                                          interface=INTERFACE,
                                          backwardcompatible=False,
                                          **kwargs)

    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in self.last_measure:
            if channel == 'Channel':
                answer = 'value'

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        self.last_measure[channel] = answer
        return answer


if __name__ == "__main__":
    i = Instrument("GPIB::1", debug=False)








