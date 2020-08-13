"""
temporary driver for vna


VNA Plots:

Plot 1: S11
Plot 2: S12
Plot 3: S21
Plot 4: S22
"""

try:
    from . import Tool
except:
    import Tool

import matplotlib.pyplot as plt
import numpy as np
param = {
    'Channel' : 'Unit',
    'Focused Freq':'Hz',
    'S12 Real':'',
    'S12 Imaginary':'',
    'S21 Real':'',
    'S21 Imaginary':'',

}

INTERFACE = Tool.INTF_GPIB
NAME = 'vna'

properties = {

    'Focused Freq': {
        'type':'float',
        'range':[2e7, 2e10], # float range for QIntValidator
        'unit':'Hz' # optional unit
    }
}

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
        self.focused_freq = 2e9 #Hz
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
                    answer = self.ask("*IDN?")
                    answer = 0
                if channel == 'Focused Freq':
                    answer = self.focused_freq
                if channel == 'S12 Real':
                    answer = self.ReadGraphValue(2, self.focused_freq).real
                if channel == 'S12 Imaginary':
                    answer = self.ReadGraphValue(2, self.focused_freq).imag
                if channel == 'S21 Real':
                    answer = self.ReadGraphValue(3, self.focused_freq).real
                if channel =='S21 Imaginary':
                    answer = self.ReadGraphValue(3, self.focused_freq).imag
            else:
                answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        #answer = 1 + 2J
        self.last_measure[channel] = answer
        return answer

    def get(self):
        return {'Focused Freq':self.focused_freq}

    def set(self, data):

        if not self.DEBUG:
            for channel, value in data.items():
                if channel == 'Focused Freq':
                    self.focused_freq = float(value)
                else:
                    print("If you reached here, something went wrong: ", channel)
        else:
            print("Debug mode enabled", data)
    def ReadGraphValue(self, channel, frequency):
        self.write("DISP:FORM QQSP")  # show all 4 graphs

        xcoord = np.array([float(i) for i in self.ask("TRAC:STIM? CH%sDATA" % str(channel)).split(",")])
        ycoord = np.array([float(i) for i in self.ask("TRAC? CH%sDATA" % str(channel)).split(",")])

        data = ycoord[::2] + 1J * ycoord[1::2]

        if frequency < xcoord.min() or frequency > xcoord.max():
            print("Frequency out of range")
            return float('nan')

        idx = (np.abs(xcoord - frequency)).argmin()

        return data[idx]



    def data(self, channel=4):
        self.write("DISP:FORM QQSP") # show all 4 graphs

        xcoord = np.array([float(i) for i in self.ask("TRAC:STIM? CH%sDATA"%str(channel)).split(",")])
        ycoord = np.array([float(i) for i in self.ask("TRAC? CH%sDATA"%str(channel)).split(",")])

        data = ycoord[::2] + 1J*ycoord[1::2]
        Re = ycoord[::2]
        Im = ycoord[1::2]
        Mag = np.abs(data)
        Phase = np.angle(data)
        print(Phase)

        plt.plot(xcoord,data.real,label="Real Component")
        plt.plot(xcoord,data.imag,label="Imaginary Component")
        plt.xlabel("Freq (Hz)")
        plt.ylabel("Amplitude (units?)")
        plt.legend()
        plt.show()

        plt.scatter(data.real,data.imag)
        plt.xlabel("Real Component")
        plt.ylabel("Imaginary Component")
        plt.show()

        plt.scatter(Phase, Mag)
        plt.show()

        Complex = Re + 1J*Im

        #print(Complex)
        print(len(xcoord),len(ycoord))

if __name__ == "__main__":
    i = Instrument("GPIB::1", debug=False)













