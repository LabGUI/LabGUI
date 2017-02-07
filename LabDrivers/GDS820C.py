# -*- coding: utf-8 -*-
"""
Created on Thu Jun 12 18:25:10 2014
GDS820C 150MHz Ocsilloscope
NOTE : to connect the oscilloscope, you should use a NULL RS232 modem, or to reverse the order of pin 2 and 3 (send pin 2 onto pin 3 and pin 3 onto pin 2) while keeping pin 5 onto pin 5.
Make sure the baudrate is set to the correct value
@author: pfduc
"""


#!/usr/bin/env python
import numpy as np
import time
import random
try:
    from . import Tool
except:
    import Tool
    
from struct import pack, unpack


"""
when I ask from the terminal it accepts the command i.read(), I can send i.write("*IDN?") followed by i.read(), it also works from the file.close
But it doesn't work with acquire...

It actually works,

Now it seems the problem is with the trigger, I should try the option with the delay trigger...

I connected with serial and it works,

the time needed to fetch the data is about 1.6 second and it seems low to me I will see what I can do for that.


"""

param = {'CH1': 'V', 'CH2': 'V', 'phase': 'deg', 'Z': 'Ohm', 'Z2': 'Ohm'}

INTERFACE = Tool.INTF_SERIAL

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'GDS820C', debug=debug,
                                         interface=INTERFACE, baud_rate=38400,
                                         term_chars="\n", timeout=2, bytesize=8,
                                         parity='N', stopbits=1, xonxoff=False, 
                                         dsrdtr=False, **kwargs)

        if not self.DEBUG:
            print("init done")
            print(self.ask("*IDN?"))        
            # initialise the volt per div
            self.volt_per_div = {1: [], 2: []}
            self.get_channel_scale(1)
            self.get_channel_scale(2)
            self.time_per_div = self.get_time_scale()
            self.waveform = {1: [], 2: []}
            self.param_id = {'CH1': 1, 'CH2': 2}
            self.latest_data = ""
            self.get_channel_scale()
            self.phase = 0
            self.impedance = 0
            self.impedance2 = 0

        self.scales = np.array(
            [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1., 2., 5.])

    def measure(self, channel='CH1'):
        if channel in self.last_measure:
            if not self.debug:
                if channel == 'phase':
                    answer = self.phase
                elif channel == 'Z':
                    answer = self.impedance
                elif channel == 'Z2':
                    answer = self.impedance2
                else:
                    # 0 #this is to be defined for record sweep
                    answer = self.ask(':READ?')
                    answer = float(answer.split(',', 1)[0])

            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def acquire_spectrum(self, channel='CH1'):
        print(channel)

        chan_num = self.param_id[channel]

        if not self.debug:
            self.get_raw_data(chan_num)
            return self.waveform[chan_num] * self.volt_per_div[chan_num]
        else:
            print("pas prout")
            return [random.random() for i in range(1000)]

    def get_settings(self):
        print(self.ask("*LRN?"))

    def get_phase(self):
        return self.phase

    def set_phase(self, phase):
        self.phase = phase

    def wait(self):
        """
        Prevents the programming instrument from executing further commands or
        queries until all pending operations finish.
        """
        self.write("*WAI")

    def set_average(self, n):
        """
        Select the average number of waveform acquisition. The range for averaging is
        from 2 to 256 in powers of 2.
        """
        print("im in set average")
        if n < 1 or n > 8:
            print("%s : set_average : input argument needs to be an integer between 1 and 8\n" % (self.ID_name))
        else:
            self.write(":ACQ:AVER %i" % (n))

    def set_length(self, L):
        """
        Select the number of record length. This oscilloscope provides record length of
        500, 1250, 2500, 5000, 12500, 25000, 50000, and 125000.
        """
        lengthes = [500, 1250, 2500, 5000, 12500, 25000, 50000, 125000]
        if not L in lengthes:
            print("%s : set_length : input argument needs to be an integer in the list:\n[500, 1250, 2500, 5000, 12500, 25000, 50000,125000]\n" % (self.ID_name))
        else:
            print("set 2 :", lengthes.index(L))
            self.write(":ACQ:LENG %i" % (lengthes.index(L)))
            self.wait()

    def get_length(self):
        """
        Return the number of record length. This oscilloscope provides record length of
        500, 1250, 2500, 5000, 12500, 25000, 50000, and 125000.
        """
        return float(self.ask(":ACQ:LENG?"))

    def set_mode(self, i):
        """
        Select the waveform acquisition mode. There are four different acquisition mode:
        sample (0), peak detection(1), average(2) and accumulate (this one wasn't present in the manual).
        """
        if not i in [0, 1, 2]:
            print("%s : set_mode : input argument needs to be an integer between 0 and 2\n" % (self.ID_name))
        else:
            self.write(":ACQ:MOD %i" % (i))
            self.wait()

    def get_mode(self):
        """
        Return the waveform acquisition mode. There are four different acquisition mode:
        sample (0), peak detection(1), average(2) and accumulate (this one wasn't present in the manual).
        """
        return self.ask(":ACQ:MOD?")

    def get_mode_meaning(self):
        """
        Return the waveform acquisition mode. There are four different acquisition mode:
        sample (0), peak detection(1), average(2) and accumulate (this one wasn't present in the manual).
        """
        answers = ["sample", "peak detection", "average", "accumulate"]
        return answers[int(self.ask(":ACQ:MOD?"))]

    def get_pp_voltage(self, chan_num):
        """
        Return the average voltage of a given channel of the scope.
        """
        if not chan_num in [1, 2]:
            print("%s : get_displayed_data : input argument needs to be an integer between 1 and 2\n" % (self.ID_name))
            return 0
        else:
            self.write(":MEAS:SOUR %i" % (chan_num))
            self.wait()
            answer = self.ask(":MEAS:VAMP?")
            if answer[-2:] == "mV":
                answer = float(answer[:-2]) / 1000.
            elif answer[-1:] == "V":
                answer = float(answer[:-1])
            else:
                return self.get_pp_voltage(chan_num)
            return answer

    def get_peak_voltage(self, chan_num):
        """
        Return the average voltage of a given channel of the scope.
        """
        if not chan_num in [1, 2]:
            print("%s : get_displayed_data : input argument needs to be an integer between 1 and 2\n" % (self.ID_name))
            return 0
        else:
            answer = self.get_pp_voltage(chan_num)

            cur_scale = self.get_channel_scale(chan_num)
            if answer == 0.0:

                #                print "cur",cur_scale
                if cur_scale >= max(self.scales):
                    print(("%s : get_peak_voltage : the voltage scale is already %.3fV per div, you cannot go higher than that \n" % (
                        self.ID_name, max(self.scales))))
                else:
                    print(("%s : get_peak_voltage : the voltage is above the scale range : optimization... \n" % (
                        self.ID_name)))
