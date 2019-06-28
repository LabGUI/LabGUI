#!/usr/bin/env python
try:
    from . import Tool
except:
    import Tool

import time
import random
import numpy as np

param = {'Field': 'T'}

INTERFACE = Tool.INTF_GPIB


class Instrument(Tool.MeasInstr):
    def __init__(self, resource_name, debug=False, read_only=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'IPS120', debug=debug,
                                         interface=INTERFACE,
                                         read_termination='\r',
                                         write_termination='\r', **kwargs)
        if not self.DEBUG:
            self.read_only = read_only

            if self.read_only == False:
                self.set_extended()
                print((self.read_status()))
            self.clear()

    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'Field':
                    answer = self.read_field()
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        return answer

    def clear_buffer(self):
        if not self.DEBUG:
            self.clear()

    def unlock(self):
        if not self.DEBUG:
            return self.ask('@0C3')

    def set_field_sweep_rate(self, rate):
        if not self.DEBUG:
            if rate <= 0.20 and rate > 0:
                return self.ask('@0T%.4f' % rate)
            else:
                return "set rate too fast"

    def set_point_field(self, val):
        if not self.DEBUG:
            if val >= -9 and val <= 9:
                return self.ask('@0J%.4f' % val)

    def hold(self):
        if not self.DEBUG:
            return self.ask('@0A0')

    def goto_set(self):
        if not self.DEBUG:
            return self.ask('@0A1')

    def goto_zero(self):
        if not self.DEBUG:
            return self.ask('@0A2')

    def read_param(self, param):
        if not self.DEBUG:
            return self.ask('@0R' + str(param))

    def read_field(self):
        if not self.DEBUG:
            return float(self.ask('@0R7').lstrip('R'))
        else:
            return 0

    def read_status(self):
        if not self.DEBUG:
            return self.ask('@0X')

    def set_extended(self):
        if not self.DEBUG:
            return self.write('@0Q4')

    # waits until a setpoint is reached. Can't be interrupted.
    def ramp_to_setpoint(self, field):
        self.set_point_field(field)
        self.goto_set()

        still_ramping = True
        print ("Ramping field...")
        while still_ramping:
            actual_field = self.read_field()
            # floating point numbers may be close enough but not "pre
            still_ramping = abs(actual_field - field) > 0.00001
            time.sleep(1)


# if run as own program
if (__name__ == '__main__'):
    i = Instrument("GPIB0::25")
    print(i.identify())
    i.unlock()
