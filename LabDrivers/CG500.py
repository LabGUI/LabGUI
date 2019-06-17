# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:28:29 2012
Cryogenic 500 Level Meter Driver
@author: PF

"""
#import visa
import random
try:
    from . import Tool
except:
    import Tool

param = {'HeLevel': 'cm', 'HeLevel2': 'cm'}

INTERFACE = Tool.INTF_GPIB


class Instrument(Tool.MeasInstr):

    # a tag that will be initiallized with the same name than the module
    # const_label=''

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'CG500',
                                         debug=debug, interface=INTERFACE, **kwargs)

#------------------------------------------------------------------------------

    # I don't know if the values measured stack or not, if they do we should
    # probably think about this function again
    def measure(self, channel='HeLevel'):
        if channel in self.last_measure:
            if not self.DEBUG:
                chan = self.get_channel()
                if channel == 'HeLevel2':
                    answer = self.ask('MEAS? ' + chan)
                else:
                    answer = self.ask('MEAS ' + chan + ';MEAS? ' + chan)
                answer = float(answer[:-3])
            else:
                answer = 100 * random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def get_status(self):
        return self.ask('STAT?')

    def get_type(self):
        chan_type = self.ask('TYPE? ' + self.get_channel())
        if chan_type:
            print("The channel type is Liquid Nitrogen")
        else:
            print("The channel type is Liquid Helium")
        return chan_type

    def get_channel(self):
        return self.ask('CHAN?')

    def set_channel(self, value_chan):
        return self.connexion.write('CHAN ' + str(value_chan) + ';CHAN?')

    def get_sampling_interval(self):
        return self.ask('INTVL?')

    # format 'HH:MM:SS', if 0 is inputed then it measures continously
    def set_sampling_interval(self, value_intvl):
        return self.write('INTVL ' + str(value_intvl) + ';INTVL?')

    #'S' for sample/hold and 'C' for continuous
    def get_mode(self):
        return self.ask('mode?')

    #'S' for sample/hold and 'C' for continuous
    def set_mode(self, value_mode):
        return self.write('MODE ' + str(value_mode) + ';MODE?')

    def set_error_mode(self, value_err_mode):
        return self.write('ERROR ' + str(value_err_mode) + ';ERROR?')

    #'CM', 'IN', '%'
    def set_units(self, value_units):
        return self.write('UNITS ' + str(value_units) + ';UNITS?')

    # 0 will desactivate the alarm, a low value will not annoy people in the
    # lab
    def set_alarm(self, value_alarm):
        return self.write('ALARM ' + str(value_alarm) + ';ALARM?')


if (__name__ == '__main__'):

    myInst = Instrument("GPIB0::7", interface='prologix')
    print(myInst.identify())
