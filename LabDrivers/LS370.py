#!/usr/bin/env python
import random
import numpy as np
import logging

try:
    from . import Tool
except:
    import Tool


CHANNELS_IDX = {"1K Pot":1,"Still":2,"ICP":3,"MC":4}

param = {'heater': '%',"1K Pot":"Ohm","Still":"Ohm","ICP":"Ohm","MC":"Ohm"}


TEMP_CONTROL_PARAM = ['channel', 'filter','units', 'delay', 'current/power','htr limit', 'htr resistance']

HEATER_RANGE = ['Off','31.6uA','100uA','316uA','1mA','3.16mA','10mA','31.6mA','100mA']
HEATER_RANGE_VAL = [0,31.6e-6,100e-6,316e-6,1e-3,3.16e-3,10e-3,31.6e-3,100e-3]
INTERFACE = Tool.INTF_GPIB

HEATER_RESISTANCE = 120
MANUAL_HTR_MAX_CURRENT = 0.091

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        
        #manage the presence of the keyword interface which will determine
        #which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE
        
        super(Instrument, self).__init__(resource_name, 'LS370', debug = debug,
                                         interface = interface, **kwargs)

    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'heater':
                    return self.get_heater_range_value()*self.get_heater_output()*0.01
                else:
                    answer = self.read_channel(CHANNELS_IDX[channel],param[channel])

            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def read_channel(self, chan, units = "Ohm"):
        
        if not self.DEBUG:
            
            if units == "K":
                
                data = self.ask('RDGK? %02d'%(chan))
            
            elif units == "Ohm":
                
                data = self.ask('RDGR? %02d'%(chan))
            
            
            try:
                return float(data)
            except:
                logging.error("the reading from the lakeshore 370 is no a number, please check that the timout is sufficiently large, 0.1 s is too short")
                return np.nan
                        
        else:
            return 1337.0

    def parameter_setup(self,**kwargs):
        """
            Temperature Control Setup Parameter Command
            CSET <channel>,<filter>,<units>,<delay>, <current/power>, 
            <htr limit>, <htr resistance>[term]
        """
        #fetch the actual parameters
        actual_parameters = self.parameter_query()
        
        #print their values
        print(",".join(TEMP_CONTROL_PARAM))
        msg = "%02d,%i,%i,%03d,%i,%i,%07.3f"%(tuple(actual_parameters))
        print(msg)
                
        #loop over the kwargs
        for key in kwargs:
            
            #reacts only if one finds a valid key
            if key in TEMP_CONTROL_PARAM:
                
                #get the key
                idx = TEMP_CONTROL_PARAM.index(key)
                value = kwargs[key]
                
                #check the type (should check max values as well...)
                if isinstance(value,int) or isinstance(value,float):
                    
                    actual_parameters[idx] = value
                
        #Format: nn,n,n,nnn,n,n,nnn.nnn 
        msg = "%02d,%i,%i,%03d,%i,%i,%07.3f"%(tuple(actual_parameters))
        print(msg)
        
        if not self.DEBUG:
            
            self.write('CSET %s'%(msg))

    
    def parameter_query(self):
        """
        #CSET?
        #Temperature Control Setup Parameter Query 
        #Input: 
        #CSET?[term]
        #Returned: 
        #<channel>, <filter>,<units>, <delay>, <current/power>,<htr limit>, <htr resistance>[term] 
        #Format: nn,n,n,nnn,n,n,nnn.nnn 

        """
        if not self.DEBUG:
            
            answer = self.ask('CSET?')
            
        else:
            
            answer = "01,0,2,025,1,8,+120.000"
            
        parameters = [int(el) for el in answer.split(',')[:-1]]
        parameters.append(float(answer.split(',')[-1]))
        
        return parameters