#                    print np.squeeze(np.where(self.scales==cur_scale))
                    new_scale = self.scales[np.squeeze(
                        np.where(self.scales == cur_scale)) + 1]
#                    print "new",new_scale
                    self.set_channel_scale(chan_num, new_scale)
                    return self.get_peak_voltage(chan_num)
            else:

                best_scale = self.scales[
                    np.min(np.where(answer / self.scales <= 8))]

                if cur_scale == best_scale:
                    return answer
                else:
                    self.set_channel_scale(chan_num, best_scale)
                    return self.get_peak_voltage(chan_num)

#            for s in self.scales:
#                print s,answer/s

    def get_block_data(self):
        """
        Transfer the displayed waveform data from the oscilloscope memory into the variable self.latest_data
        """
#        print "yolo1"

        self.latest_data = self.read(10)
#        print "yolo324211"
        length = len(self.latest_data)
#        print "The length is %i"%(length)
        if not length == 10:
            print("The data wasn't triggered")
            return 0

        self.headerlen = 2 + int(self.latest_data[1])
        print("The headerlength is %i" % (self.headerlen))
        pkg_length = int(self.latest_data[2:self.headerlen]) + self.headerlen
        print("Data transferring...  ")
        print(pkg_length)
        pkg_length = pkg_length - length
        while True:
            print('%8d\r' % pkg_length)
            if(pkg_length > 100000):
                try:
                    buf = self.read(100000)
                except:
                    print('KeyboardInterrupt!')
                    exit()
                num = len(buf)
                self.latest_data += buf
                pkg_length = pkg_length - num
            else:
                try:
                    buf = self.read(pkg_length)
                except:
                    print('KeyboardInterrupt!')
                    exit()
                num = len(buf)
                self.latest_data += buf
                pkg_length = pkg_length - num
                if(pkg_length == 0):
                    break
