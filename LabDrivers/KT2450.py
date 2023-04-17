# -*- coding: utf-8 -*-
"""
Modified on Tue Jun 4 2019
Keithley 2450
@author: zackorenberg

"""

try:
    from . import Tool
except:
    import Tool

import numpy as np


try:
    from . import KT2400 as KT2400
except:
    import KT2400
#param = {"VOLTAGE":'V',"CURRENT":'A'}
param = {'V': 'V', 'I': 'A'}

INTERFACE = Tool.INTF_GPIB


class Instrument(KT2400.Instrument):
    # class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument Keithley 2450"""
    """"Child class of similar KT2400.py instrument driver"""

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name,
                                         name='KT2450',
                                         debug=debug,
                                         interface=INTERFACE,
                                         backwardcompatible=False,
                                         **kwargs)
        answer = self.ask("*IDN?")
        print("model: "+answer)
        if "MODEL 2450" in answer:
            lang = self.ask("*LANG?")
            if "SCPI2400" in lang:
                self.write("*LANG SCPI")
                print("=== Please reboot device ===")
        elif "MODEL 2400" in answer: # will happen iff in incorrect language mode
            try:
                self.write("*LANG SCPI")
                print("=== Please reboot device ===")
            except:
                print("You are using the incorrect driver for Keithley Model 2400")
                pass
        self.enable_output()

    def measure(self, channel):
        if channel in self.last_measure:

            #'*RST'
            # Clear buffer before taking a measurement

            if channel == 'V':
                if not self.DEBUG:
                    self.write('VOLT:RANG:AUTO ON')
                    # to set on autorange
                    #answer = self.ask(':READ?')
                    answer = self.ask(':MEAS:VOLT?')
                    if type(answer) is str: #incase its running in 2400 mode
                        if ',' in answer:
                            answer = float(answer.split(',')[0])
                        else:
                            answer = float(answer)
                    #if not answer or answer=='\n': ONLY NEEDED FOR
                    #    self.enable_output()
                    #    return self.measure(channel)
                    #elif type(answer) is not str and math.isnan(answer): #answer will be nan if error
                    #    print("Please set Output on") # will be set by default for 2450 from above
                    #    answer = float(answer)
                    #else:
                    #    answer = float(answer.split(',')[0])
                else:
                    answer = np.random.random()
                self.last_measure[channel] = answer

            elif channel == 'I':
                if not self.DEBUG:
                    self.write('CURR:RANG:AUTO ON')
                    # to set on autorange
                    #answer = self.ask(':READ?')
                    answer = self.ask(':MEAS:CURR?')
                    if type(answer) is str: #incase its running in 2400 mode
                        if ',' in answer:
                            answer = float(answer.split(',')[1])
                        else:
                            answer = float(answer)
                    #if not answer or answer=='\n':
                    #    self.enable_output()
                    #    return self.measure(channel)
                    #elif type(answer) is not str and math.isnan(answer): #answer will be nan if error
                    #    print("Please set Output on")
                    #    answer = float(answer)
                    #else:
                    #    answer = float(answer.split(',')[1])

                else:
                    answer = np.random.random()
                self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        answer = float(answer)
        return answer

    def set_voltage(self, voltage, i_compliance=1.0E-6, v_compliance=1):
        if not self.DEBUG:
            voltage = float(voltage)
            i_compliance = float(i_compliance)
            v_compliance = float(v_compliance)
            self.write(':SOUR:VOLT:RANG:AUTO 1')
            # set autorange on source

            #c = ':SENS:CURR:PROT %r' % compliance
            c = ':SOUR:VOLT:ILIM %r' % i_compliance
            self.write(c)
            c = ':SOUR:CURR:VLIM %r' % v_compliance
            self.write(c)
            # set compliance

            s = ':SOUR:FUNC VOLT;:SOUR:VOLT %f' % voltage
            self.write(s)
        else:
            print("voltage set to " + str(voltage) + " on " + self.ID_name)

    def set_overvoltage(self, overvoltage):
        if not self.DEBUG:
            overvoltage = float(overvoltage)
            self.write(':SOUR:VOLT:PROT PROT%r' % overvoltage)
        else:
            print("overvoltage set to " + str(overvoltage) + " on " + self.ID_name)

if __name__ == "__main__":
    i = Instrument("GPIB0::11", debug=False)
    print((i.identify("Hello, this is ")))

    #i.configure_output('VOLT', 0, 1E-8)
    i.set_voltage(1, 1.0e-7)
    print((i.measure('V')))
    print((i.measure('I')))
