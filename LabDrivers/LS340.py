# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:28:29 2012
Lakeshore 340 Driver
@author: Bram
issues:
   - need to hardcode limits of valid setPoint() resistance input
"""
#import visa
import random
#import alarm_toolbox as alarm
try:
    from . import Tool
except:
    import Tool
import converter_RuOx_U02627 as convT
#import numpy as np

param = {'A': 'K', 'B': 'K', 'C': 'kOhm', 'D': 'kOhm',
         'C(T)': 'kOhm_to_K', 'D(T)': 'kOhm_to_K'}

INTERFACE = Tool.INTF_GPIB

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False,**kwargs):
        super(Instrument, self).__init__(resource_name, 'LS340', debug=debug, interface = INTERFACE,**kwargs)
        chan_names = ['Charcoal', '1Kpot', 'He3Pot', 'Cell']
        for chan, chan_name in zip(self.channels, chan_names):
            self.last_measure[chan] = 0
            self.channels_names[chan] = chan_name

    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                answer = 0
                if param[channel] == 'K':
                    # read in Kelvin thrithy
                    try:
                        answer = float(self.ask('KRDG?' + channel))
                    except ValueError:
                        answer = self.last_measure[channel]
                elif param[channel] == 'kOhm':
                    try:
                        answer = float(self.ask('SRDG?' + channel))  # read in kOhm
                    except ValueError:
                        answer = self.last_measure[channel]
                elif param[channel] == 'kOhm_to_K':
                    try:
                        answer = round(convT.R_to_T(
                        float(self.ask('SRDG?' + channel))), 4)
                    except ValueError:
                        answer = self.last_measure[channel]
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        return answer

    def setPoint(self, resistance, loop):  # float value of resistance in Ohm, loop 1 or 2
        if not self.DEBUG:
            if resistance > 1050:
                self.connexion.write(
                    'SETP ' + str(loop) + ', ' + "%.3f" % (resistance))
            else:
                print('invalid setpoint for the Lakeshore')

    def setTemp(self, resistance, loop):  # float value of resistance in Ohm, loop 1 or 2
        if not self.DEBUG:
            if resistance < 40:
                self.connexion.write(
                    'SETP ' + str(loop) + ', ' + "%.3f" % (resistance))
            else:
                print('invalid setpoint for the Lakeshore')

    # set an alarm that will actually ring from the instrument, this is to be
    # desactivated when the experimentalist is not him self in the lab for the
    # sake of others
    def set_alarm(self, value_channel, on_off, value_source, value_high, value_low, beep_on_off):
        sep = ', '
        self.write('ALARM ' + value_channel + sep + str(on_off) + sep + str(value_source) +
                   sep + str(value_high) + sep + str(value_low) + ';BEEP ' + str(beep_on_off))

    # this shouldbe changed into self.ask once this function will be changed
    def get_alarm_status(self):
        return self.ask('ALARMST?')

    # MM,DD,YYY,HH,mm,SS,sss
    def get_datetime(self):
        return self.ask('DATETIME?')

    def get_PID(self):
        return self.ask('PID?')

    def set_PID(self, value_loop, value_P, value_I, value_D):
        sep = ', '
        self.write('PID ' + value_loop + sep + str(value_P) +
                   sep + str(value_I) + sep + str(value_D))

    def set_heater_range(self, value_range):
        return self.ask('RANGE ' + str(value_range) + ';RANGE?')

if (__name__ == '__main__'):

    myInst = Instrument("GPIB0::12")
    print(myInst.identify())