#                    print('%8d\r' %pkg_length),
        return 1

    def get_raw_data(self, chan_num):
        """
        Transfer the displayed waveform data from the oscilloscope.
        """
#        data_points=None
        if not chan_num in [1, 2]:
            print("%s : get_displayed_data : input argument needs to be an integer between 1 and 2\n" % (self.ID_name))
        else:

            have_data = 0
            while have_data == 0:
                self.write(":ACQ%i:MEM?" % (chan_num))
                print("sent command")
                have_data = self.get_block_data()

            # Number of sample points.
            self.points_num = len(self.latest_data[self.headerlen + 8:]) / 2

            # Get sample rate from header.
            sample_rate = unpack(">f", self.latest_data[
                                 self.headerlen:self.headerlen + 4])
#            print('Sample rate: %f SPS' %sample_rate[0])

            self.time_per_div = 1 / sample_rate[0]

            # Convert hex to int.
            self.waveform[chan_num] = np.array(unpack('>%sh' % (len(self.latest_data[
                                               self.headerlen + 8:]) / 2), self.latest_data[self.headerlen + 8:]))
#            print ('Number of samples: %d' %len(self.waveform[chan_num]))

#        return ch #Return the buffer index.

    def set_channel_coupling(self, chan_num, i):
        """
        Select the different coupling states for the oscilloscope.
        Place scope in AC coupling state(0) Place scope in DC coupling state(1), Place scope in grounding state(2)
        """
        if not chan_num in [1, 2]:
            print("%s : set_channel_coupling : chan_num needs to be an integer between 1 and 2\n" % (self.ID_name))
        else:
            if not i in [0, 1, 2]:
                print("%s : set_channel_coupling : input argument needs to be an integer between 0 and 2\n" % (self.ID_name))
            else:
                data_string = self.write(":CHAN%i:COUP %i" % (chan_num, i))
            # process data_string

    def get_channel_coupling(self, chan_num):
        """
        Return the different coupling states for the oscilloscope.
        Place scope in AC coupling state(0) Place scope in DC coupling state(1), Place scope in grounding state(2)
        """
        if not chan_num in [1, 2]:
            print("%s : set_channel_coupling : chan_num needs to be an integer between 1 and 2\n" % (self.ID_name))
        else:
            return self.ask(":CHAN%i:COUP?" % (chan_num))

    def set_trigger_source(self, trig_source):
        """
        Select the trigger source.
        """
        sources = ["CH1", "CH2", "EXT", "AC"]
        if trig_source in sources:
            self.write(":TRIG:SOUR %i" % (sources.index(trig_source)))
        else:
            if trig_source in [1, 2]:
                self.write(":TRIG:SOUR %i" % (trig_source))
        self.wait()

    def get_trigger_source(self, name=False):
        """
        Query the trigger source, it could be channel 1, channel 2, external trigger and AC line voltage
        """
        sources = ["CH1", "CH2", "EXT", "AC"]
        answer = self.ask(":TRIG:SOUR?")
        if name:
            return sources[int(answer)]
        else:
            return answer

    def set_trigger_mode(self, trig_mode):
        """
        Select the trigger mode.
        """
        modes = ["Auto Level", "Auto", "Normal", "Single"]
        if trig_mode in modes:
            self.write(":TRIG:MOD %i" % (modes.index(trig_mode)))
        else:
            if trig_mode in [1, 2]:
                self.write(":TRIG:MOD %i" % (trig_mode))
        self.wait()

    def get_trigger_mode(self, name=False):
        """
        Query the trigger mode, it could be auto level, auto, normal, single
        """
        modes = ["Auto Level", "Auto", "Normal", "Single"]
        answer = self.ask(":TRIG:MOD?")
        if name:
            return types[int(answer)]
        else:
            return answer

    def set_trigger_type(self, trig_type):
        """
        Select the trigger type.
        """
        types = ["Edge", "Video", "Pulse", "Delay"]
        if trig_type in types:
            self.write(":TRIGger:TYPe %i" % (types.index(trig_type)))
        else:
            if trig_type in [1, 2]:
                self.write(":TRIGger:TYPe %i" % (trig_type))
        self.wait()

    def get_trigger_type(self, name=False):
        """
        Query the trigger type, it could be Edge, Video, Pulse or Delay
        """
        types = ["Edge", "Video", "Pulse", "Delay"]
        answer = self.ask(":TRIG:TYP?")
        if name:
            return types[int(answer)]
        else:
            return answer

    def get_channel_coupling_meaning(self, chan_num):
        """
        Return the different coupling states for the oscilloscope.
        Place scope in AC coupling state(0) Place scope in DC coupling state(1), Place scope in grounding state(2)
        """
        answers = ["AC", "DC", "ground"]
        if not chan_num in [1, 2]:
            print("%s : set_channel_coupling : chan_num needs to be an integer between 1 and 2\n" % (self.ID_name))
        else:
            return answers[int(self.ask(":CHAN%i:COUP?" % (chan_num)))]

    def set_channel_scale(self, chan_num, scale):
        """
        Sets the vertical scale of the specified channel.
        """
        if not chan_num in [1, 2]:
            print("%s : set_channel_scale : chan_num needs to be an integer between 1 and 2\n" % (self.ID_name))
        else:

            if not scale in self.scales:
                print("%s : set_channel_scale : input argument needs to be a float in the list  in the list:\n[0.002,0.005,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5]\n" % (self.ID_name))
            else:
                self.write(":CHAN%i:SCAL %.3f" % (chan_num, scale))
                # update the value of volt_per_div
                self.get_channel_scale(chan_num)

    def get_channel_scale(self, chan_num=None):
        """
        Query the vertical scale of the specified channel. Give the answer in volts.
        """
