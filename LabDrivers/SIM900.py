# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 15:39:39 2016

@author: pfduc

Repeated executions of the script will fail (communications do not stop?)
Change COM to different #, run, then change again and can try again...
Within execution, no problem using different commands.

Could be updated with compliance if coupled with DMMs used as amperemeters...

"""

import numpy as np
import time
import random

from struct import pack, unpack
import pylab as plt

try:
    from . import Tool
except:
    import Tool


param = {'CH1': 'V', 'CH2': 'V', 'phase': 'deg', 'Z': 'Ohm', 'Z2': 'Ohm'}

INTERFACE = Tool.INTF_SERIAL

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'SIM900', debug, interface=INTERFACE, baud_rate=9600,
                                         term_chars="\n", timeout=2, bytesize=8, parity='N', stopbits=1, xonxoff=False, dsrdtr=False, **kwargs)

    def ask_channel(self,chan_num,msg):
#        print 'SEND %i,"%s"'%(chan_num,msg)
        self.write('CONN %i,"xyz"'%chan_num)
        answer=self.ask('%s'%(msg))
        i.write("xyz")
        return answer
#        return i.ask('SNDT %i,"%s"'%(chan_num,msg))
        
    def get_voltage(self,chan_num):
        return self.ask_channel(chan_num,"VOLT?")
        
    def set_voltage(self, chan_num, voltage):
        if not self.debug:
            i.write('CONN %i,"xyz"'%chan_num)
            i.write("VOLT %f"% voltage)
            i.write("xyz")
        else:
            print("voltage set to " + str(voltage) + " on channel " + chan_num)
            
    def enable_output(self,chan_num):
        if not self.debug:
            i.write('CONN %i,"xyz"'%chan_num)
            i.write("OPON")
            i.write("xyz")

    def disable_output(self,chan_num):
        if not self.debug:
            i.write('CONN %i,"xyz"'%chan_num)
            i.write("OPOF")
            i.write("xyz")
            
    def move_voltage(self, p_reader, chan_num, p_target_voltage, step=0.002, wait=0.001):
#    def move_voltage(self, p_reader, p_target_voltage, step=0.001, wait=0.005):
#        print 'Moving voltage'        
        current_voltage = float(self.get_voltage(chan_num))
        # Parse move direction cases
        if current_voltage < p_target_voltage:  # If keithley needs to move up
            # While the current_voltage is not within one increment of the target voltage
            while current_voltage < p_target_voltage:
                # Stop if it needs to
                if p_reader.isStopped():
                    print("Stopping")
                    return 0
                # Increment the current voltage by a safe amount
                current_voltage += step
                self.set_voltage(chan_num, current_voltage)
                # Wait
                time.sleep(wait)
        elif current_voltage > p_target_voltage:  # If keithley needs to move up
            # While the current_voltage is not within one increment of the
            # target voltage
            while current_voltage > p_target_voltage:
                # Stop if it needs to
                if p_reader.isStopped():
                    print("Stopping")
                    return 0
                # Increment the current voltage by a safe amount
                current_voltage -= step
                self.set_voltage(chan_num, current_voltage)
                # Wait
                time.sleep(wait)
        # Correct for offset
        self.set_voltage(chan_num, p_target_voltage)
#        time.sleep(1)
        # return success
        print("Done moving")
        return 1
        
if __name__ == "__main__":
    
    i=Instrument("COM7")
    
#    i.write('SNDT 4,"GAIN"')
    print(i.ask("*IDN?"))
    i.enable_output(4)
#    i.set_voltage(5,5)
#    i.set_voltage(4,4)
#    print(i.get_voltage(5))
#    print(i.get_voltage(4))
#    i.move_voltage(5,0)
#    i.move_voltage(4,0)
#    print(i.get_voltage(5))
#    print(i.get_voltage(4))
