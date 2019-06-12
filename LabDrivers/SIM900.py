# -*- coding: utf-8 -*-
"""
Created  on Tue Jun 11 2019

@author: zackorenberg

All messages must be encoded/decoded into bytes

This driver is encoded for the following mainframe devices: SIM928, SIM980, SIM910. Since hot swapping is not allowed, you must manually write how many of each device is connected to the mainframe, in the following variables:

SIM928 = amount connected
SIM980 = amount connected
SIM910 = amount connected
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

import sys

#param = {'CH1': 'V', 'CH2': 'V', 'phase': 'deg', 'Z': 'Ohm', 'Z2': 'Ohm'}
param = {'Summing Offset Voltage':'microV'}

# for summing offset voltage
SIM928 = 4
SIM980 = 1
SIM910 = 1
AVERAGING_TIME = None
def create_SIM928_range():
    return [str(i+1) for i in range(0, SIM928)]
def create_SIM910_range():
    return [str(i+1) for i in range(0, SIM910)]
def create_SIM980_range():
    return [str(i+1) for i in range(0, SIM980)]
def create_SIM928_properties_obj():
    ret = {
        'Channel': {
            'type': 'text',
            'range': '',
            'readonly': True
        },
        'Voltage':{
            'type':'float',
            'range':[-120,120],
            'unit':'V'
        },
        'Output on':{
            'type':'bool',
            'range':True,
        },

    }
    return ret

def create_SIM910_properties_obj():
    ret =  {
        'Channel': {
            'type': 'text',
            'range': 'empty',
            'readonly': True
        },
        'Gain': {
            'type':'selector',
            'range':['1','2','5','10','20','50','100']
        },
        'Coupling':{
            'type':'selector',
            'range':['AC','DC']
        },
        'Amp Input':{
            'type':'selector',
            'range':['A','A-B','GND']
        }
    }
    return ret

def create_SIM980_properties_obj():
    #ret = {} multi object!
    ret = {
        'Channel': {
            'type': 'text',
            'range': '',
            'readonly': True
        },
        'Input': {
            'type':'multi',
            'range':['1','2','3','4'],
            'properties':{
                'State':{
                    'type':'selector',
                    'range':['OFF','ON, POSITIVE POLARITY','ON, NEGATIVE POLARITY']
                }
            }
        },
        'Averaging Time':{
            'type':'int',
            'range':[0,10000],
            'unit':'ms'
        }
    }
    return ret

properties = {
    'Voltage': {
        'type':'float',
        'range':[-120, 120],
        'unit':'V'
    },
    'Channel': {
        'type':'int',
        'range':[2, 15]
    },
    'Output': {
        'type':'bool',
        'range':True
    },
}
properties = {}
# set the properties
if SIM910 != 0:
    properties['SIM910'] = {
        'type':'multi',
        'range':create_SIM910_range(),
        'properties':create_SIM910_properties_obj()
    }
if SIM928 != 0:
    properties['SIM928'] = {
        'type':'multi',
        'range':create_SIM928_range(),
        'properties':create_SIM928_properties_obj()
    }
if SIM980 != 0:
    properties['SIM980'] = {
        'type':'multi',
        'range':create_SIM980_range(),
        'properties':create_SIM980_properties_obj()
    }


READ_BITS = 64
NAME = 'SIM900'
INTERFACE = Tool.INTF_SERIAL


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, NAME, debug, interface=INTERFACE, baud_rate=9600,
                                         term_chars="\n".encode(), timeout=2, bytesize=8, parity='N', stopbits=1, xonxoff=False, dsrdtr=False, **kwargs)
        self.connections = {}
        device_temp = {}
        self.ports = ['1','2','3','4','5','6','7','8']#,'A','B','C','D']
        print("Identifying devices")
        self.connected_devices = {}
        for port in self.ports:
            resp = self.ask_channel(port,"*IDN?")
            if resp == '' or resp == None:
                print("There is no device at port "+port)
            else:
                self.connections[port] = resp.split(',')[1]
                if self.connections[port] in self.connected_devices.keys():
                    self.connected_devices[self.connections[port]].append(port)
                else:
                    self.connected_devices[self.connections[port]] = [port]
                print(self.connections[port]+" detected on port "+port)
                device_temp[self.connections[port]] = True
        self.devices = device_temp.keys()

        try:
            if 'SIM980' in self.devices:
                #print(self.connected_devices)
                self.SIM980_PORT = self.connected_devices['SIM980'][0] # will only take first one
            else:
                self.SIM980_PORT = None
        except:
            print("error setting 'SIM980' port")
    def measure(self, channel):
        if channel == 'Summing Offset Voltage':
            if self.SIM980_PORT is not None:
                answer = self.read_offset_voltage(self.SIM980_PORT, AVERAGING_TIME)
                answer = float(answer)
            else:
                answer = None
        else:
            print("invalid measurement channel: "+channel)
            return -1
        self.last_measure[channel] = answer
        return answer

    def get(self):
        ret = {}
        if 'SIM910' in self.devices:
            ret['SIM910'] = self.get_SIM910_obj()

        if 'SIM980' in self.devices:
            ret['SIM980'] = self.get_SIM980_obj()

        if 'SIM928' in self.devices:
            ret['SIM928'] = self.get_SIM928_obj()
        print("ret", ret)
        return ret
    def set(self, data):
        #print(data)
        try:
            for device, obj in data.items():
                for unimportant, dat in obj.items():
                    if device == 'SIM910':
                        self.set_SIM910_obj(dat)
                    elif device == 'SIM980':
                        self.set_SIM980_obj(dat)
                    elif device == 'SIM928':
                        self.set_SIM928_obj(dat)
                    else:
                        print("Unsupported device: ",device)
        except:
            print("Set Error",sys.exc_info())

    def get_SIM910_obj(self):
        ret = {}
        for i in range(0, SIM910):
            j = str(i+1)
            channel = self.connected_devices['SIM910'][i]
            ret[j] = {
                'Channel': channel,
                'Gain': self.get_preamplifier_gain(channel),
                'Coupling': self.get_preamplifier_coupling(channel),
                'Amp Input': self.get_preamplifier_input(channel)
            }
        return ret
    def set_SIM910_obj(self, obj):
        # assuming correct type of object
        chan = obj['Channel']
        self.set_preamplifier_gain(chan, obj['Gain'])
        self.set_preamplifier_coupling(chan, obj['Coupling'])
        self.set_preamplifier_input(chan, obj['Amp Input'])

    def get_SIM928_obj(self):
        ret = {}
        for i in range(0, SIM928):
            j = str(i+1)
            channel = self.connected_devices['SIM928'][i]
            ret[j] = {
                'Channel': channel,
                'Voltage': self.get_voltage(channel),
                'Output on': self.get_output(channel),
            }
        return ret
    def set_SIM928_obj(self, obj):
        chan = obj['Channel']
        self.set_voltage(chan, obj['Voltage'])
        self.toggle_output(chan, obj['Output on'])
    def get_SIM980_obj(self):
        ret = {}
        for i in range(0, SIM980):
            j = str(i+1)
            channel = self.connected_devices['SIM980'][i]
            # make input stuff
            inp_list = self.get_amplifier(channel)

            inp_options = {
                '0':'OFF',
                '1':'ON, POSITIVE POLARITY',
                '-1':'ON, NEGATIVE POLARITY'
            }
            #print(inp_list, [inp_options[inp_list[q]] for q in range(0, len(inp_list))], [inp_list[q] for q in range(0, len(inp_list))])
            inp_obj = {}
            for p in range(0,4):
                k = str(p+1)
                inp_obj[k] = { 'State':inp_options[inp_list[p]] }

            ret[j] = {
                'Channel': channel,
                'Input': inp_obj,
                'Averaging Time':AVERAGING_TIME
            }
        return ret
    def set_SIM980_obj(self, obj):
        chan = obj['Channel']
        convert = {
            'OFF':'0',
            'ON, POSITIVE POLARITY':'1',
            'ON, NEGATIVE POLARITY':'-1'
        }
        for input, iobj in obj['Input'].items():
            self.set_amplifier_channel(chan, input, convert[iobj['State']])
        self.set_averaging_time(obj['Averaging Time'])


    def ask(self, msg):
        # custom made
        self.write(msg)
        return self.read()

    def write(self, msg):
        # custom made
        self.connection.write(msg.encode() + self.term_chars)
    def read(self):
        return self.connection.read(READ_BITS).decode()

    def ask_channel(self, channel, msg):
        #channel = int(channel) can be letter!
        self.write("CONN "+str(channel)+", \"xyz\"")

        answer = self.ask(msg)
        self.write("xyz")
        return answer.strip('\n').strip('\r').strip('\n') # incase sandwhich or reverse order
    def ask_channel_multiple(self, channel, *msgs):
        #channel = int(channel)
        self.write("CONN "+str(channel)+",\"xyz\"")
        resp = []
        for msg in msgs:
            resp.append(self.ask(msg))
        self.write("xyz")
        return resp
    def write_channel(self, channel, msg):
        #channel = int(channel) can be letter!
        self.write("CONN "+str(channel)+", \"xyz\"")
        self.write(msg)
        self.write("xyz")
    def write_channel_multiple(self, channel, *msgs):
        #channel = int(channel)
        self.write("CONN "+str(channel)+",\"xyz\"")
        resp = []
        for msg in msgs:
            self.write(msg)
        self.write("xyz")

    #def measure(self, channel):

    def get_voltage(self, channel):
        channel = str(channel)
        if channel in self.connections.keys():
            # check if SIM928
            if self.connections[channel] == 'SIM928':
                answer = self.ask_channel(channel, "VOLT?")
                return float(answer)
            else:
                print("Unsupported device: "+self.connection[channel])
        else:
            print("No device connected to channel "+channel)
        return None

    def set_voltage(self, channel, voltage):
        channel = str(channel)
        voltage = str(float(voltage))
        if channel in self.connections.keys():
            # check if SIM928
            if self.connections[channel] == 'SIM928':
                answer = self.ask_channel(channel, "VOLT "+voltage+"; VOLT?")
                return float(answer)
            else:
                print("Unsupported device: "+self.connection[channel])
        else:
            print("No device connected to channel "+channel)
        return None

    def enable_output(self, channel):
        channel = str(channel)
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM928':
                self.write_channel(channel, "OPON")
    def disable_output(self, channel):
        channel = str(channel)
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM928':
                self.write_channel(channel, "OPOF")
    def toggle_output(self, channel, state):
        state = int(state) #0 for false, 1 for true
        channel = str(channel)
        if channel in self.connections.keys(): # might only befor SIM928
            if self.connections[channel] == 'SIM928':
                self.write_channel(channel, "EXON "+str(state))
    def get_output(self, channel):
        channel = str(channel)
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM928':
                answer = self.ask_channel(channel, 'EXON?')
                if '0' in answer:
                    return False
                elif '1' in answer:
                    return True
                else:
                    return None
    def set_amplifier_channel(self, channel, input, state):
        """

        :param channel: Channel on mainframe
        :param input: Input channel on SIM980 (1-4, 0 for all)
        :param state: 0 for off, -1 for negative polarity, +1 for positive polarity
        :return: none
        """
        channel = str(channel)
        input = str(input)
        state = str(state)
        if input.lower() == 'all':
            input = '0'
        elif not input.isdigit():
            print("Invalid channel: " + input)
            return
        if state.lower() == 'off':
            state = '0'
        elif 'neg' in state.lower():
            state = '-1'
        elif 'pos' in state.lower():
            state = '1'
        elif state.isdigit():
            # this is good
            unusedvariable = 1
        else:
            print("Invalid state: "+state)
            return
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM980':
                self.write_channel(channel, "CHAN "+input+","+state)
                return
            print("Invalid device: " + self.connections[channel])
            return None
        print("Invalid channel: " + channel)
        return None
    def get_amplifier_channel(self, channel, input):
        """

        :param channel: Channel on mainframe
        :param input: Input channel on SIM980 (1-4, 0 for all)
        :return: none
        """
        channel = str(channel)
        input = str(input)
        if input.lower() == 'all':
            input = '0'
        elif not input.isdigit():
            print("Invalid channel: "+input)
            return None
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM980':
                answer = self.ask_channel(channel, "CHAN? " + input)
                return answer
            print("Invalid device: "+self.connections[channel])
            return None
        print("Invalid channel: "+channel)
        return None

    def get_amplifier(self, channel):
        return self.get_amplifier_channel(channel, '0').split(',')

    def read_offset_voltage(self, channel, averaging_time = None):
        channel = str(channel)
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM980':
                if averaging_time is not None and averaging_time:
                    averaging_time = str(int(averaging_time))
                    answer = self.ask_channel(channel, "READ? "+averaging_time)
                else:
                    answer = self.ask_channel(channel, "READ?")
                return answer

    def set_averaging_time(self, averaging_time):
        try:
            AVERAGING_TIME = int(averaging_time)
        except:
            AVERAGING_TIME = None


    def reset(self, channel):
        channel = str(channel)
        if channel in self.connections.keys():
            self.write_channel(channel, "*RST")

    def set_preamplifier_gain(self, channel, gain):
        gain = str(gain)
        allowed = ['1','2','5','10','20','50','100']
        if gain not in allowed:
            print("Invalid gain: "+gain)
            return
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM910':
                self.write_channel(channel, "GAIN "+gain)
                return
            print("Invalid device: "+self.connections[channel])
            return
        print("Invalid channel: "+channel)



    def set_preamplifier_coupling(self, channel, coupling):
        coupling == str(coupling)
        if coupling.lower() == 'ac':
            coupling = '1'
        elif coupling.lower() == 'dc':
            coupling = '2'
        allowed = ['1','2']
        if coupling not in allowed:
            print("Invalid coupling: "+coupling)
            return
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM910':
                self.write_channel(channel, "COUP "+coupling)
                return
            print("Invalid device: "+self.connections[channel])
            return
        print("Invalid channel: "+channel)


    def set_preamplifier_input(self, channel, input_mode):
        input_mode == str(input_mode)
        if input_mode.lower() == 'a':
            input_mode = '1'
        elif input_mode.lower() == 'a-b':
            input_mode = '2'
        elif input_mode.lower() == 'gnd' or input_mode.lower() == 'ground':
            input_mode = '3'

        allowed = ['1','2','3']
        if input_mode not in allowed:
            print("Invalid input mode: "+input_mode)
            return
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM910':
                self.write_channel(channel, "INPT "+input_mode)
                return
            print("Invalid device: "+self.connections[channel])
            return
        print("Invalid channel: "+channel)


    def get_preamplifier_gain(self, channel):
        channel = str(channel)
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM910':
                answer = self.ask_channel(channel, "GAIN?")
                return answer
            print("Invalid device: "+self.connections[channel])
            return None
        print("Invalid channel: "+channel)
        return None
    def get_preamplifier_coupling(self, channel):
        channel = str(channel)
        convert = {
            '1':'AC',
            '2':'DC'
        }
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM910':
                answer = self.ask_channel(channel, "COUP?")
                answer = str(answer)
                return convert[answer]
            print("Invalid device: "+self.connections[channel])
            return None
        print("Invalid channel: "+channel)
        return None
    def get_preamplifier_input(self, channel):
        channel = str(channel)
        convert = {
            '1':'A',
            '2':'A-C',
            '3':'GND'
        }
        if channel in self.connections.keys():
            if self.connections[channel] == 'SIM910':
                answer = self.ask_channel(channel, "INPT?")
                answer = str(answer)
                return convert[answer]
            print("Invalid device: "+self.connections[channel])
            return None
        print("Invalid channel: "+channel)
        return None

if __name__ == "__main__":

    i = Instrument("COM4")

#    i.write('SNDT 4,"GAIN"')
    i.write("*IDN?".encode())
    print(i.read(64).decode())
    i.write("*IDN?".encode())
    print(i.read(64).decode())
    i.write("*IDN?".encode())
    print(i.read(64).decode())
    #print(i.ask("*IDN?",20))