#        [0.002:0.002,0.01:0.01,0.1:0.1,1:1,0.005:2,0.02:20,0.2:200,2:2,0.05:50,0.5:500,5:5V]

        if chan_num == None:
            self.get_channel_scale(1)
            self.get_channel_scale(2)
        elif not chan_num in [1, 2]:
            print("%s : get_channel_scale : chan_num needs to be an integer between 1 and 2\n" % (self.ID_name))
        else:
            answer = ""
            while answer == "":
                answer = self.ask(":CHAN%i:SCAL?" % (chan_num))
#            print answer
#            print answer[:-1]
            if answer[-2:] == "mV":
                answer = float(answer[:-2]) / 1000.
            else:
                answer = float(answer[:-1])
            self.volt_per_div[chan_num] = answer / 25.
            return answer

    def get_time_scale(self):
        """
        Query the horizontal scale give the answer in seconds.
        """
#        [0.002:0.002,0.01:0.01,0.1:0.1,1:1,0.005:2,0.02:20,0.2:200,2:2,0.05:50,0.5:500,5:5V]
        answer = ""
        while answer == "":
            answer = self.ask(":TIM:SCAL?")

        if answer[-2:] == "ms":
            answer = float(answer[:-2]) * 1e-3
        elif answer[-2:] == "us":
            answer = float(answer[:-2]) * 1e-6
        elif answer[-2:] == "ns":
            answer = float(answer[:-2]) * 1e-9
        else:
            answer = float(answer[:-2])
        return answer

    def status(self):
        """
        Query of the Status Byte register (SBR) with *STB? will return a decimal number
        representing the bits that are set (true) in the status register.
        """
        return self.ask("*STB?")

    def run(self):
        """
        Controls the RUN state of trigger system. The acquisition cycle will follow each
        qualified trigger in the RUN state.
        """

        self.write(":RUN")
        self.wait()

    def stop(self):
        """
        Controls the STOP state of trigger system. The acquisition cycle only triggered
        when the :RUN command is received.
        """

        self.write(":STOP")

    def plot_data(self, chan_num=1, average=0):
        """
        This function set the average aquisition number and collects the signal from the scope, transforming it into volts and time
        The average number should be between 1 and 8 (it represents powers of 2) and the channel number should be indicated
        """
        if not (average == 0 or average == 1):
            # Set
            self.set_average(average)
            self.set_mode(2)
        else:
            #            pass
            self.set_mode(0)

        self.get_raw_data(chan_num)  # *self.get_channel_scale(chan_num)

        x = np.arange(len(self.waveform[chan_num])) * self.time_per_div
        plt.plot(x, self.waveform[chan_num] * self.volt_per_div[chan_num])


