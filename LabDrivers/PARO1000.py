# -*- coding: utf-8 -*-
"""
Created on Wed May 08 13:31:59 2013
Paroscientific Digiquartz Pressure sensor 1000 Driver
@author: PF
"""

import random
try:
    from . import Tool
except:
    import Tool

param = {'PRESSURE': 'psi', 'TEMPERATURE': 'C'}

INTERFACE = Tool.INTF_SERIAL

properties = {
    'Units': {
        'type':'selection',
        'range':[
            'psi',
            'mbar or hPa',
            'bar',
            'kPa',
            'MPa',
            'in Hg',
            'mm Hg or torr',
            'm H20'
        ]
    }
}

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):

        # manage the presence of the keyword interface which will determine
        # which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE

        super(Instrument, self).__init__(resource_name,
                                         'PARO1000', debug=debug,
                                         interface=interface,
                                         term_chars='', baudrate=9600, parity='N', timeout=1, **kwargs)
    def write(self, msg):
        return self.connection.write((msg+'\r\n').encode())
    def write_multiple(self, msgs):
        return self.connection.write(('\r\n'.join(msgs)+'\r\n').encode())
    def read(self):
        return self.connection.readline().decode()
    def ask(self, msg):
        self.write(msg)
        return self.read()


    def measure(self, channel='PRESSURE'):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'PRESSURE':
                    command = '*0100P3'
                elif channel == 'TEMPERATURE':
                    command = '*0100Q3'
                answer = self.ask(command)
                answer = float(answer[5:])  # remove the first 5 characters
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def get(self):
        ret = {}
        if not self.DEBUG:
            for channel in properties.keys():
                if channel == 'Units':
                    self.write('*0100UN')
                    resp = self.read()
                    ret['Units'] = properties['Units']['range'][int(resp[8:])-1]

        return ret

    def set(self, data):
        if not self.DEBUG:
            for channel, value in data.items():
                if channel == 'Units':
                    try:
                        idx = properties['Units']['range'].index(value)
                    except:
                        print("Invalid unit selection for PARO1000")
                        continue

                    try:
                        self.write_multiple(['*0100EW','*0100UN=%d'%(idx+1)])
                    except:
                        print("Unable to write to PARO1000")
        else:
            print("Debug mode enabled, PARO1000 property data: ", data)
    def identify(self, msg=''):
        if not self.DEBUG:

            answer = self.ask('*0100MN')
            answer = "PARO" + answer[8:]

        else:

            answer = self.ID_name

        return msg + answer


if __name__ == "__main__":
    i = Instrument("COM3")
    i.get()
    #print("writing")
    #i.connection.write('*0100EW\r\n*0100UN=1\r\n'.encode())
    #i.connection.write('*0100P3\r\n'.encode())
    #print("reading")
    #print(i.connection.readline().decode())
    #print(i.identify())