#            channel, filter_reading, units, delay, htr_output, htr_limit, htr_resistance = self.ask('CSET?')
            
            
            
    def setpoint_temperature(self,channel, target_temp = None):
        if not self.DEBUG:
            
            #make sure the channel is the one actually controlled and
            #that the units are in kelvin
            self.parameter_setup(channel = channel, units = 1)
            
            if target_temp == None:
                
                return float(self.ask('SETP?'))
                
            else:
                
                exponent = int(np.log10(target_temp))
                
                if exponent > 0:
                    
                    mantisse = target_temp / (np.power(10.,exponent))
                    
                elif exponent == 0:
                    
                    exponent = -3
                    mantisse = target_temp * (np.power(10.,np.abs(exponent)))
                    
                else:
                    
                    mantisse = target_temp * (np.power(10.,np.abs(exponent)))
                
                if exponent > 0:
                
                    self.write("SETP %07.3fE+%02d"%(mantisse,exponent))                
                
                else:
                    
                    self.write("SETP %07.3fE%03d"%(mantisse,exponent))

    def set_heater_range(self, htr_range):
        
        htr_range = int(htr_range)
        
        if not self.DEBUG:
            if htr_range >= 0 and htr_range < 9:
                self.write('HTRRNG %i' % htr_range)
        
        else:
            
            print("DEBUG : Set htr range :%s"%(HEATER_RANGE[htr_range]))


    def set_heater_off(self):
        """stop the Manual output heater"""
        self.set_heater_range(0)

    def get_heater_range(self):
        if not self.DEBUG:
            return HEATER_RANGE[int(self.ask('HTRRNG ?'))]
        else:
            return 0
        
        
    def get_heater_range_value(self):
        if not self.DEBUG:
            return HEATER_RANGE_VAL[int(self.ask('HTRRNG ?'))]
        else:
            return random.randint(0,len(HEATER_RANGE))

    def set_heater_output(self, percent):
        if not self.DEBUG:
            if percent >= 0. and percent <= 100.:
                self.write('MOUT %.3f' % percent)
        else:
            print("DEBUG : Set htr output :%.2f"%(percent))

    def set_heater_current(self, current, 
                           htr_range_array = np.array(HEATER_RANGE_VAL)):
        """set a current (in A) through the Manual output"""
        
        #input current is greater than 91mA, so we forbid it
        if current > MANUAL_HTR_MAX_CURRENT:
            
            logging.warning("the current you want to set on the heater is \
above the threshold of %.3f A : %.6f A"%(MANUAL_HTR_MAX_CURRENT, current))
        
        else:
            #this way the heater output is always between 20% and 80%
            #for all intermediate ranges except the maximum and minimum ones
            htr_range = htr_range_array[htr_range_array >= 0.4 * current]
            
            #for all ranges except the maximum and minimum ones
            if len(htr_range) > 1 and \
                  len(htr_range) < len(HEATER_RANGE_VAL) - 1:
                
                htr_range = htr_range[1]
                
            else:
                
                htr_range = htr_range[0]
            
            #heater output in percent
            htr_output = np.round(100*(current/htr_range),2)
            
            #set the heater output
            self.set_heater_output(htr_output)
            
            if htr_output:
                #the range isn't 0, set the range
                self.set_heater_range(
                    np.squeeze(np.where(htr_range_array == htr_range)))
                
            else:
                #the range is below the minimum, so we turn it off for safety
                self.set_heater_off()
            
    def set_heater_power(self, power, htr_resistance = HEATER_RESISTANCE):
        """set a current through the Manual output according to a power"""
        
        current = np.sqrt(power / htr_resistance)     
        
        self.set_heater_current(current)
            
    def get_heater_output(self):
        if not self.DEBUG:
            return float(self.ask('MOUT ?'))
        else:
            return np.round(random.random()*100,2)

    def auto_scan(self):
        if not self.DEBUG:
            self.write('SCAN 1,1')

    def scanner_to_channel(self, chan):
        if not self.DEBUG:
            self.write('SCAN %d,0' % chan)


if (__name__ == '__main__'):


    i = Instrument("GPIB0::12",False)
#    print i.read()
#    print(i.setpoint_temperature(6,5e-2))
    print i.measure("heater")
    i.set_heater_off()
    print i.get_heater_range()
    print i.get_heater_output()
    i.close()
    


    
