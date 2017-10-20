import time
import random
import numpy as np
import logging



try:
    import serial
except:
    pass

try :
    
    from . import Tool
    
except:
    
    import Tool


#!/usr/bin/env python
#import string, os, sys, time
#import io
param = {'1': 'Torr', '2': 'Torr'}

INTERFACE = Tool.INTF_SERIAL

class Instrument(Tool.MeasInstr):
    
    def __init__(self, resource_name, debug = False, **keyw):
        super(Instrument, self).__init__(resource_name, 'MKS', debug = debug, 
                                         interface = INTERFACE,
                                         baud_rate = 9600,
                                         term_chars = "\r", timeout = 1, 
                                         bytesize = serial.SEVENBITS, 
                                         parity = serial.PARITY_EVEN, 
                                         stopbits = serial.STOPBITS_ONE)    
                                         

    def measure(self, channel):
        
        if channel in self.last_measure:
            
            if not self.DEBUG:
                
                answer = self.get_pressure(channel)
                
            else:
                
                print("the channel " + channel)
                answer = random.random()
            self.last_measure[channel] = answer
            
        else:
            
            print("you are trying to measure a non existent channel : "  \
                + channel)
            print("existing channels :", self.channels)
            answer = None
            
        return answer

    def get_pressure(self, chan):
        
        chan = float(chan)
        
        if not self.DEBUG:
            
            if chan == 1:
                
                self.write('@6011?')
                
            elif chan == 2:
                
                self.write('@6012?')
                
            else:
                
                return None
            
                        
            try :
                
                data_string = self.read(13)
                
            except:
                
                logging.error("")
                return np.nan
            
            try :            
            
                return float(data_string.split(':')[1])
            
            except ValueError:
                
                logging.error("")
                return np.nan
            
            except AttributeError:  
                
                logging.error("")
                return np.nan
        
        
                
            
        else:
            
            return 1.23e-3


    def read2(self):
        
        if not self.DEBUG:
            
            sio = self.sio
            time.sleep(0.1)
            out = ''
            
            while sio.inWaiting() > 0:
                
                out += sio.read(1)
                
            return (out)

    # initialization should open it already
    def reopen(self):
        
        if not self.DEBUG:
            
            self.connexion.open()

if __name__ == "__main__":
    

    i = Instrument("COM8")
    
    print("hello")

    print(i.get_pressure(1))
                    
    
#    i = serial.Serial("COM8", bytesize = serial.SEVENBITS, 
#                              parity = serial.PARITY_EVEN)
#    
#    print(i)
#    
#    i.write('@6011?\r')    
#    
#    print(i.read(13))
#    
#    i.close()