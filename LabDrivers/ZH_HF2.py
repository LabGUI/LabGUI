#!/usr/bin/env python
#import visa
from . import Tool
import numpy as np
import time
from collections import OrderedDict
try:
    import zhinst.ziPython
    import zhinst.utils
    import zhinst.utils as utils
    import zhinst.ziPython as ziPython
except:
    pass
#print("Zurich Instruments drivers unavailable")
# use an ordered dictionary so that the parameters show up in a pretty order :)
param = OrderedDict([('X', 'V'), ('Y', 'V'), ('X2', 'V'),
                     ('Y2', 'V'), ('X3', 'V'), ('Y3', 'V')])

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):
    def __init__(self, name, debug=False):
        super(Instrument, self).__init__(
            None, name='ZH_HF2', debug=debug, interface=INTERFACE)
        # self.ID_name=name
       # self.debug=debug
       # self.resource_name = name

        if name != 'default':

            #            module_name=import_module("."+name,package=LABDRIVER_PACKAGE_NAME)
            #            else:
            #                module_name=import_module("."+name,package=LABDRIVER_PACKAGE_NAME)
            self.channels = []
            for chan, u in list(param.items()):
                # initializes the first measured value to 0 and the channels' names
                self.channels.append(chan)
                self.units[chan] = u
                self.last_measure[chan] = 0
                self.channels_names[chan] = chan

            if not self.DEBUG:
                self.daq = zhinst.ziPython.ziDAQServer('localhost', 8005)

    def measure(self, channel):

        if channel in param:
            if channel == 'X':
                sample = self.get_sample('/dev855/demods/0/sample')
                answer = sample['x'][0]
            elif channel == 'Y':
                sample = self.get_sample('/dev855/demods/0/sample')
                answer = sample['y'][0]
            elif channel == 'X2':
                sample = self.get_sample('/dev855/demods/1/sample')
                answer = sample['x'][0]
            elif channel == 'Y2':
                sample = self.get_sample('/dev855/demods/1/sample')
                answer = sample['y'][0]
            elif channel == 'X3':
                sample = self.get_sample('/dev855/demods/2/sample')
                answer = sample['x'][0]
            elif channel == 'Y3':
                sample = self.get_sample('/dev855/demods/2/sample')
                answer = sample['y'][0]
            self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def get_sample(self, stri):
        if not self.DEBUG:
            try:
                return self.daq.getSample(stri)
            except:
                time.sleep(0.1)
                print ("Zurich has died for a moment!")
                return self.daq.getSample(stri)
        else:
            return np.random.random()


