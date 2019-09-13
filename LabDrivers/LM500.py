# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
For Cryomagnetic LM-500, which I believe is the same machine as CG500.py
@author: zackorenberg


"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool


param = {
    'HeLevel_1': 'cm',
    'HeLevel_2': 'cm'
}

INTERFACE = Tool.INTF_GPIB
NAME = 'LM500'


class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name, debug=False, **kwargs):

        super(Instrument, self).__init__(resource_name,
                                         name=NAME,
                                         debug=debug,
                                         interface=INTERFACE,
                                         **kwargs)

    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'HeLevel_1':
                    answer = self.ask("CHAN 1; MEAS?")
                    answer = float(answer.strip(' ').split(' ')[0])
                elif channel == 'HeLevel_2':
                    answer = self.ask("CHAN 2; MEAS?")
                    answer = float(answer.strip(' ').split(' ')[0])
            else:
                answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        self.last_measure[channel] = answer
        return answer

    def status(self):
        answer = self.ask('STAT?').split(',')

        bit_status = [
            'Everything is ok',
            'Read in progress',
            'Refill active',
            'Refill timeout occurred',
            'Auto refil is inhibited by low = 0.0 or timeout',
            'Alarm limit is exceeded',
            'Open sensor was detected (LHe channel only)',
            'Burnout condition was detected'
        ]
        ## channel 1 ##
        binary = bin(int(answer[0])).split('b')[1]
        bits = list(binary)
        bits.reverse()
        chan1 = []
        for i in range(0, len(bits)):
            j = i + 1
            if bits[i] == '1':
                chan1.append(bit_status[j])
        if len(chan1) == 0:
            chan1.append(bit_status[0])

        ## channel 2 ##
        binary = bin(int(answer[1])).split('b')[1]
        bits = list(binary)
        bits.reverse()
        chan2 = []
        for i in range(0, len(bits)):
            j = i + 1
            if bits[i] == '1':
                chan2.append(bit_status[j])
        if len(chan1) == 0:
            chan2.append(bit_status[0])

        ## menu mode v operator mode ##
        if '0' in answer[2]:
            mode = 'Operator Mode'
        else:
            mode = 'Menu Mode'

        return {'Channel_1': chan1, 'Channel_2': chan2, 'Mode': mode}

    def set_low(self, channel, level):
        channel = int(channel)
        level = float(level)
        return self.ask("CHAN " + str(channel) + "; LOW " + str(level) + "; LOW?")

    def set_high(self, channel, level):
        channel = int(channel)
        level = float(level)
        return self.ask("CHAN " + str(channel) + "; HIGH " + str(level) + "; HIGH?")

    def get_low(self, channel):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; LOW?")

    def get_high(self, channel):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; HIGH?")

    def set_alarm(self, channel, level):
        channel = int(channel)
        level = float(level)
        return self.ask("CHAN " + str(channel) + "; ALARM " + str(level) + "; ALARM?")

    def get_alarm(self, channel):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; ALARM?")

    def set_mode(self, channel, mode):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; MODE " + str(mode) + "; MODE?")

    def get_mode(self, channel, mode):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; MODE?")

    def get_length(self, channel):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; LNGTH?")

    def get_interval(self, channel):
        channel = int(channel)
        return self.ask("CHAN " + str(channel) + "; INTVL?")

    def set_interval(self, channel, hour, minute, second):
        channel = int(channel)
        hour = str(int(hour)).zfill(2)
        minute = str(int(minute)).zfill(2)
        second = str(int(second)).zfill(2)
        return self.ask("CHAN " + str(channel) + "; INTVL " + hour + ":" + minute + ":" + second + "; INTVL?")

    def start_fill(self, channel):
        channel = int(channel)
        return self.ask("FILL " + str(channel) + "; FILL?")

    def fill_status(self, channel):
        channel = int(channel)
        return self.ask("FILL? " + str(channel))

    def set_units(self, channel, units):  # options are 'cm', 'in', '%'
        channel = int(channel)
        return self.ask('CHAN ' + str(channel) + '; UNITS ' + str(units) + '; UNITS?')

    def get_units(self, channel):
        channel = int(channel)
        return self.ask('CHAN ' + str(channel) + '; UNITS?')

    def set_boost(self, channel, mode):  # options are 'OFF', 'ON', 'SMART'
        channel = int(channel)
        return self.ask('CHAN ' + str(channel) + '; BOOST ' + str(mode) + '; BOOST?')

    def get_boost(self, channel):
        channel = int(channel)
        return self.ask('CHAN ' + str(channel) + '; BOOST?')


if __name__ == "__main__":
    i = Instrument("GPIB::7", debug=False)
