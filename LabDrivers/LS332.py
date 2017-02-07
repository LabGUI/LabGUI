# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:28:29 2012
Lakeshore 332 Driver
@author: Bram
Modified by: Kevin Mortimer (Oct 7 2014)
"""

import random
from . import Tool

param = {'A': 'K', 'B': 'K'}

INTERFACE = Tool.INTF_GPIB

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'LS332', debug=debug, 
                                         interface = INTERFACE, **kwargs)


    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'A':
                    answer = float(self.ask('KRDG?' + channel))  # read in K
                if channel == 'B':
                    answer = float(self.ask('KRDG?' + channel))  # read in K

            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def setTemp(self, temp, loop):  # float value of resistance in Ohm, loop 1 or 2
        if not self.DEBUG:
            if loop == 1 or loop == 2:
                print("that's good", 'SETP ' + str(loop) + ',' + "%.2f" % (temp))
                self.write('SETP ' + str(loop) + ',' + "%.2f" % (temp))
                # Controller can only take 6 numeric inputs (plus a sign)
            else:
                print('invalid loop for the Lakeshore')
        else:
            print(('SETP ' + str(loop) + ', ' + "%.2f" % (temp)))

    def get_PID(self):
        return self.ask('PID?')

    def set_PID(self, value_loop, value_P, value_I, value_D):
        if not self.DEBUG:
            sep = ','
            if (value_loop != 1 and value_loop != 2) or value_P < 0.1 or value_P > 1000 or value_I < 0.1 or value_I > 1000 or value_D < 0 or value_D > 200:
                print("PID settings invalid")
            else:
                self.write('PID ' + format(value_loop, '.1g') + sep + format(value_P,
                                                                             '+.5g') + sep + format(value_I, '+.5g') + sep + format(value_D, '+.5g'))
        else:
            print(('PID ' + format(value_loop, '.1g') + sep + format(value_P, '+.5g') +
                  sep + format(value_I, '+.5g') + sep + format(value_D, '+.5g')))

    def set_heater_range(self, value_range):
        if not self.DEBUG:
            if value_range < 4 and value_range >= 0:
                return self.ask('RANGE ' + format(value_range, '.1g') + ';RANGE?')
            else:
                print('invalid loop for the Lakeshore')
        else:
            print(('RANGE ' + format(value_range, '.1g') + ';RANGE?'))

    def set_ramp_rate(self, value_loop, value_ramp_status, value_ramp_rate):
        sep = ','
        if not self.DEBUG:
            if (value_loop == 1 or value_loop == 2) and (value_ramp_status == 0 or value_ramp_status == 1) and (value_ramp_rate > 0.1 and value_ramp_rate < 100):
                self.write('RAMP ' + format(value_loop, '.1g') + sep + format(
                    value_ramp_status, '.1g') + sep + format(value_ramp_rate, '.4g'))
            else:
                print('invalid ramp setting')
        else:
            print(('RAMP ' + format(value_loop, '.1g') +
                  sep + format(value_ramp_status, '.1g')))

if __name__ == "__main__":
    i = Instrument("GPIB0::15", False)
    print(i.identify())
    i.close()