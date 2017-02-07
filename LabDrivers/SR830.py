#!/usr/bin/env python
#import visa
try:
    from . import Tool
except:
    import Tool
from collections import OrderedDict
from numpy import nan

# use an ordered dictionary so that the parameters show up in a pretty order :)
param = OrderedDict([('X', 'V'), ('Y', 'V'), ('R', 'V'), ('PHASE', 'degrees'),
                     ('AIN_1', 'V'), ('AIN_2', 'V'), ('AIN_3', 'V'), ('AIN_4', 'V'), ('AOUT_1', 'V'), ('AOUT_2', 'V'), ('AOUT_3', 'V'), ('AOUT_4', 'V'), ('FREQ', 'Hz')])

INTERFACE = Tool.INTF_GPIB


import logging

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'SR830', debug=debug, interface=INTERFACE, **kwargs)

    def measure(self, channel):
        if channel in param:
            if channel == 'X':
                answer = self.read_input(1)
            elif channel == 'Y':
                answer = self.read_input(2)
            elif channel == 'R':
                answer = self.read_input(3)
            elif channel == 'PHASE':
                answer = self.read_input(4)
            elif channel == 'AIN_1':
                answer = self.read_aux_in(1)
            elif channel == 'AIN_2':
                answer = self.read_aux_in(2)
            elif channel == 'AIN_3':
                answer = self.read_aux_in(3)
            elif channel == 'AIN_4':
                answer = self.read_aux_in(4)
            elif channel == 'AOUT_1':
                answer = self.read_aux_out(1)
            elif channel == 'AOUT_2':
                answer = self.read_aux_out(2)
            elif channel == 'AOUT_3':
                answer = self.read_aux_out(3)
            elif channel == 'AOUT_4':
                answer = self.read_aux_out(4)
            elif channel == 'FREQ':
                answer = self.get_freq()
            elif channel == 'AMPL':
                answer = self.get_amplitude()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def set_scale(self, scale):
        self.write('SENS ' + str(scale))

    def set_ref_internal(self):
        self.write('FMOD 1')

    def set_ref_external(self):
        self.write('FMOD 0')

    def set_phase(self, shift):
        self.write('PHAS ' + str(shift))

    def set_amplitude(self, amplitude):
        self.write('SLVL' + str(amplitude))

    def get_amplitude(self):
        if not self.DEBUG:
            return self.ask('SLVL?')
        else:
            return 1.0

    def set_freq(self, freq):
        self.write('FREQ ' + str(freq))

    def get_freq(self):
        if not self.DEBUG:
            return float(self.ask('FREQ?'))

    def set_harm(self, harm):
        self.write('HARM ' + str(harm))

    def set_ref_out(self, voltage):
        self.write('SLVL ' + str(voltage))

    def get_ref_out(self, voltage):
        if not self.DEBUG:
            self.write('SLVL?')
            return self.read()
        else:
            return 1.234

    def read_aux_in(self, chan):
        '''
        Reads the AuxIn voltage value of the lock-in. The channel values can be 1, 2 ,3 or 4. 
        '''
        if not self.debug:
            self.write('OAUX? ' + str(chan))
            return float(self.read())
        else:
            return 1.234
            
    def read_aux_out(self, chan):
        '''
        Reads the AuxOut voltage value of the lock-in. The channel values can be 1, 2 ,3 or 4. 
        '''
        if not self.debug:
            self.write('AUXV? ' + str(chan))
            return float(self.read())
        else:
            return 1.234

    def set_aux_out(self, chan, volts):
        '''
        Sets the AuxOut voltage value for the lock-in. The channel values can be 1, 2 ,3 or 4. 
        '''
        self.write('AUXV ' + str(chan) + ", " + str(volts))


    def read_input(self, num):
        '''
        Reads the specificed input of the lockin. 1=x, 2=y, 3=r, 4=phase
        '''
        if not self.DEBUG:
            try:
                return float(self.ask('OUTP? ' + str(num)))
            except ValueError:
                logging.error("The value returned by the lockin GPIB::%s was \
                not a number, when this happened it was a problem from the \
                lockin, try changing GPIB address."%(self.resource_name))
                return nan
        else:
            return 1.23e-4

# if run as own program
if (__name__ == '__main__'):

    lockin1 = Instrument("GPIB0::11")
    print lockin1.identify()
    print lockin1.measure('X')  # no averaging
    lockin1.close()
