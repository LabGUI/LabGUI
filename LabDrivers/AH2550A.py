# -*- coding: utf-8 -*-
"""
Created on Thurs June 6 2019
@author: zackorenberg

"""
try:
    from . import Tool
except:
    import Tool

import time
import threading

param = {
    'Capacitance' : 'pF',
    'Loss'        : 'ns',
    'Voltage'     : 'V',
    'Frequency'   : 'Hz'
}

INTERFACE = Tool.INTF_GPIB
NAME = 'AH2550A'


class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument AH2550A"""""

    def __init__(self, resource_name, debug=False, **kwargs):

        super(Instrument, self).__init__(resource_name,
                                          name=NAME,
                                          debug=debug,
                                          interface=INTERFACE,
                                          **kwargs)


        self.connection.control_ren(2)
    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'Capacitance':
                    answer = self.get_data()[0]
                elif channel == 'Loss':
                    answer = self.get_data()[1]
                elif channel == 'Voltage':
                    answer = self.get_data()[2]
                elif channel == 'Frequency':
                    answer = self.get_frequency()

            else:
                    answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        self.last_measure[channel] = answer
        return answer


    def get_data(self):
        resp = self.ask('SINGLE')
        resp = resp.split(' ')
        #will be in form 'C=val unit\tL=val unit\tV=val unit
        ret = []
        # cycle through whitespace arrays and determine which is which
        flag = False
        for item in resp:
            if flag:
                ret.append(float(item))
                flag = False
                continue
            if '=' in item: # check to see if number is enclosed by checking length
                if item[-1] == '=': #if last character is equal sign, next item is value
                    flag = True
                    continue
                else:
                    ret.append( float(item.split('=')[1]) )


        return ret # order is capacitance, loss, voltage

    def get_frequency(self):
        resp = self.ask('SHOW FREQUENCY')
        resp = resp.split(' ',1)[1].strip()
        return float(resp.split(' ')[0])

    # alternative method
    def continuous(self, on:bool):
        if on:
            self.write('CONTINUOUS ON')
        else:
            self.write('CONTINUOUS OFF')

    def acquire_data(self, duration, frequency=0.2):
        duration=float(duration)
        frequency=float(frequency)
        self.continuous(True)
        raw_data=[]
        timer = threading.Timer(duration, self.continuous, [False])
        timer.start()
        t_start=time.time()
        try:
            while True:
                r_time, r_data = time.time(), self.read()
                raw_data.append( (r_time, r_data ))
                tnow = time.time()
                if (frequency - (tnow - r_time)) > 0:
                    time.sleep( frequency - (tnow - r_time) )
        except: # this means timer turned continuous off, and nothing was read
            pass

        #if you reached here, all readings are done and its time to process
        data = []
        for tup in raw_data:
            ret = [tup[0]-t_start]
            resp = tup[1].split(' ')
            flag = False
            for item in resp:
                if flag:
                    ret.append(float(item))
                    flag = False
                    continue
                if '=' in item:  # check to see if number is enclosed by checking length
                    if item[-1] == '=':  # if last character is equal sign, next item is value
                        flag = True
                        continue
                    else:
                        ret.append(float(item.split('=')[1]))
            data.append(tuple(ret))

        return data

    def average(self, average):  # 4 is default, higher the number slower the measurement
        if self.DEBUG == False:
            self.write('AVERAGE ' + str(average))
        else:
            print("average - debug mode")
    def frequency(self, freq):  # broken function. Something wrong with capacitance bridge
        if self.DEBUG == False:
            self.write('FREQUENCY' + str(freq))
        else:
            print("frequency - debug mode")

if __name__ == "__main__":
    i = Instrument("GPIB::1", debug=False)








