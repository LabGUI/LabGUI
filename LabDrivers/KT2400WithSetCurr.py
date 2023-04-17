# -*- coding: utf-8 -*-
"""
Created on Wed May 28 2019
Keithley 2400
@author: zackorenberg

=== TO MAINTAIN BACKWARDS COMPATIBILITY ===
When writing a function that requires the ':READ?' command, use:

self.ask(self.READ)

instead of

self.ask(':READ?')

"""

#!/usr/bin/env python
import time

import random
try:
    from . import Tool
except:
    import Tool

import math
import numpy as np
import time

param = {'V': 'V', 'I': 'A'}

plot = ['Time(s)', 'Voltage(V)', 'Current(A)']
functions = {
    "Voltage Pulse Sweep":[
        { # parameter 1
            'name': 'Pulses',
            'type': 'int',
            'range':[0, 1000],
            'required': True,
            'units':'#'
        },
        { # parameter 2
            'name':'Start',
            'type':'float',
            'range':[-120, 120],
            'required': True,
            'units': 'V'
        },
        { # parameter 3
            'name':'Stop',
            'type':'float',
            'range':[-120, 120],
            'required': True,
            'units': 'V'
        },
        { # parameter 4
            'name':'Pulse Width',
            'type':'float',
            'range':[0, 120],
            'required': True,
            'units': 's'
        },
        { # parameter 5
            'name':'Pulse Delay',
            'type':'float',
            'range':[0, 120],
            'required': True,
            'units': 's'
        },
        { # parameter 5.5
            'name':'Baseline',
            'type':'float',
            'range':[0, 120],
            'required': False,
            'units': 'V'
        },
        {
            'name':'Frequency of Readings',
            'type':'float',
            'range':[0, 120],
            'required': False,
            'units': 's',
            'default':0.2
        }, # parameter 6
        {
            'name':'Direction',
            'type':'selector',
            'range':['UP','DOWN','BOTH'],
            'required': False,
            'default':'BOTH'
        }, # parameter 7
        { # parameter 8
            'name':'VCompliance',
            'type':'float',
            'range':[0, 120],
            'required': False,
            'units': 'V',
            'default':1
        },
        { # parameter 9
            'name':'ICompliance',
            'type':'float',
            'range':[0, 1],
            'required': False,
            'units': 'A',
            'default':1e-7
        },
    ],
    "Voltage Staircase Sweep":[
        { # parameter 1
            'name': 'Steps',
            'type': 'int',
            'range':[0, 1000],
            'required': True,
            'units':'#'
        },
        { # parameter 2
            'name':'Start',
            'type':'float',
            'range':[-120, 120],
            'required': True,
            'units': 'V'
        },
        { # parameter 3
            'name':'Stop',
            'type':'float',
            'range':[-120, 120],
            'required': True,
            'units': 'V'
        },
        { # parameter 4
            'name':'Step Width',
            'type':'float',
            'range':[0, 120],
            'required': True,
            'units': 's'
        },
        { # parameter 5
            'name':'Frequency of Readings',
            'type':'float',
            'range':[0, 120],
            'required': False,
            'units': 's'
        }, # parameter 6
        {
            'name':'Direction',
            'type':'selector',
            'range':['UP','DOWN','BOTH'],
            'required': False
        }, # parameter 7
        { # parameter 8
            'name':'VCompliance',
            'type':'float',
            'range':[0, 120],
            'required': False,
            'units': 'V'
        },
        { # parameter 9
            'name':'ICompliance',
            'type':'float',
            'range':[0, 1],
            'required': False,
            'units': 'A'
        },
    ]
}