def read_data(file_name):
    data_file = open(file_name, 'r')
    lines = data_file.readlines()

    # sets the time scale
    dt = float(lines[0].split(":")[1])
    # deletes first two lines from the buffer because they are of diff format
    del lines[0:2]

#    phase_shifts = []
    Z = []
    freq = []
    phase = []
    for element in lines:
        raw_data = element.split(", ")

        freq.append(float(raw_data[1]))
#        period = 1 / frequency
        data_CH1 = raw_data[2:502]  # channel 1 data is from 2nd to 501st
        data_CH2 = raw_data[502:1002]  # channel 2 data is from 502nd to 1001st

        ch1 = []
        ch2 = []

        for i, x, y in zip(list(range(len(data_CH1))), data_CH1, data_CH2):

            ch1.append(float(x))
            ch2.append(float(y))
#        print data_CH2

        ch1 = np.array(ch1)
        ch2 = np.array(ch2)
        Z.append(np.max(ch1) / np.max(ch2))
#        print np.max(ch1)
#        t=np.arange(len(ch1))*dt
#        f = np.fft.fftfreq(t.shape[-1])
#        phase.append(np.angle(np.fft.fft(ch1))-np.angle(np.fft.fft(ch2)))
        phase.append(np.arccos(np.dot(ch1, ch2) /
                               np.sqrt(np.dot(ch1, ch1) * np.dot(ch2, ch2))))
#        plt.plot(np.abs(np.fft.fft(ch1)),'r')
#        plt.hold(True)
#        plt.plot(np.abs(np.fft.fft(ch2)))
#        plt.show()

#        max_CH1 = max(data_CH1)
#        max_CH2 = max(data_CH2)
#
#        time_maxCH1 = data_CH1.index(max_CH1) * time_division
#        time_maxCH2 = data_CH2.index(max_CH2) * time_division
#        delta_t= np.abs(time_maxCH2 - time_maxCH1)
#
#        phase = (delta_t % period) / period * np.pi * 2
#        phase_shifts.insert(frequency, phase)

#    phase_file = open("phase_data.csv", "w")
#    for item in phase_shifts:
#        phase_file.write("%d, %d" % (phase_shifts.index(item), item))
    phase = np.array(phase)
    fig = plt.figure()
    ax = fig.add_subplot(111)


#   create a second axis
    ax2 = ax.twinx()
    ax.plot(phase * 180 / np.pi, 'r')
    plt.hold(True)
    ax2.plot(Z)
#    print freq
    plt.show()

