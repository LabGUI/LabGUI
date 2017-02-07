try:
    from . import Tool
except:
    import Tool
    

try:
    from . import KT2400 as KT2400
except:
    import KT2400
#param = {"VOLTAGE":'V',"CURRENT":'A'}
param = {'V': 'V', 'I': 'A'}

INTERFACE = Tool.INTF_GPIB

class Instrument(KT2400.Instrument):
#class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument Keithley 2450"""
    """"Child class of similar KT2400.py instrument driver"""
    
   
    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, name = 'KT2450', debug=debug, interface = INTERFACE, **kwargs)
 

    def measure(self, channel):
        if channel in self.last_measure:

            #'*RST'
            #Clear buffer before taking a measurement
            
            if channel == 'V':
                if not self.DEBUG:
                    self.write('VOLT:RANG:AUTO ON')
                    #to set on autorange
                    #answer = self.ask(':READ?')
                    answer = self.ask(':MEAS:VOLT?')
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'I':
                if not self.DEBUG:
                    self.write('CURR:RANG:AUTO ON')
                    #to set on autorange
                    #answer = self.ask(':READ?')
                    answer = self.ask(':MEAS:CURR?')

                else:
                    answer = random.random()
                self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        answer = float(answer)
        return answer
        
        
    def set_voltage(self, voltage, compliance=1.0E-7):
        if not self.DEBUG:
        
            self.write(':SOUR:VOLT:RANG:AUTO 1')
            #set autorange on source

            #c = ':SENS:CURR:PROT %r' % compliance            
            c = ':SOUR:VOLT:ILIM %r' % compliance
            self.write(c)
            #set compliance

            s = ':SOUR:FUNC VOLT;:SOUR:VOLT %f' % voltage
            self.write(s)
        else:
            print("voltage set to " + str(voltage) + " on " + self.ID_name)        
       

if __name__ == "__main__":
    i = Instrument("GPIB0::11",debug=False)
    print((i.identify("Hello, this is ")))
    
    #i.configure_output('VOLT', 0, 1E-8)
    i.set_voltage(1,1.0e-7)
    print((i.measure('V')))
    print((i.measure('I')))
