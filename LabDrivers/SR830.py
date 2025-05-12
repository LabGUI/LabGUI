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

Sensitivity = {
    0: (2, 'nV', 'fA'),
    1: (5, 'nV', 'fA'),
    2: (10, 'nV', 'fA'),
    3: (20, 'nV', 'fA'),
    4: (50, 'nV', 'fA'),
    5: (100, 'nV', 'fA'),
    6: (200, 'nV', 'fA'),
    7: (500, 'nV', 'fA'),
    8: (1, 'uV', 'pA'),
    9: (2, 'uV', 'pA'),
    10: (5, 'uV', 'pA'),
    11: (10, 'uV', 'pA'),
    12: (20, 'uV', 'pA'),
    13: (50, 'uV', 'pA'),
    14: (100, 'uV', 'pA'),
    15: (200, 'uV', 'pA'),
    16: (500, 'uV', 'pA'),
    17: (1, 'mV', 'nA'),
    18: (2, 'mV', 'nA'),
    19: (5, 'mV', 'nA'),
    20: (10, 'mV', 'nA'),
    21: (20, 'mV', 'nA'),
    22: (50, 'mV', 'nA'),
    23: (100, 'mV', 'nA'),
    24: (200, 'mV', 'nA'),
    25: (500, 'mV', 'nA'),
    26: (1, 'V', 'uA'),
}
UnitsMultiplier = {
    'nV': 1e-9,
    'uV': 1e-6,
    'mV': 1e-3,
    'V': 1,
    'fA':1e-15,
    'pA':1e-12,
    'nA':1e-9,
    'uA':1e-6,
}

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
    
    def auto_sensitivity(self):
        """
        Performs the "Auto Gain" function of the lockin. Will wait for execution to finish before returning
        """
        if not self.DEBUG:
            try:
                self.write("AGAN") # Instruct lockin to perform autogain
                while int(self.ask('*STB? 1')): # Check status bit, waiting for it to read 0 when no command is executing
                    print("Auto Gain Running")
                    time.sleep(0.05)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return True
    
    def get_sensitivity(self, voltage_mode = True):
        """
        Determines the current sensitivity
        """
        if not self.DEBUG:
            try:
                sensitivity_mode = self.ask('SENS?')
                coef, unitV, unitA = Sensitivity[int(sensitivity_mode)]
                if voltage_mode:
                    return coef * UnitsMultiplier[unitV] # We are always in voltage mode
                else:
                    return coef * UnitsMultiplier[unitA] # Incase for whatever reason we are in current mode. TODO: Determine this automatically through commands?
            except Exception as e:
                print(e)
                return nan
        else:
            return 1.23e-4
    
    def increase_sensitivity(self):
        """
        Increases the sensitivity. This function is equivalent to pressing the up arrow on the lockin.
        
        Additionally, a check is performed to determine whether or not the sensitivity was actually raised.
        """
        if not self.DEBUG:
            try:
                current_sensitivity = int(self.ask('SENS?'))
                if current_sensitivity < max(Sensitivity.keys()):
                    self.write(f'SENS {current_sensitivity+1}')
                    return int(self.ask('SENS?')) == (current_sensitivity+1)
                else:
                    return False
            except Exception as e:
                print(e)
                return nan
        else:
            return True
            
    def decrease_sensitivity(self):
        """
        Decreases the sensitivity. This function is equivalent to pressing the down arrow on the lockin.
        
        Additionally, a check is performed to determine whether or not the sensitivity was actually lowered.
        """
        if not self.DEBUG:
            try:
                current_sensitivity = int(self.ask('SENS?'))
                if current_sensitivity > 0:
                    self.write(f'SENS {current_sensitivity-1}')
                    return int(self.ask('SENS?')) == (current_sensitivity-1)
                else:
                    return False
            except Exception as e:
                print(e)
                return nan
        else:
            return True
    
    def determine_signal_sensitivity_percentage(self):
        """
        Determines where the current signal lies within the current range.
        
        This function effectively returns the position at which the range indicator under the lockin screen is, for both x and y
        
        This function returns a tuple (Xpercentage, Ypercentage), including the sign of the signal. If the voltage is negative, the return percentage will also be negative.
        """
        if not self.DEBUG:
            try:
                sensitivity = self.get_sensitivity()
                X = float(self.ask('OUTP? 1'))
                Y = float(self.ask('OUTP? 2'))
                return X / sensitivity, Y / sensitivity
            except Exception as e:
                print(e)
                return nan, nan
        else:
            return 1.23e-4, 1.23e-4

if (__name__ == '__main__'):

    from utils import command_line_test

    command_line_test(Instrument)
    print(i.identify())