class ScopeAveraging(object):

    def __init__(self):
        # Open connection to ziServer
        # daq = zhinst.ziPython.ziDAQServer('localhost', 8005)
        # Create an instance of the ziDiscovery class.
        d = ziPython.ziDiscovery()

        # Determine the device identifier from it's ID.
        self.device = d.find('dev855').lower()

        # Get the device's default connectivity properties.
        props = d.get(self.device)
        apilevel = 1
        self.daq = ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)


    def get_and_save_data(self, output_file):
        # Record one demodulator sample from the specified node

        sample = self.daq.getSample('/dev855/demods/0/sample')
        data = [time.time(), amp, freq, DC, sample['x'][0], sample['y'][0], T]
        output_file.write(', '.join([str(s) for s in data]) + '\n')
        output_file.flush()
        print(', '.join([str(s) for s in data]))

    def sample_scope(self, device_id, num_samples=1, poll_length=5):
        # See the LabOne Programming Manual for an explanation of API levels.

        # Create a connection to a Zurich Instruments Data Server (an API session)
        # using the device's default connectivity properties.

        # Check that the device is visible to the Data Server
        if self.device not in utils.devices(self.daq):
            raise RuntimeError("The specified device `%s` is not visible to the Data Server, " % device_id + \
                               "please ensure the device is connected by using the LabOne User Interface. " + \
                               "or ziControl (HF2 Instruments).")

        # create a base configuration: disable all outputs, demods and scopes
        general_setting = [
            ['/%s/demods/*/rate' % self.device, 0],
            ['/%s/demods/*/trigger' % self.device, 0],
            ['/%s/sigouts/*/enables/*' % self.device, 0],
            ['/%s/scopes/*/trigchannel' % self.device, -1]]
        self.daq.set(general_setting)

        # The scope's sampling rate is configured by specifying the ``time`` node
        # (/devN/scopes/0/time). The rate is equal to 210e6/2**time, where 210e6 is
        # the HF2 ADC's sampling rate (^=clockbase, /devX/clockbase). time is an
        # integer in range(0,16).
        #
        # Since the length of a scope shot is fixed (2048) on an HF2, specifying the
        # rate also specifies the time duration of a scope shot,
        # t_shot=2048*1./rate=2048*2**time/210e6.
        #
        # Therefore, if we would like to obtain (at least) 10 periods of the signal
        # generated by Oscillator 1, we need to set the scope's time parameter as
        # following:
        clockbase = float(self.daq.getInt('/%s/clockbase' % self.device))  # 210e6 for HF2 (210 MSa/s)
        desired_t_shot = 8e-5
        scope_time = np.ceil(np.max([0, np.log2(clockbase * desired_t_shot / 2048.)]))
        if scope_time > 15:
            scope_time = 15
            warnings.warn("Can't not obtain scope durations of %.3f s, scope shot duration will be %.3f." \
                          % (desired_t_shot, 2048. * 2 ** scope_time / clockbase))
        print("Will set /%s/scopes/0/time to %d." % (self.device, scope_time))
        # Now set the settings relevant to this experiment. Note: Since we're taking
        # scope data from the signal outputs, we don't configure the signal inputs.
        exp_setting = [
            ['/%s/scopes/0/channel' % (self.device), 0],  # 2 ^= Signal Output 1
            ['/%s/scopes/0/triglevel' % (self.device), 0.0],
            ['/%s/scopes/0/trigholdoff' % (self.device), 0],
            # Enable bandwidth limiting: avoid antialiasing effects due to
            # subsampling when the scope sample rate is less than the input
            # channel's sample rate.
            ['/%s/scopes/0/bwlimit' % (self.device), 1],
            ['/%s/scopes/0/time' % (self.device), scope_time],  # set the sampling rate
            ['/%s/scopes/0/trigchannel' % (self.device), 1]]
        self.daq.set(exp_setting)

        # Perform a global synchronisation between the device and the data server:
        # Ensure that 1. the settings have taken effect on the device before issuing
        # the poll() command and 2. clear the API's data buffers.

        averages = []
        for i in range(num_samples):
            # Subscribe to the scope data
            path = '/%s/scopes/0/wave' % (self.device)
            test = False
            while not test:
                try:
                    self.daq.sync()
                    self.daq.subscribe(path)

                    poll_timeout = 500  # [ms]
                    poll_flags = 0
                    poll_return_flat_dict = True
                    data = self.daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)
                    # Unsubscribe from all paths
                    self.daq.unsubscribe('*')

                    # Check the dictionary returned is non-empty
                    assert data, "poll(%s) returned an empty data dictionary, scope's trigger criteria not violated?" % (
                            i + 1)
                    keypath = False
                    if not keypath:
                        try:
                            # Note, the data could be empty if no data arrived, e.g., if the scope was disabled
                            assert path in data, "data dictionary has no key '%s'" % path
                            # The data returned by poll is a dictionary whose keys correspond to the
                            # subscribed node paths. Looking up a key in the dictionary returns the data
                            # associated with that node.
                            shots = data[path]
                            keypath = True
                        except KeyError:
                            print("data dictionary has no key '%s'" % path)
                            time.sleep(60)
                    # The scope data polled from the node /devN/scopes/0/wave, here ``shots``,
                    # is a list of dictionaries; the length of ``shots`` is the number of scope
                    # shots that were returned by poll().
                    print("poll(%s) returned %i scope shots." % (i + 1, len(shots)))
                    assert len(shots) >= 0, "len(data[%s]) is 0: no scope shots." % path
                    test = True
                except AssertionError:
                    print(
                        "ERORR! poll(%s) returned an empty data dictionary, scope's trigger criteria not violated?" % (
                                    i + 1))
                    self.daq.setInt('/%s/scopes/0/trigchannel' % self.device, -1)
                    time.sleep(60)
                    self.daq.setInt('/%s/scopes/0/trigchannel' % self.device, 1)

                    # In order to obtain the physical value of the wave we need to scale
            # accordingly:
            happy = False
            while not happy:
                try:
                    sigins_range_set = self.daq.getDouble('/%s/sigins/0/range' % self.device)
                    happy = True

                except RuntimeError:
                    print("Zurich does not respond again! Waiting for a miracle...")
                    time.sleep(60)

            scale = sigins_range_set / (2 ** 15)  # The scope's wave are 16-bit integers

            # for shot in shots:
            #    t = np.linspace(0, shot['dt']*len(shot['wave']), len(shot['wave']))
            # plt.plot(t, scale*shot['wave'])
            t = np.linspace(0, shots[0]['dt'] * len(shots[0]['wave']), len(shots[0]['wave']))
            # print len([shot['wave'] for shot in shots])
            memoryerror = False
            while not memoryerror:
                try:
                    averaged_shots = scale * np.average(np.vstack([shot['wave'] for shot in shots]), 0)
                    averages.append(averaged_shots)
                    memoryerror = True
                except MemoryError:
                    print("Zurich has memmory issues! Let us wait for 60 seconds...")
                    time.sleep(60)

            # plt.plot (t, averaged_shots)

        # Disable the scope
        self.daq.setInt('/%s/scopes/0/trigchannel' % self.device, -1)
        return [t, np.average(np.vstack(averages), 0)]

    def save_trace(self, filename='test', samples=1, length=5):
        """
        This function plots and save the scope data acquired via Zurich.
        """
        data = sample_scope('dev855', samples, length)
        fig = figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(data[0] * 1e6, data[1] * 1e3)
        ax.set_xlabel(r'Time ($\mu$s)')
        ax.set_ylabel(r'Voltage (mV)')
        savefig(fpath + "Zurich_Raw_Data_Plots/" + filename + ".pdf", format='pdf', dpi=2400)
        close(fig)
        sys.stdout.write('\nSaving data to ' + filename + '.txt\n')
        np.savetxt(fpath + "Zurich_Raw_Data_Plots/" + filename + ".txt", np.vstack([data[0], data[1]]).T)
        return data




# Plan to move to using Instrument as the name within, but for back-compatibility
# include this (so you can still use SRS830.SRS830 instead of SRS830.Instrument)
#SRS830 = Instrument

    # if run as own program
    # if (__name__ == '__main__'):

     #   lockin = device('dev9')
     #   lockin.set_ref_internal  # no averaging
     #   lockin.close()