INTERFACE = Tool.INTF_GPIB


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, backwardcompatible=True, **kwargs):

        if "interface" in kwargs:
            itfc = kwargs.pop("interface")
        else:
            itfc = INTERFACE

        name = 'KT2400'
        if "name" in kwargs:
            name = kwargs.pop("name")



        super(Instrument, self).__init__(resource_name,
                                         name=name,
                                         debug=debug,
                                         interface=itfc,
                                         **kwargs)
        self.READ = ":READ?"
        if backwardcompatible:
            # make sure that if model 2450, to change language
            answer = self.ask("*IDN?")
            if "MODEL 2450" in answer:
                lang = self.ask("*LANG?")
                if "SCPI2400" not in lang:
                    self.write("*LANG SCPI2400")
                    print("=== Please reboot device ===")
        else:
            self.READ = ':READ? "defbuffer1", SOUR, READ'
        self.enable_output()

    def measure(self, channel):
        if channel in self.last_measure:

            if channel == 'V':
                if not self.DEBUG:
                    # 0 #this is to be defined for record sweep
                    self.write('VOLT:RANG 10')# Never use auto range (:AUTO ON) when measuring voltage only
                    answer = self.ask(self.READ)
                    #if math.isnan(float(answer)):
                    if not answer or answer=='\n': #incase 2450 is connected
                        self.enable_output()
                        return self.measure(channel)
                    elif type(answer) is not str and math.isnan(answer): #answer will be nan if error
                        # case where 2400 is connected but output is off
                        print("Output must be enabled")
                        self.enable_output()
                        return self.measure(channel)
                        #print("Please set Output on")
                        #answer = float(answer)
                    else:
                        answer = float(answer.split(',')[0])
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'I':
                if not self.DEBUG:
                    # 0 #this is to be defined for record sweep
                    self.write('CURR:RANG:AUTO ON')
                    answer = self.ask(self.READ)
                    #if math.isnan(float(answer)):
                    if not answer or answer=='\n': #incase 2450 is connected
                        self.enable_output()
                        return self.measure(channel)
                    elif type(answer) is not str and math.isnan(answer): #answer will be nan if error
                        # case where 2400 is connected but output is off
                        print("Output must be enabled")
                        self.enable_output()
                        return self.measure(channel)
                        #print("Please set Output on")
                        #answer = float(answer)
                    else:
                        answer = float(answer.split(',')[1])
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

        # Should Read KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx,
        # yyyyy/zzzzz /a/d

    def run(self, channel, arguments):
        #print(channel)
        if channel == 'Voltage Pulse Sweep':
            items = arguments.items()
            params = {}
            names_switch = {
                'Pulses':'pulses',
                'Start':'start',
                'Stop':'stop',
                'Pulse Width':'pulse_width',
                'Pulse Delay':'pulse_delay',
                'Baseline':'base',
                'Frequency of Readings':'frequency',
                'Direction':'direction',
                'VCompliance':'v_compliance',
                'ICompliance':'i_compliance'
            }
            #print(items)
            for key, value in items:
                if value is not None:
                    params[names_switch[key]] = value
            return self.pulse_voltage_simple(**params)
        elif channel == 'Voltage Staircase Sweep':
            items = arguments.items()
            params = {}
            names_switch = {
                'Steps':'steps',
                'Start':'start',
                'Stop':'stop',
                'Step Width':'width',
                'Frequency of Readings':'frequency',
                'Direction':'direction',
                'VCompliance':'v_compliance',
                'ICompliance':'i_compliance'
            }
            for key, value in items:
                if value is not None:
                    params[names_switch[key]] = value
            return self.sweep_voltage_staircase(**params)

    def reset(self):
        if not self.DEBUG:
            self.write('*RST')
            time.sleep(1)
        # Resets the instrument
#
#    def operation_complete(self):
#        if not self.DEBUG:
#            self.write ('*OPC')
#        # Returns a 1 after all the commands are complete
#

    def configure_measurement(self, sensor):
        if not self.DEBUG:
            # VOLT,CURR RES
            s = ':%s:RANG:AUTO ON' % sensor
            print(s)
            self.write(s)
#
#    def configure_voltage_source(self):
#        if not self.DEBUG:
#            self.write(':SOUR:FUNC:MODE VOLT')
#
#    def set_current_compliance(self,compliance):
#        if not self.DEBUG:
#            self.write(':SENS:CURR:PROT: %r'+ str(compliance))


    def configure_output(self, source_mode='VOLT', output_level=0, compliance_level=0.001):
        if not self.DEBUG:
            # source_mode: VOLT, CURR
            # output_level: in Volts or Amps
            # compliance level: in Amps or Vol
            if source_mode == 'CURR':
                protection = 'VOLT'
            else:
                protection = 'CURR'

            s = ':SOUR:FUNC %s;:SOUR:%s %f;:%s:PROT %r;' % (
                source_mode, source_mode, output_level, protection, compliance_level)
            self.write(s)
#
#

    def enable_output(self):
        if not self.DEBUG:
            self.write(':OUTP ON;')
#
#    def disable_output(self):
#        if not self.DEBUG:
#            self.write (':OUTP OFF;')
#

    def set_value(self, val):  # for interferometer program
        self.set_voltage(val)

    def set_voltage(self, voltage, i_compliance=0.6E-6, v_compliance=11):
        if not self.DEBUG:
            voltage = float(voltage)
            i_compliance = float(i_compliance)
            v_compliance = float(v_compliance)
            if voltage > v_compliance:
                print("V compliance needs to be checked")
                voltage = v_compliance
            self.write(':SOUR:VOLT:RANG 1E-6')######################  This sets the Current measurement range. Normal setting: RANG:AUTO 1 , Other values :RANG 1E-6
            # set autorange on source

            c = ':SENS:CURR:PROT %r' % i_compliance
            self.write(c)
            # set compliance
            c = ':SENS:VOLT:PROT %r' % v_compliance
            self.write(c)

            s = ':SOUR:FUNC VOLT;:SOUR:VOLT %f' % voltage

            self.write(s)
        else:
            print("voltage set to " + str(voltage) + " on " + self.ID_name)
            
            
    def set_current(self, current, i_compliance=0.6E-6, v_compliance=10):
    # This function is added to be able to measure-only the voltage (Not using the keithley as a source measure)
        if not self.DEBUG:
            current = float(current)
            i_compliance = float(i_compliance)
            v_compliance = float(v_compliance)
            if current > i_compliance:
                print("i compliance needs to be checked")
                current = i_compliance
                
            # set autorange on source
            self.write(':SOUR:CURR:RANG MIN')######################  This sets the Current measurement range. Normal setting: RANG:AUTO 1 , Other values :RANG 1E-6
            
            # set compliance
            c = ':SENS:CURR:PROT %r' % i_compliance
            self.write(c)
            
            c = ':SENS:VOLT:PROT %r' % v_compliance
            self.write(c)

            s = ':SOUR:FUNC CURR;:SOUR:CURR %f' % current

            self.write(s)
        else:
            print("voltage set to " + str(voltage) + " on " + self.ID_name)
