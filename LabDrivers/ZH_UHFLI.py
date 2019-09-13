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
import numpy as np
import time
import sys


ZHINST = True
try:
    import zhinst.ziPython
    import zhinst.utils
except:
    ZHINST = False
    print("zhinst is NOT installed! Install it by running 'pip install zhinst'")
    print(sys.exc_info())

# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool


HOSTNAME = 'localhost'
PORT = 8004  # default for this device
API_LEVEL = 5  # version of the API to use
DEVICE_ID = 2279  # differs from device to device, you must obtain this from LabONE, it is the serial number

param = {  # sample of data that it can read
    'X0': 'V',
    'Y0': 'V',
    #    'R0' : 'V', DOES NOT APPEAR TO BE OBTAINABLE THROUGH SAMPLE
    'Aux0in0': 'V',
    'Aux1in0': 'V',
    'Phase0': 'Rad',
    'Frequency0': 'Hz',
}
for i in range(0, 8):  # creates values for all modulators
    param['X' + str(i)] = 'V'
    param['Y' + str(i)] = 'V'
#    param['R' + str(i)] = 'V'
    param['Aux0in' + str(i)] = 'V'
    param['Aux1in' + str(i)] = 'V'
    param['Phase' + str(i)] = 'Rad'
    param['Frequency' + str(i)] = 'Hz'

INTERFACE = Tool.INTF_NONE  # will be custom
NAME = 'ZH_UHFLI'


class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name=None, debug=False, **kwargs):

        super(Instrument, self).__init__(resource_name,
                                         name=NAME,
                                         debug=debug,
                                         interface=INTERFACE,
                                         **kwargs)
        self.INFO = True
        # name device
        self.dev = 'dev' + str(DEVICE_ID)
        # make sure all required parameters are set, and make all first measured values equal zero
        for chan, u in list(param.items()):
            self.channels.append(chan)
            self.units[chan] = u
            self.last_measure[chan] = 0
            self.channels_names[chan] = chan

        # connect to LabONE
        if not self.DEBUG:
            try:
                self.daq = zhinst.ziPython.ziDAQServer(HOSTNAME, PORT)
            except:
                self.daq = None
                print("=== Make sure LabONE is started, and attempt to reconnect ===")
                if self.INFO:
                    print(sys.exc_info())

    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in param:
            if 'X' in channel:
                # get number
                number = channel[1:]
                sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
                answer = sample['x'][0]
            elif 'Y' in channel:
                # get number
                number = channel[1:]
                sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
                answer = sample['y'][0]
            # elif 'R' in channel:
            #     #get number
            #     number = channel[1:]
            #     sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
            elif 'Aux0in' in channel:
                number = channel[6:]
                sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
                answer = sample['auxin0'][0]
            elif 'Aux1in' in channel:
                number = channel[6:]
                sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
                answer = sample['auxin1'][0]
            elif 'Phase' in channel:
                # get number
                number = channel[5:]
                sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
                answer = sample['phase'][0]
            elif 'Frequency' in channel:
                # get number
                number = channel[9:]
                sample = self.get_sample('/' + self.dev + '/demods/' + number + '/sample')
                answer = sample['frequency'][0]

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        self.last_measure[channel] = answer
        return answer

    def get_sample(self, stri):
        if not self.DEBUG:
            try:
                return self.daq.getSample(stri)
            except:
                time.sleep(0.1)
                print("Zurich has died for a moment!")
                try:
                    return self.daq.getSample(stri)
                except:
                    print("There is currently no data reading on this channel", sys.exc_info()[0])
                    if self.INFO:
                        print(sys.exc_info())
                    return 0
        else:
            return np.random.random()


if __name__ == "__main__":
    i = Instrument()
