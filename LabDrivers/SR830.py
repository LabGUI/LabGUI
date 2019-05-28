#!/usr/bin/env python
#import visa

from collections import OrderedDict
from numpy import nan

try:
    from . import Tool
except:
    import Tool


# use an ordered dictionary so that the parameters show up in a pretty order :)
param = OrderedDict([('X', 'V'), ('Y', 'V'), ('R', 'V'), ('PHASE', 'degrees'),
                     ('AIN_1', 'V'), ('AIN_2', 'V'), ('AIN_3', 'V'), ('AIN_4', 'V'), ('AOUT_1', 'V'), ('AOUT_2', 'V'), ('AOUT_3', 'V'), ('AOUT_4', 'V'), ('FREQ', 'Hz')])

INTERFACE = Tool.INTF_GPIB


import logging


class Instrument(Tool.MeasInstr):
    """ Class to communicate with Stanford Research Systems SR830 lock-in"""

    def __init__(self, resource_name, debug=False, **kwargs):

        # manage the presence of the keyword interface which will determine
        # which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE

        super(Instrument, self).__init__(resource_name, 'SR830', debug=debug,
                                         interface=interface, **kwargs)

    def measure(self, channel):
        """ Measure the specified 'channel' and return the result. The list
        of available channels is given by the keys in param.

        Args:
            channel (string): the channel to measure. 
        """
        #Note, if ordered, param.keys().index(channel) gives read number
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
        """ Set the sensitivity of the input channel. Refer to SR830 
        documentation for the full list of settings

        Args:
            scale (int): Between 0 and 26, the sensitivity to use
        """
        self.write('SENS ' + str(scale))

    def set_ref_internal(self):
        """ Instruct the lock-in to lock to its internal oscillator"""
        self.write('FMOD 1')

    def set_ref_external(self):
        """ Instruct the lock-in to lock to the ref-in input """
        self.write('FMOD 0')

    def set_phase(self, shift):
        """ Set the phase offset.

        Args:
            shift (float): Phase shift in degrees
        """
        self.write('PHAS ' + str(shift))

    def set_amplitude(self, amplitude):
        """ set the reference output amplitude in volts

        Args:
            amplitude (float): RMS voltage output of the reference channel
        """
        self.write('SLVL' + str(amplitude))

    def get_amplitude(self):
        """ Query the current reference channel output amplitude """
        if not self.DEBUG:
            return self.ask('SLVL?')
        else:
            return nan

    def set_freq(self, freq):
        """ Set the frequency of the reference channel.

        Args: 
            freq (float): frequency in Hertz. 
        """
        self.write('FREQ ' + str(freq))

    def get_freq(self):
        """ Query the frequency of the reference channel."""
        if not self.DEBUG:
            return float(self.ask('FREQ?'))

    def set_harm(self, harm):
        """ Sets the harmonic number to measure. Use set_harm(1) to measure
        at the reference frequency itself.

        Args:
            harm (int): harmonic number to measure.
        """
        self.write('HARM ' + str(harm))

    def read_aux_in(self, chan):
        """ Reads the AuxIn voltage value of the lock-in. 

        Args: 
            chan (int): channel to read, one of 1, 2 ,3 or 4. 
        """
        if not self.debug:
            self.write('OAUX? ' + str(chan))
            return float(self.read())
        else:
            return 1.234

    def read_aux_out(self, chan):
        """ Reads the AuxOut voltage value of the lock-in. 

        Args: 
            chan (int): channel to read, one of 1, 2 ,3 or 4. 
        """
        if not self.debug:
            self.write('AUXV? ' + str(chan))
            return float(self.read())
        else:
            return 1.234

    def set_aux_out(self, chan, volts):
        """ Sets the AuxOut voltage value for the lock-in. 

        Args: 
            chan (int): channel to read, one of 1, 2 ,3 or 4. 
        """
        self.write('AUXV ' + str(chan) + ", " + str(volts))

    def read_input(self, num):
        """
        Reads the specificed input of the lockin. 

        Args:
            num (int): 1=x, 2=y, 3=r, 4=phase
        """
        if not self.DEBUG:
            try:
                return float(self.ask('OUTP? ' + str(num)))
            except ValueError:
                logging.error("The value returned by the lockin GPIB::%s was \
                not a number, when this happened it was a problem from the \
                lockin, try changing GPIB address." % (self.resource_name))
                return nan
        else:
            return 1.23e-4


if (__name__ == '__main__'):

    from utils import command_line_test

    command_line_test(Instrument)
    print(i.identify())