#    def configure_multipoint(self,sample_count=1,trigger_count=1,output_mode='FIX'):
#        if not self.DEBUG:
#            s = ':ARM:COUN %d;:TRIG:COUN %d;:SOUR:VOLT:MODE %s;:SOUR:CURR:MODE %s;' % (sample_count,trigger_count,output_mode,output_mode)
#            self.write(s)
#
#    def configure_trigger(self,arming_source='IMM',timer_setting=0.01,trigger_source='IMM',trigger_delay=0.0):
#        if not self.DEBUG:
#            # arming source: IMM,BUS,TIM,MAN,TLIN,NST,PST,BST
#                # Immediate Arming
#                # Software Trigger Signal
#                # Timer (set with <B>Timer Setting</B>)
#                # Manual (pressing the TRIG button on the instrument)
#                # Rising SOT Pulse
#                # Falling SOT Pulse
#                # Any SOT Pulse
#                # trigger source: IMM,TLIN
#                # timer setting: interval of time to wait before arming the trigger
#                # trigger delay: the time to wait after the trigger has been
#                s = ':ARM:SOUR %s;:ARM:TIM %f;:TRIG:SOUR %s;:TRIG:DEL %f;' % (arming_source,timer_setting,trigger_source,trigger_delay)
#                self.write(s)
#
#    def initiate(self):
#        if not self.DEBUG:
#            # Clears the trigger, then initiates
#            s = ':TRIG:CLE;:INIT;'
#            self.write(s)
#            time.sleep(0.01)
#            # delay to replace OPC
#
#    def wait_for_OPC(self):
#        if not self.DEBUG:
#            self.write('*OPC;')
#
#    def fetch_measurements(self):
#        if not self.DEBUG:
#            print self.ask(':FETC')
#

    def standard_setup(self):
        if not self.DEBUG:
            self.reset()
            self.configure_measurement('VOLT')
            self.configure_measurement('CURR')
            self.configure_measurement('RES')
            self.configure_output('VOLT', 0, 0.00005)
            self.enable_output()
#
#    def close(self):
#        if not self.DEBUG:
#            self.disable_output()
#            self.write('*RST')
#            self.write('*CLS')
#            self.write(':*SRE 0')
#            #super(Instrument,self).close()

#    def leaking(self, p_tolerance):
#        # Returns 1 if the current leaking is greater than some supplied tolerance
#        # Returns 0 otherwise
#        if abs(self.measure('I')) > abs(p_tolerance):
#            return 1
#        else:
#            return 0

#    def conditional_leak_check(self, p_code, p_leak_check_list=[], p_tolerance=1E-6):
#        # Code = 0 --> do no leak check
#        if p_code == 0 or p_code == 1:
#            return 0
#        # Code = 2 --> Leak check ALL supplied gates, if ONE leaks, report
#        elif p_code == 2:
#            for gate in p_leak_check_list:
#                boolean = gate[0].leaking(gate[1])
#                if boolean == 1:
#                    return 1
#            return 0
#        # Code = 1 --> Leak check only this gate
#        elif p_code == 3:
#            return self.leaking(p_tolerance)

    def move_voltage(self, p_reader, p_target_voltage, step=0.0005, wait=0.05):
        #    def move_voltage(self, p_reader, p_target_voltage, step=0.001, wait=0.005):
        #        print 'Moving voltage'
        current_voltage = self.measure('V')
        # Parse move direction cases
        if current_voltage < p_target_voltage:  # If keithley needs to move up
            # While the current_voltage is not within one increment of the
            # target voltage
            while current_voltage < p_target_voltage:
                # Stop if it needs to
                #                if p_leak_check_code != 0:
                #                    if p_reader.isStopped():
                #                        print("Stopping")
                #                        return 0
                # Increment the current voltage by a safe amount
                current_voltage += step
                self.set_voltage(current_voltage)
                # Wait
                time.sleep(wait)
        elif current_voltage > p_target_voltage:  # If keithley needs to move up
            # While the current_voltage is not within one increment of the
            # target voltage
            while current_voltage > p_target_voltage:
                # Stop if it needs to
                #                if p_leak_check_code != 0:
                #                    if p_reader.isStopped():
                #                        print("Stopping")
                #                        return 0
                # Increment the current voltage by a safe amount
                current_voltage -= step
                self.set_voltage(current_voltage)
                # Wait
                time.sleep(wait)
        # Correct for offset
        self.set_voltage(p_target_voltage)
