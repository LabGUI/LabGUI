# -*- coding: utf-8 -*-
"""
Created on Fri Apr 06 17:12:05 2018

Driver for the MGC4000 by Kurt J. Lesker

Inspired from Plotly dash-control-component

@author: pierre-francois.duc@mail.mcgill.ca
"""

import random
import numpy as np
import logging

try:
    from . import Tool
except:
    import Tool

param = {'CG1': 'mbar','CG2': 'mbar','CG3': 'mbar','CG4': 'mbar'}

RESPONSE_BIT_NUM = 13

GAUGE_TYPES = ['CG', 'IG' , 'AI']

INTERFACE = Tool.INTF_SERIAL

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        
        #manage the presence of the keyword interface which will determine
        #which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE
        
        super(Instrument, self).__init__(resource_name, 'MGC4000', debug=debug,
                                         interface=interface, baud_rate=19200,
                                         term_chars = '\r',**kwargs)

    def measure(self, channel):
        
               
        
        if channel in self.last_measure:
            
            gtype, n = self.check_is_gauge(channel)
            
            if not self.DEBUG:
                
                if n is not None:
                    
                    if self.is_gauge_ready(gtype, n):                  
                    
                        answer = float(self.ask('#  RD%s%i'%(gtype, n)))
                    
                    else:
                        
                        answer = np.nan
                    
                else:
                    
                    answer = np.nan
#
            else:
                
                answer = random.random()
                
            self.last_measure[channel] = answer
            
        else:
            
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = np.nan
            
        return answer

    def read(self, num_bytes=RESPONSE_BIT_NUM):

        answer = super(Instrument,self).read(num_bytes)
        
        if answer:
            
            if answer[0] == '*':
                #the first 3 characters after the * are only space for RS232
                return answer[4:]
                
            elif answer[0] == '?':
                
                return answer
                
            else:
                print('Invalid answer from %s'%(self))
                return None
        
        else:
            print('No answer recieved from %s'%(self))
            return None
                

    def ask(self, msg):
        
        return super(Instrument,self).ask(msg, num_bytes=RESPONSE_BIT_NUM)

    def status(self, gtype='CG', n=None):
        """query the status of a pressure gauge"""
        
        if n is None:
            gtype, n = self.check_is_gauge(gtype)
            
        answer = i.ask('#  RS%s%i'%(gtype, n))
  
        
        if answer in STATUS:
                
            return STATUS[answer]
            
        else:
                
            return answer


    def is_gauge_ready(self, gtype='CG', n=None):
        """tell us if the gauge is ready to be measured"""
        answer = self.status(gtype, n)
        
        return (answer == GAUGE_READY)
        
    def check_is_gauge(self, gauge):
        
        n = int(gauge[2:])
        gtype = gauge[:2]
        
        if gtype in GAUGE_TYPES:
            
            return gtype, n
            
        else:
            #Raise an error here
            print("The gauge type '%s' is not accepted, please choose one \
from the list %s"%(gtype, GAUGE_TYPES))
            return None, None
    
GAUGE_READY = 'status ok'
        
STATUS = {
    '00 ST OK': GAUGE_READY,
    '01 OVPRS': 'IG over pressure; AI pressure over 1100 Torr',
    '02 EMISS': 'Ie failure',
    '04 FLVLO': 'filament V low',
    '08 FLOPN': 'IG filament open; CG sensor wire is open circuit or \
CG cable unplugged',
    '10 DEGAS': 'upper pressure limit exceeded during DEGAS operation',
    '20 ICLOW': 'Ic too low',
    '40 FLVHI': 'filament V high',
    '?01 INVALID': 'The device does not exist',
    '?01 SYNTX ER': 'Unknown command'
}

if (__name__ == '__main__'):
  
    i = Instrument("COM6",False)

    print i.measure('CG1')
    
    print i.measure('CG3')
