# -*- coding: utf-8 -*-
"""
Created on Wed May 16 16:22:26 2012
Keithley 2400
@author: Bram
"""

#!/usr/bin/env python
import time

import random
try:
    from . import Tool
except:
    import Tool

import math

param = {'V': 'V', 'I': 'A'}

INTERFACE = Tool.INTF_GPIB


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):

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

    def measure(self, channel):
        if channel in self.last_measure:

            if channel == 'V':
                if not self.DEBUG:
                    # 0 #this is to be defined for record sweep
                    self.write('VOLT:RANG:AUTO ON')
                    answer = self.ask(':READ?')
                    #if math.isnan(float(answer)):
                    if type(answer) is not str and math.isnan(answer): #answer will be nan if error
                        print("Please set Output on")
                        answer = float(answer)
                    else:
                        answer = float(answer.split(',')[0])
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'I':
                if not self.DEBUG:
                    # 0 #this is to be defined for record sweep
                    self.write('CURR:RANG:AUTO ON')
                    answer = self.ask(':READ?')
                    #if math.isnan(float(answer)):
                    if type(answer) is not str and math.isnan(answer): #answer will be nan if error
                        print("Please set Output on")
                        answer = float(answer)
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
#            self.write(':SENS:CURR:PROT:LEV '+ str(compliance))
#

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

    def set_voltage(self, voltage, compliance=1.0E-7):
        if not self.DEBUG:

            self.write(':SOUR:VOLT:RANG:AUTO 1')
            # set autorange on source

            #c = ':SENS:CURR:PROT %r' % compliance
            # self.write(c)
            # set compliance

            s = ':SOUR:FUNC VOLT;:SOUR:VOLT %f' % voltage

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

    def move_voltage(self, p_reader, p_target_voltage, step=0.0005, wait=0.005):
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

    # sweep commands, as defined in the Keithley Manual
    #def sweep_voltage_bipolar_staircase(self, ):
    def sweep_voltage_staircase(self, steps, start, stop, direction="BOTH", v_compliance = 1, i_compliance = 1e-7):
        """
        :param steps:
            number of steps in sweep
        :param start:
            starting voltage (for safety reasons, we will disregard and make 0
        :param stop:
            stopping voltage
        :param direction:
                UP, DOWN, or BOTH
        :return: Data or False

        This is programmed as specified by Keithley2400 Manual, Chapter 10-22, staircase sweep from:
        http://research.physics.illinois.edu/bezryadin/labprotocol/Keithley2400Manual.pdf
        """
        # check that all values are good
        try:
            steps = int(steps)
            start = 0
            stop = float(stop)
            compliance = int(compliance)
        except ValueError:
            print("Invalid data, must have steps=integer, start=float, stop=float")
            return False
        if direction not in ['UP','DOWN', 'BOTH']:
            print("Invalid direction, must be UP, DOWN, or BOTH")
            return False

        if direction == "BOTH":
            data_up = self.sweep_voltage_staircase(steps, start, stop, "UP", compliance)
            data_down = self.sweep_voltage_staircase(steps, start, stop, "DOWN", compliance)
            return data_up + data_down

        self.write("*RST") # reset any conditions previously set

        self.write(":SENS:FUNC:CONC OFF")
        self.write(":SOUR:FUNC VOLT") #set source function to VOLT
        self.write(":SENS:FUNC 'CURR:DC'")
        ######## TODO: CHECK THIS, MIGHT NEED TO BE SOUR:VOLT OR SENS:CURR
        self.write(":SENSE:VOLT:PROT " + str(v_compliance))  # SET VOLT COMPLIANCE, default 1
        self.write(":SENSE:CURR:PROT " + str(i_compliance))
        self.write(":SOUR:VOLT:START "+ str(start)) # set start
        self.write(":SOUR:VOLT:STOP " + str(stop))  # set stop
        self.write(":SOUR:VOLT:STEP " + str(steps))  # set step

        self.write(":SOUR:SWE:RANG AUTO") # TODO: make this a parameter of function
        self.write(":SOUR:SWE:SPAC LIN")  # TODO: make this a parameter of function

        points = round( (stop - start)/steps ) + 1 #TODO: check, as per manual
        self.write(":TRIG:COUN "+ str(points))
        self.write(":SOUR:DEL 0.1") #100ms source delay, should be changeable parameter

        # get ready to start
        self.write(":OUTP ON")

        #trigger and get results
        rawdata = self.ask(":READ?") #takes exactly one reading
        #rawdata += self.ask(":READ?")

        # do something with raw data

        data = rawdata # maybe convert to float

        # return data
        return data

    # sweep commands, as defined in the Keithley Manual
    def sweep_current_staircase(self, steps, start, stop, direction="BOTH", v_compliance = 1, i_compliance = 1e-7):
        """
        :param steps:
            number of steps in sweep
        :param start:
            starting voltage (for safety reasons, we will disregard and make 0
        :param stop:
            stopping voltage
        :param direction:
                UP, DOWN, or BOTH
        :return: Data or False

        This is programmed as specified by Keithley2400 Manual, Chapter 10-22, staircase sweep from:
        http://research.physics.illinois.edu/bezryadin/labprotocol/Keithley2400Manual.pdf
        """
        # check that all values are good
        try:
            steps = int(steps)
            start = 0
            stop = float(stop)
            compliance = int(compliance)
        except ValueError:
            print("Invalid data, must have steps=integer, start=float, stop=float")
            return False
        if direction not in ['UP','DOWN', 'BOTH']:
            print("Invalid direction, must be UP, DOWN, or BOTH")
            return False

        if direction == "BOTH":
            data_up = self.sweep_voltage_staircase(steps, start, stop, "UP", compliance)
            data_down = self.sweep_voltage_staircase(steps, start, stop, "DOWN", compliance)
            return data_up + data_down

        self.write("*RST") # reset any conditions previously set

        self.write(":SENS:FUNC:CONC OFF")
        self.write(":SOUR:FUNC CURR") #set source function to VOLT
        self.write(":SENS:FUNC 'VOLT:DC'")
        ######## TODO: CHECK THIS, MIGHT NEED TO BE SOUR:VOLT OR SENS:CURR
        self.write(":SENSE:VOLT:PROT " + str(v_compliance)) # SET VOLT COMPLIANCE, default 1
        self.write(":SENSE:CURR:PROT "+ str(i_compliance))
        self.write(":SOUR:CURR:START "+ str(start)) # set start
        self.write(":SOUR:CURR:STOP " + str(stop))  # set stop
        self.write(":SOUR:CURR:STEP " + str(steps))  # set step

        self.write(":SOUR:SWE:RANG AUTO") # TODO: make this a parameter of function
        self.write(":SOUR:SWE:SPAC LIN")  # TODO: make this a parameter of function

        points = round( (stop - start)/steps + 1 ) #TODO: check, as per manual
        self.write(":TRIG:COUN "+ str(points))
        self.write(":SOUR:DEL 0.1") #100ms source delay, should be changeable parameter

        # get ready to start
        self.write(":OUTP ON")

        #trigger and get results
        rawdata = self.ask(":READ?")

        # do something with raw data

        data = rawdata # maybe convert to float

        # return data
        return data

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

    #i.configure_output('VOLT', 0, 1E-7)
#    i.set_voltage(0,1E-7)
    #data = i.sweep_voltage_staircase(100, 0, 0.1, "BOTH")
    #print("data", data)
    print((i.measure('V')))
    print((i.measure('I')))