#        time.sleep(1)
        # return success
        print("Done moving")
        return 1

#    def move_voltage(self, p_reader, p_target_voltage, step=0.001, wait=0.005, p_leak_check_code=0, p_leak_check_list=0, p_tolerance=1E-6):
#        # Safely moves the voltage from its current value to a target voltage
#        # p_leak_check_code = 0 ----> No leak checking and cannot stop with p_reader.isStopped()
#        # p_leak_check_code = 1 ----> No leak checking, can be stopped
#        # p_leak_check_code = 2 ----> All keithleys and tolerance list in p_leak_check_list checked (but not this keithley if not in the list)
#        # p_leak_check_code = 3 ----> Only this Keithley checked for leaks
#        # p_leak_check_list syntax : ([keithley_object_1,
#        # keithley_1_tolerance],[keithley_object_2, keithley_2_tolerance],etc.)
#        # Update voltage to ensure proper information
#        current_voltage = self.measure('V')
#        # Parse move direction cases
#        if current_voltage < p_target_voltage:  # If keithley needs to move up
#            # While the current_voltage is not within one increment of the
#            # target voltage
#            while current_voltage < p_target_voltage:
#                # Stop if it needs to
#                if p_leak_check_code != 0:
#                    if p_reader.isStopped():
#                        print "Stopping"
#                        return 0
#                # Increment the current voltage by a safe amount
#                current_voltage += step
#                self.set_voltage(current_voltage)
#                # If any gate leaking
#                boolean = self.conditional_leak_check(
#                    p_leak_check_code, p_leak_check_list, p_tolerance)
#                if boolean == 1:
#                    # Exit with error
#                    return 0
#                # Wait
#                time.sleep(wait)
#        if current_voltage > p_target_voltage:  # If keithley needs to move up
#            # While the current_voltage is not within one increment of the
#            # target voltage
#            while current_voltage > p_target_voltage:
#                # Stop if it needs to
#                if p_leak_check_code != 0:
#                    if p_reader.isStopped():
#                        print "Stopping"
#                        return 0
#                # Increment the current voltage by a safe amount
#                current_voltage -= step
#                self.set_voltage(current_voltage)
#                # If any gate leaking
#                boolean = self.conditional_leak_check(
#                    p_leak_check_code, p_leak_check_list, p_tolerance)
#                if boolean == 1:
#                    # Exit with error
#                    return 0
#                # Wait
#                time.sleep(wait)
#        # Correct for offset
#        self.set_voltage(p_target_voltage)
#        time.sleep(1)
#        # return success
#        print "Done moving"
#        return 1

        def set_compliance(self):
            # Will eventually create set_compliance function here
            if not self.DEBUG:
                self.write(':SENS:CURR:PROT[:LIM]')
                time.sleep(1)

    def pulse_voltage_simple(self, pulses, start, stop, pulse_width, pulse_delay, frequency = 0.2, base = 0, direction = "BOTH", v_compliance=1, i_compliance=1.0e-7):
        """

        :param pulses:
            number of pulses from start to stop
        :param start:
            default 0V
        :param stop:
            voltage to end at, in Volts
        :param pulse_width:
            length of pulse, in seconds
        :param pulse_delay:
            length of delay between pulses, in seconds
        :param frequency:
            how often readings should occur, in seconds
        :param base:
            the baseline for pulse, as in what the voltage between pulses is set to
        :param direction:
            UP, DOWN, or BOTH
        :param v_compliance:
            voltage compliance, in Volts
        :param i_compliance:
            current compliance, in Amps
        :return: list of [ (list of time readings), (list of voltage readings), (list of current readings) ]

        Does a voltage sweep in pulses,
        meaning in increments dictated by (stop-start)/pulses,
        and will traverse from start to stop and back to stop (depending on direction),
        pulses for pulse_width seconds,
        stays at 0 for pulse_delay seconds, (stays at baseline)
        returns a list of plottable points in 3 dimensions.
        """
        try:
            pulses = int(pulses)
            #start = 0
            start = float(start)
            stop = float(stop)
            pulse_width = float(pulse_width)
            pulse_delay = float(pulse_delay)
            v_compliance = float(v_compliance)
            i_compliance = float(i_compliance)
            frequency = float(frequency)
            base = float(base)
        except ValueError:
            print("Invalid data, must have steps=integer, start=float, stop=float")
            return False
        # okay do stuff
        self.reset()
        self.enable_output()
        start_time = time.time()
        data = []
        step_size = (stop-start)/pulses

        #make range depending on direction
        rang = [i+1 for i in range(0, pulses)]
        if direction == "DOWN":
            rang.reverse()
        elif direction == "BOTH":
            rang += rang[::-1][1::]

        for i in rang:
            # do pulse delay setup
            self.set_voltage(base, i_compliance, v_compliance)
            t = tnow = time.time()
            # do pulse_delay
            while (tnow-t) < pulse_delay:
                r_time, r_data = time.time(), self.ask(self.READ)
                if self.DEBUG:
                    r_data = "%f, %f"%(base,base)
                data.append( (r_time, r_data) )
                tnow = time.time() # to calculate sleep
                if (frequency - (tnow - r_time)) > 0:
                    time.sleep( frequency - (tnow - r_time) )
                tnow = time.time() # to calculate for pulse time

            #do pulse setup, some math involved here
            self.set_voltage( (step_size * i)+start, i_compliance , v_compliance)
            t = tnow = time.time()
            while (tnow-t) < pulse_width:
                r_time, r_data = time.time(), self.ask(self.READ)
                if self.DEBUG:
                    r_data = "%f, %f"%((step_size * i)+start,(step_size * i)+start)
                data.append( (r_time, r_data))
                tnow = time.time()  # to calculate sleep
                if (frequency - (tnow - r_time)) > 0:
                    time.sleep(frequency - (tnow - r_time))
                tnow = time.time()  # to calculate for pulse time

        # now do final reading for base
        self.set_voltage(base, i_compliance, v_compliance)
        t = tnow = time.time()
        while (tnow-t) < pulse_delay:
            r_time, r_data = time.time(), self.ask(self.READ)
            if self.DEBUG:
                r_data = "%f, %f" % (base,base)
            data.append( (r_time, r_data))
            tnow = time.time()  # to calculate sleep
            if (frequency - (tnow - r_time)) > 0:
                time.sleep(frequency - (tnow - r_time))
            tnow = time.time()  # to calculate for pulse time

        # now process some data before returning
        ret = []

        for tup in data:
            splitted = tup[1].split(",")
            ret.append( (
                tup[0]-start_time, #relative time
                float(splitted[0]), #convert voltage to float
                float(splitted[1]) #convert current to float
            ))

        return ret

    # sweep commands, as defined in the Keithley Manual
    def sweep_voltage_bipolar_staircase(self, steps, start, stop, v_compliance = 1, i_compliance = 1e-7):
        def sweep_voltage_staircase(self, steps, start, stop, width=1, frequency=0.2, v_compliance=1,
                                    i_compliance=1e-7):
            """
            :param steps: int (number)
            :param start: float (Volts)
            :param stop: float (Volts)
            :param direction: str
                direction of sweep, UP, DOWN, or BOTH
            :param width: float (seconds)
                the length of the step
            :param frequency: float (seconds)
                how frequent measurement readings are taken
            :param v_compliance: float (Volts)
            :param i_compliance: float (Amps)
            :return: list of coordinates (time, voltage, current)


            Essentially the same as sweep_voltage_staircase, but is bidirection and bipolar
            It is practically equivalent to calling
            sweep_voltage_staircase(steps, start, stop, UP)
            sweep_voltage_staircase(steps, start, stop, DOWN)
            sweep_voltage_staircase(steps, start, -stop, UP)
            sweep_voltage_staircase(steps, start, -stop, DOWN)
            """
            self.enable_output()
            try:
                steps = int(steps)
                start = 0
                stop = float(stop)
                v_compliance = float(v_compliance)
                i_compliance = float(i_compliance)
                width = float(width)
                frequency = float(frequency)
            except TypeError:
                print("Invalid parameter types")
                pass

            sweep1 = np.linspace(start, stop, num=steps)
            sweep2 = np.linspace(stop, start, num=steps)
            sweep3 = np.linspace(start, -stop, num=steps)
            sweep4 = np.linspace(-stop, start, num=steps)

            sweeps = np.concatenate((sweep1, sweep2, sweep3, sweep4))
            list = []
            self.reset()
            self.enable_output()
            start_time = t = time.time()
            for v in sweeps:
                t = tnow = time.time()
                self.set_voltage(v, i_compliance, v_compliance)
                while (tnow - t) < width:
                    r_time, r_data = time.time(), self.ask(self.READ)

                    list.append((r_time, r_data))
                    tnow = time.time()  # to calculate sleep
                    if (frequency - (tnow - r_time)) > 0:
                        time.sleep(frequency - (tnow - r_time))
                    tnow = time.time()  # to calculate for pulse time

            data = []  # 3d coordinates, (Time, Voltage, Current)

            for datapoint in list:
                spl = datapoint[1].split(",")
                data.append((datapoint[0] - t, float(spl[0]), float(spl[1])))
            return data
    # NEEDS WORK

    # def sweep_voltage_staircase(self, steps, start, stop, direction="BOTH", v_compliance = 1, i_compliance = 1e-7):
    #     """
    #     :param steps:
    #         number of steps in sweep
    #     :param start:
    #         starting voltage (for safety reasons, we will disregard and make 0
    #     :param stop:
    #         stopping voltage
    #     :param direction:
    #             UP, DOWN, or BOTH
    #     :v_compliance:
    #             default 1, voltage compliance
    #     :i_compliance:
    #             default 1e-7 A or 100 nanoAmps, current compliance
    #     :return: Data or False
    #
    #     This is programmed as specified by Keithley2400 Manual, Chapter 10-22, staircase sweep from:
    #     http://research.physics.illinois.edu/bezryadin/labprotocol/Keithley2400Manual.pdf
    #     """
    #     # check that all values are good
    #     try:
    #         steps = int(steps)
    #         start = 0
    #         stop = float(stop)
    #         v_compliance = float(v_compliance)
    #         i_compliance = float(i_compliance)
    #     except ValueError:
    #         print("Invalid data, must have steps=integer, start=float, stop=float")
    #         return False
    #     if direction not in ['UP','DOWN', 'BOTH']:
    #         print("Invalid direction, must be UP, DOWN, or BOTH")
    #         return False
    #
    #     if direction == "BOTH":
    #         data_up = self.sweep_voltage_staircase(steps, start, stop, "UP", v_compliance, i_compliance)
    #         data_down = self.sweep_voltage_staircase(steps, start, stop, "DOWN", v_compliance, i_compliance)
    #         return data_up + data_down
    #
    #     self.reset()
    #     #self.write("*RST") # reset any conditions previously set
    #
    #     self.write(":SENS:FUNC:CONC OFF")
    #     self.write(":SOUR:FUNC VOLT") #set source function to VOLT
    #     self.write(":SENS:FUNC 'CURR:DC'")
    #     ######## TODO: CHECK THIS, MIGHT NEED TO BE SOUR:VOLT OR SENS:CURR
    #     self.write(":SENSE:VOLT:PROT " + str(v_compliance))  # SET VOLT COMPLIANCE, default 1
    #     self.write(":SENSE:CURR:PROT " + str(i_compliance))
    #
    #     self.write(":SOUR:VOLT:START "+ str(start)) # set start
    #     self.write(":SOUR:VOLT:STOP " + str(stop))  # set stop
    #     self.write(":SOUR:VOLT:STEP " + str(steps))  # set step
    #
    #     self.write(":SOUR:SWE:RANG AUTO") # TODO: make this a parameter of function
    #     self.write(":SOUR:SWE:SPAC LIN")  # TODO: make this a parameter of function
    #     points = self.ask(":SOUR:SWE:POIN?")
    #     print(points)
    #     #points = round( (stop - start)/steps ) + 1 #TODO: check, as per manual
    #     self.write(":TRIG:COUN "+ str(steps))
    #     self.write(":SOUR:DEL 0.1") #100ms source delay, should be changeable parameter
    #     # get ready to start
    #     self.write(":OUTP ON")
    #     self.write(":INIT")
    #     #time.sleep(0.1*steps)
    #     #trigger and get results
    #     rawdata = [] #self.ask(":TRAC:DATA?") #takes exactly one reading
    #     for i in range(1, steps):
    #         rawdata.append(self.ask(":READ?").split(",")[0])
    #         time.sleep(0.1)
    #     #rawdata += self.ask(":READ?")
    #     #rawdata = self.ask(":TRAC:DATA?")
    #     # do something with raw data
    #     #time.sleep(5)
    #     #rawdata = self.ask(":READ?")
    #     data = rawdata # maybe convert to float
    #
    #     # return data
    #     return data

    def sweep_voltage_simple(self, steps, start, stop, v_compliance=1, i_compliance=1e-7):
        """
        :param steps: int
        :param start: float
        :param stop: float
        :param v_compliance:
        :param i_compliance:
        :return:

        From Oujin's script file
        """
        print("got here")
        self.enable_output()
        try:
            steps = int(steps)
            start = 0
            stop = float(stop)
            v_compliance = float(v_compliance)
            i_compliance = float(i_compliance)
        except TypeError:
            print("Invalid parameter types")
            pass

        sweep1 = np.linspace(start, stop, num=steps)
        sweep2 = np.linspace(stop, start, num=steps)
        sweep3 = np.linspace(start, -stop, num=steps)
        sweep4 = np.linspace(-stop, start, num=steps)

        sweeps = np.concatenate((sweep1, sweep2, sweep3, sweep4))
        sleeptime = 1
        list = []
        for v in sweeps:
            self.set_voltage(v, i_compliance, v_compliance)
            #time.sleep(sleeptime)
            list.append(self.ask(self.READ).split(","))

        data = [] # 2d coordinates, (V, I)

        for datapoint in list:
            data.append( (float(datapoint[0]), float(datapoint[1])))
        return data
    def sweep_voltage_staircase(self, steps, start, stop, direction="BOTH", width=1, frequency=0.2, v_compliance=1, i_compliance=1e-7):
        """
        :param steps: int (number)
        :param start: float (Volts)
        :param stop: float (Volts)
        :param direction: str
            direction of sweep, UP, DOWN, or BOTH
        :param width: float (seconds)
            the length of the step
        :param frequency: float (seconds)
            how frequent measurement readings are taken
        :param v_compliance: float (Volts)
        :param i_compliance: float (Amps)
        :return: list of coordinates (time, voltage, current)

        """
        self.enable_output()
        try:
            steps = int(steps)
            start = 0
            stop = float(stop)
            v_compliance = float(v_compliance)
            i_compliance = float(i_compliance)
            width = float(width)
            frequency = float(frequency)
        except TypeError:
            print("Invalid parameter types")
            pass
        # consider rewritting
        sweep1 = np.linspace(start, stop, num=steps)
        sweep2 = np.linspace(stop, start, num=steps)
        #sweep3 = np.linspace(start, -stop, num=steps) FOR BIPOLAR
        #sweep4 = np.linspace(-stop, start, num=steps)
        if direction == "UP":
            sweeps = sweep1
        elif direction == "DOWN":
            sweeps = sweep2
        else:
            sweeps = np.concatenate((sweep1, sweep2)) #, sweep3, sweep4))
        list = []
        self.reset()
        self.enable_output()
        start_time = t = time.time()
        for v in sweeps:
            t = tnow = time.time()
            self.set_voltage(v, i_compliance, v_compliance)
            while (tnow-t) < width:
                r_time, r_data = time.time(), self.ask(self.READ)
                if self.DEBUG:
                    r_data = "%f, %f"%(v,v)
                list.append((r_time, r_data))
                tnow = time.time()  # to calculate sleep
                if (frequency - (tnow - r_time)) > 0:
                    time.sleep(frequency - (tnow - r_time))
                tnow = time.time()  # to calculate for pulse time
            #time.sleep(sleeptime)
            #list.append(self.ask(":READ?").split(","))

        data = [] # 3d coordinates, (Time, Voltage, Current)


        for datapoint in list:
            spl = datapoint[1].split(",")
            data.append( (datapoint[0]-start_time, float(spl[0]), float(spl[1])))
        return data
    # sweep commands, as defined in the Keithley Manual
    # def sweep_current_staircase(self, steps, start, stop, direction="BOTH", v_compliance = 1, i_compliance = 1e-7):
    #     """ NOT WORKING YET
    #     :param steps:
    #         number of steps in sweep
    #     :param start:
    #         starting voltage (for safety reasons, we will disregard and make 0
    #     :param stop:
    #         stopping voltage
    #     :param direction:
    #             UP, DOWN, or BOTH
    #     :return: Data or False
    #
    #     This is programmed as specified by Keithley2400 Manual, Chapter 10-22, staircase sweep from:
    #     http://research.physics.illinois.edu/bezryadin/labprotocol/Keithley2400Manual.pdf
    #     """
    #     # check that all values are good
    #     try:
    #         steps = int(steps)
    #         start = 0
    #         stop = float(stop)
    #         v_compliance = float(v_compliance)
    #         i_compliance = float(i_compliance)
    #     except ValueError:
    #         print("Invalid data, must have steps=integer, start=float, stop=float")
    #         return False
    #     if direction not in ['UP','DOWN', 'BOTH']:
    #         print("Invalid direction, must be UP, DOWN, or BOTH")
    #         return False
    #
    #     if direction == "BOTH":
    #         data_up = self.sweep_voltage_staircase(steps, start, stop, "UP", v_compliance, i_compliance)
    #         data_down = self.sweep_voltage_staircase(steps, start, stop, "DOWN", v_compliance, i_compliance)
    #         return data_up + data_down
    #
    #     self.reset()
    #     #self.write("*RST") # reset any conditions previously set
    #
    #     self.write(":SENS:FUNC:CONC OFF")
    #     self.write(":SOUR:FUNC CURR") #set source function to VOLT
    #     self.write(":SENS:FUNC 'VOLT:DC'")
    #     ######## TODO: CHECK THIS, MIGHT NEED TO BE SOUR:VOLT OR SENS:CURR
    #     self.write(":SENSE:VOLT:PROT " + str(v_compliance)) # SET VOLT COMPLIANCE, default 1
    #     self.write(":SENSE:CURR:PROT "+ str(i_compliance))
    #     self.write(":SOUR:CURR:START "+ str(start)) # set start
    #     self.write(":SOUR:CURR:STOP " + str(stop))  # set stop
    #     self.write(":SOUR:CURR:STEP " + str(steps))  # set step
    #
    #     self.write(":SOUR:SWE:RANG AUTO") # TODO: make this a parameter of function
    #     self.write(":SOUR:SWE:SPAC LIN")  # TODO: make this a parameter of function
    #
    #     points = round( (stop - start)/steps + 1 ) #TODO: check, as per manual
    #     self.write(":TRIG:COUN "+ str(points))
    #     self.write(":SOUR:DEL 0.1") #100ms source delay, should be changeable parameter
    #
    #     # get ready to start
    #     self.write(":OUTP ON")
    #
    #     #trigger and get results
    #     rawdata = self.ask(self.READ)
    #
    #     # do something with raw data
    #
    #     data = rawdata # maybe convert to float
    #
    #     # return data
    #     return data

    """  sweep commands, as defined in the Keithley Manual
    def sweep_staircase(self, voltage_dict, current_dict, sweep_points, sweep_direction="BOTH", source_ranging="BEST", sweep_scale="LINEAR"):
        ""
        :param voltage_dict:
            A dictionary containing the following elements:
                start: number (WILL ALWAYS BE 0)
                stop: number
                step: number
                center: number
                span: number
        :param current_dict:
                start: number
                stop: number
                step: number
                center: number
                span: number
        :param source_ranging:
                string, either "BEST", "AUTO", "FIX" (fixed)
        :param sweep_scale:
                either "LINEAR" or "LOGARITHMIC"
        :param sweep_points:
                either
        :param sweep_direction:
                UP, DOWN, or BOTH
        :return: Data or False

        This is programmed as specified by Keithley2400 Manual, Chapter 10-22, staircase sweep from:
        http://research.physics.illinois.edu/bezryadin/labprotocol/Keithley2400Manual.pdf
        ""
        # check that all values
        required_voltages = ['stop', 'step', 'center', 'span']
        required_currents = ['start', 'stop', 'step', 'center', 'span']
        if not all(key in voltage_dict.keys() for key in required_voltages):
            print("There is missing data in voltage dictionary")
            return False
        # set start voltage to 0 for safety reasons
        voltage_dict['start'] = 0

        if not all(key in current_dict.keys() for key in required_currents):
            print("There is missing data in current dictionary")

        if source_ranging not in ['BEST', 'AUTO', 'FIX']:
            if source_ranging == "FIXED":
                source_ranging = "FIX"
            else:
                print("Invalid source ranging; must be either BEST, AUTO, or FIX")
                return False
        if sweep_scale not in ['LIN', 'LOG']:
            if sweep_scale == 'LINEAR':
                sweep_scale = 'LIN'
            elif sweep_scale == 'LOGARITHMIC':
                sweep_scale = 'LOG'
            else:
                print("Invalid sweep scale; must be either LIN or LOG")
                return False


        if sweep_direction == "BOTH": #sweep up then down
            #rup up
            dataup = self.sweep_staircase(voltage_dict,current_dict,sweep_points,"UP",source_ranging,sweep_scale)
            #rup down
            datadown = self.sweep_staircase(voltage_dict,current_dict,sweep_points,"DOWN",source_ranging,sweep_scale)
            if dataup is False or datadown is False:
                return False
            else:
                return dataup + datadown
        # make sure numerical values are strings
        for key, values in voltage_dict.items():
            voltage_dict[key] = str(values)
        for key, values in current_dict.items():
            current_dict[key] = str(values)
        sweep_points = str(sweep_points)

        # now actually set the information

        # set current stuff
        self.write(":SOUR:CURR:MODE SWE") #select current sweep mode
        self.write(":SOUR:CURR:STAR " + current_dict['start']) #set start
        self.write(":SOUR:CURR:STOP " + current_dict['stop']) #set stop
        self.write(":SOUR:CURR:STEP " + current_dict['step']) #set step
        self.write(":SOUR:CURR:CENT " + current_dict['center']) #set center
        self.write(":SOUR:CURR:SPAN " + current_dict['span']) #set span

        # set voltage stuff
        self.write(":SOUR:VOLT:MODE SWE") #select voltage sweep mode
        self.write(":SOUR:VOLT:STAR " + voltage_dict['start']) #same
        self.write(":SOUR:VOLT:STOP " + voltage_dict['stop'])  #for
        self.write(":SOUR:VOLT:STEP " + voltage_dict['step'])  #current
        self.write(":SOUR:VOLT:CENT " + voltage_dict['center'])#set
        self.write(":SOUR:VOLT:SPAN " + voltage_dict['span'])  #functions

        # the rest of the stuff
        self.write(":SOUR:SWE:RANG "+source_ranging) # swet source ranging
        self.write(":SOUR:SWE:SPAC "+sweep_scale) #set sweep scale
        #self.write(":SOUR:SWE:POIN "+sweep_points) # set number of sweep points
        self.write(":SOUR:SWE:DIRE "+sweep_direction) #either up or down

        #note, trigger count should equal (stop-start)/step + 1

        sweep_points = ()
    """


if __name__ == "__main__":
    i = Instrument("GPIB0::28", debug=False)
    print((i.identify("Hello, this is ")))
    #function = Tool.generate_function_obj(pulse=i.pulse_voltage_simple, simple=i.sweep_voltage_simple)
    #print(function)
    #i.configure_output('VOLT', 0, 1E-7)
#    i.set_voltage(0,1E-7)
    #data = i.sweep_voltage_staircase(100, 0, 0.1, "BOTH")
    #print("data", data)
    print((i.measure('V')))
    print((i.measure('I')))