if __name__ == "__main__":

    #    read_data("C:/Users/pfduc/Documents/g2gui/g2python/20150409_Freq_sweep_pressure6.00e-04_rawdata.dat")

    #    omega=2*np.pi*500000
    #    phi=(np.sqrt(2)/2)*np.pi
    #    print phi
    #    T=1/500000.
    #    print T
    #    t=np.arange(0,T/2,1e-10)
    #    s1=np.sin(omega*t)
    #    s2=np.sin(omega*t+phi)
    #    plt.plot(t,s1,'r',t,s2,'b')
    #
    #    print np.arccos(np.dot(s1,s2)/np.sqrt(np.dot(s1,s1)*np.dot(s2,s2)))
    #    plt.plot(np.abs(np.angle(np.fft.fft(s1)[1:])-np.angle(np.fft.fft(s2)[1:])))
    #    plt.show()
    #    i=Instrument("COM3",debug=False)
    #
    ##    import serial
    #
    #    i=serial.Serial("COM4",38400,timeout=1)
    # i.write("*IDN?\n")
    # print i.read()
    # bigger_t=[]
    #    ts=time.time()
    # y=self.acquire_data(chan_num)#*self.get_channel_scale(chan_num)
    #    print i.get_time_scale()
    #    print i.get_channel_scale(1)
    #    print i.get_channel_scale(2)
    #
    # i.get_raw_data(1)
    #
    #    plt.plot(i.acquire_spectrum("CH1"))
    #    plt.plot(i.acquire_spectrum("CH2"))
    #    plt.show()

    #    i.plot_data(2,4)
    #    for n in [4,5,7]:
    #        print n+1,'\n'
    #        dt=np.array([])
    #        for j in range(5):
    #            ts=time.time()
    #            i.plot_data(1,n+1)
    #            dt=np.append(dt,time.time()-ts)
    #            print time.time()-ts
    #        print [np.average(dt),np.std(dt)]
    #        bigger_t.append([np.average(dt),np.std(dt)])
    #
    #    bigger_t=np.array(bigger_t)
    #    print bigger_t
    #    plt.show()

    #    [[ 1.60879998  0.02321546]
    # [ 1.60939999  0.0406576 ]
    # [ 1.61860003  0.02335464]
    # [ 1.61239996  0.03181566]]
    #[[ 1.62460003  0.03182209]
    # [ 1.5994      0.04796072]
    # [ 1.61599998  0.02704064]
    # [ 1.57340002  0.01205988]]

    i = Instrument("COM4", debug=False)
#    print i.acquire_spectrum()
    print(i.ask("*IDN?"))
#    print i.get_peak_voltage(1)
#    print i.get_peak_voltage(2)
#    Nav = 10
#    i.set_length(500)
#    print i.get_length()
#
#    data_CH1 = np.ones((Nav, i.get_length()))
#    data_CH2 = np.ones((Nav, i.get_length()))
#
#    for j in range(Nav):
#        print("Loop number %i\n" % (j + 1))
#        print "\nacq spec 1"
#        data_CH1[j, :] = i.acquire_spectrum("CH1")
#        print "\nacq spec 2"
#        data_CH2[j, :] = i.acquire_spectrum("CH2")
#        print "acq done"
#
#    data_CH1 = np.average(data_CH1, 0)
#    data_CH2 = np.average(data_CH2, 0)
##    print i.set_channel_scale(2,0.05)
#
#    Z = (i.get_peak_voltage(1) / i.get_peak_voltage(2))
#    Z2 = (np.max(data_CH1) / np.max(data_CH2))
##        print np.max(ch1)
##        t=np.arange(len(ch1))*dt
##        f = np.fft.fftfreq(t.shape[-1])
##        phase.append(np.angle(np.fft.fft(ch1))-np.angle(np.fft.fft(ch2)))
#    phase = (np.arccos(np.dot(data_CH1, data_CH2) /
#                       np.sqrt(np.dot(data_CH1, data_CH1) * np.dot(data_CH2, data_CH2))))
##        plt.plot(np.abs(np.fft.fft(ch1)),'r')
#
#
##    datai.get_data(1)
##
#    print Z, Z2, phase
#    plt.plot(data_CH1)
#    plt.hold(True)
#    plt.plot(data_CH2, 'r')
#
#    plt.show()
#
###
###
###
###
##    plt.plot(i.get_data(1))
## plt.hold(True)
## plt.plot(i.get_displayed_data(2),'r')
##    plt.show()
    i.close()

 #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
