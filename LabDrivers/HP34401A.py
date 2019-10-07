#!/usr/bin/env python
try:
    from . import Tool
except:
    import Tool

import random


param = {'V_DC': 'V', 'V_AC': 'V', 'I_DC': 'A',
         'I_AC': 'A', 'R': 'Ohm', 'READ': '?'}

INTERFACE = Tool.INTF_GPIB

REMOTE_LOCK = False


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'HP34401A', debug=debug,
                                         interface=INTERFACE, **kwargs)


    def identify(self, msg=''):
        if not self.DEBUG:
            # the *IDN? is probably not working
            return msg  # command for identifying
        else:
            return msg + self.ID_name

    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                self.connection.control_ren(1)  # Assert remote lock before to avoid error
                if channel == 'V_DC':
                    #print(self.ask(":SYST:LOC?"))
                    answer = self.read_voltage_DC()
                elif channel == 'V_AC':
                    answer = self.read_voltage_AC()
                elif channel == 'I_DC':
                    answer = self.read_current_DC()
                elif channel == 'I_AC':
                    answer = self.read_current_AC()
                elif channel == 'R':
                    answer = self.read_resistance()
                elif channel == 'READ':
                    answer = self.read_any()
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        # to prevent remote lockout
        if not REMOTE_LOCK:
            self.connection.control_ren(0) #deassert remote lock
        return answer

    def read_any(self):
        if not self.DEBUG:
            string_data = self.ask('READ?')
            return float(string_data)
        else:
            return 123.4

    def read_voltage_DC(self):
        if not self.DEBUG:
            string_data = self.ask(':MEAS:VOLT:DC?')
            #print(string_data) # prevents output from writing twice
            return float(string_data)
        else:
            return 123.4

    def read_voltage_AC(self):
        if not self.DEBUG:
            string_data = self.ask(':MEAS:VOLT:AC?')
            return float(string_data)
        else:
            return 123.4


    def read_current_DC(self):
        if not self.DEBUG:
            string_data = self.ask(':MEAS:CURR:DC?')
            return float(string_data)
        else:
            return 123.4

    def read_current_AC(self):
        if not self.DEBUG:
            string_data = self.ask(':MEAS:CURR:AC?')
            return float(string_data)
        else:
            return 123.4

    def read_resistance(self):
        if not self.DEBUG:
            string_data = self.ask(':MEAS:RES?')
            return float(string_data)
        else:
            return 123.4

# if run as own program
if (__name__ == '__main__'):
    i = Instrument('GPIB0::19')
    # print(i.identify())
    print(i.measure('V'))
    i.close()

    #   lockin = device('dev9')
     #   lockin.set_ref_internal  # no averaging
     #   lockin.close()
