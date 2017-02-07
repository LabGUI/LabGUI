# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 14:01:13 2013

@author: Lilly Tong
"""

import time
try:
    from . import Tool
except:
    import Tool
    
import random
param = {'Capacitance': 'pF'}

INTERFACE = Tool.INTF_GPIB

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(
            resource_name, 'AH2550A', debug=debug, interface = INTERFACE, **kwargs)

    def measure(self, channel):
        if self.last_measure.has_key(channel):
            if not self.DEBUG:
                if channel == 'Capacitance':
                    answer = self.capacitance(self.single())
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        return answer

    def average(self, average):  # 4 is default, higher the number slower the measurement
        if self.DEBUG == False:
            self.write('AVERAGE ' + str(average))
        else:
            print("average - debug mode")

    def capacitance(self, msg):  # parses the string and only returns capacitance

        if self.DEBUG == False:

            return float(msg[3:13])
        else:
            print("capacitance - debug mode")

    def continuousON(self):
        if self.DEBUG == False:
            self.write('CONTINUOUS')
        else:
            print("continuous - debug mode")

    def continuousOFF(self):
        if self.DEBUG == False:
            self.write('CONTINUOUS OFF')
        else:
            print("continuousOFF - debug mode")

    def frequency(self, freq):  # broken function. Something wrong with capacitance bridge
        if self.DEBUG == False:
            self.write('FREQUENCY' + str(freq))
        else:
            print("frequency - debug mode")

    def showFrequency(self):
        if self.DEBUG == False:
            return self.ask('SHOW FREQUENCY')
        else:
            print("show frequency - debug mode")

    def single(self):
        if self.DEBUG == False:
            return self.ask('SINGLE')
        else:
            print("single - debug mode")


# following code has been tested and known to work.
if (__name__ == '__main__'):
    myinst = Instrument('GPIB::28')
    myinst.average(8)
    myinst.continuousON()
    for i in range(10):
        capacitance = myinst.capacitance(
            myinst.read())  # a float, displays in pF
        print(capacitance)
        time.sleep(3)
    myinst.continuousOFF()
