# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 16:16:02 2013

@author: Sam

developer note: Lower bound of current compliance limit is off by a factor of 10 from what the query 
    ask SOUR:CURR:PROT:ULIM? MIN
since it might be specific to the machine that we were testing on, the limit was hardcoded with the default
value being the corrected compliance (x10)
"""


#!/usr/bin/env python
import time
import random
try:
    from . import Tool
except:
    import Tool


param = {'V': 'V','I':'A'}

INTERFACE = Tool.INTF_VISA


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, V_step_limit=None, I_step_limit=None):
        super(Instrument, self).__init__(resource_name,
                                         'YOKO', debug=debug, interface=INTERFACE)
        self.standard_setup()
        self.V_step_limit = V_step_limit
        self.I_step_limit = I_step_limit

    def standard_setup(self):
        if not self.DEBUG:
            self.write(':OUTP 1')
            # self.enable_output()

    def measure(self, channel='V'):  # Do I nead to write the channel argument here?
        """ This method does not measure, it asks what value is
            displayed on the screen (asks the source level) """
        if not self.DEBUG:
            if channel == 'V':
                answer = self.get_voltage()
            elif channel == 'I':
                answer = self.get_current()
            else:
                print("Invalid channel")
                answer = float('nan')
#            answer = float(answer.split(',', 1)[0])
        else:
            answer = random.random()

        return answer
    
    def get_voltage(self):
        return float(self.ask(':SOUR:VOLT:LEV?'))
    def get_current(self):
        return float(self.ask(':SOUR:CURR:LEV?'))
        
    def set_value(self, val):  # for interferometer program
        actual_voltage = self.measure()
#        actual_range = self.ask(':SOUR:RANG?')
#        actual_range = float(actual_range)

        print("actual", actual_voltage)
        if abs(actual_voltage - val) > 0.3:
            print("voltage increment is too high (>0.3)-->change refused")

#        """ WARNING: if val has more precision (digits) that the actual range allows,
#            yoko crashes and go to 0.00000 so fix that"""
#        elif len(str(actual_range).split('.', 2)[1]) < len(str(val).split('.', 2)[1]):
# print "value has more precision than allowed by Yoko range-->change
# refused"

#        elif val > 1.2*actual_range:
#            self.write(':SOUR:RANG UP')
#            self.set_voltage(val)
#
#        elif val < 1.2*actual_range:
#            self.write(':SOUR:RANG DOWN')
#            self.set_voltage(val)

        else:
            self.set_voltage(val)

    def set_voltage(self, voltage, i_compliance=1e-6, v_compliance=1, port=0):
        if not self.DEBUG:
            prev_voltage = self.get_voltage()
            voltage = float(voltage)
            i_compliance = float(i_compliance)
            if i_compliance < 0: i_compliance = -1 * i_compliance
            v_compliance = float(v_compliance)
            
            if voltage > v_compliance:
                print("V compliance needs to be checked")
                voltage = v_compliance
            # first check if there is a step limit, then do the math (no error if
            # self.V_step_limit is None, thanks to lazy evaluation)
            do_it = False

            if self.V_step_limit == None:
                do_it = True
            elif abs(voltage - prev_voltage) < self.V_step_limit:
                do_it = True
            if do_it:
                if  1e-3 < v_compliance < 110 and 1e-7 < i_compliance < 3.2:
                    # set compliances
                    c = ':SOUR:VOLT:PROT:ULIM %f' % v_compliance
                    self.write(c)
                    c = ':SOUR:VOLT:PROT:LLIM %f' % -v_compliance
                    self.write(c)
                    c = ':SOUR:CURR:PROT:ULIM %f' % i_compliance
                    self.write(c)
                    c = ':SOUR:CURR:PROT:LLIM %f' % -i_compliance
                    self.write(c)
                    s = ':SOUR:VOLT:LEV %f' % voltage
                    self.write(s)
                else:
                    print("Invalid compliance range, no voltage set")
                
                
            else:
                print("Voltage step is too large!")
        else:
            print("voltage set to " + str(voltage) + " on " + self.ID_name)
            
    def set_current(self, current, i_compliance=1e-6, v_compliance=1, port=0):
        if not self.DEBUG:
            prev_current = self.get_current()
            current = float(current)
            i_compliance = float(i_compliance)
            if i_compliance < 0: i_compliance = -1 * i_compliance
            v_compliance = float(v_compliance)
            if v_compliance < 0: v_compliance = -1 * v_compliance
            
            if current > i_compliance:
                print("I compliance needs to be checked")
                current = i_compliance
            # first check if there is a step limit, then do the math (no error if
            # self.V_step_limit is None, thanks to lazy evaluation)
            do_it = False

            if self.I_step_limit == None:
                do_it = True
            elif abs(current - prev_current) < self.I_step_limit:
                do_it = True
            if do_it:
                if  1e-3 < v_compliance < 110 and 1e-6 < i_compliance < 3.2:
                    # set compliances
                    c = ':SOUR:VOLT:PROT:ULIM %f' % v_compliance
                    self.write(c)
                    c = ':SOUR:VOLT:PROT:LLIM %f' % -v_compliance
                    self.write(c)
                    c = ':SOUR:CURR:PROT:ULIM %f' % i_compliance
                    self.write(c)
                    c = ':SOUR:CURR:PROT:LLIM %f' % -i_compliance
                    self.write(c)
                    s = ':SOUR:CURR:LEV %f' % current
                    self.write(s)
                else:
                    print("Invalid compliance range, no current set")
                
                
            else:
                print("current step is too large!")
        else:
            print("current set to " + str(current) + " on " + self.ID_name)
            # should be good test it while im gone
    def enable_output(self):
        if not self.DEBUG:
            self.write(':OUTP 1')

    def disable_output(self):
        if not self.DEBUG:
            self.write(':OUTP 0')


#    def measure(self,channel='V'):
#        if self.last_measure.has_key(channel):
#            if not self.DEBUG:
#                answer=self.ask(':READ?') #  0 #this is to be defined for record sweep
#                answer = float(answer.split(',',1)[0])
#
#            else:
#                answer=random.random()
#            self.last_measure[channel]=answer
#        else:
#            print "you are trying to measure a non existent channel : " +channel
#            print "existing channels :", self.channels
#            answer=None
#        return answer

            # Should Read KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx,
            # yyyyy/zzzzz /a/d

    def reset(self):
        if not self.DEBUG:
            self.write('*RST')
            time.sleep(1)
        # Resets the instrument

    def configure_measurement(self, sensor):
        if not self.DEBUG:
            # VOLT,CURR RES
            s = ':%s:RANG:AUTO ON' % sensor
            print(s)
            self.write(s)

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

    def move_voltage(self, p_reader, p_target_voltage, step=0.0001, wait=0.001):
        #    def move_voltage(self, p_reader, p_target_voltage, step=0.001, wait=0.005):
        #        print 'Moving voltage'
        current_voltage = self.measure('V')
        # Parse move direction cases
        if current_voltage < p_target_voltage:  # If keithley needs to move up
            # While the current_voltage is not within one increment of the
            # target voltage
            while current_voltage < p_target_voltage:
                # Stop if it needs to
                if p_reader.isStopped():
                    print("Stopping")
                    return 0
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
                if p_reader.isStopped():
                    print("Stopping")
                    return 0
                # Decrement the current voltage by a safe amount
                current_voltage -= step
                self.set_voltage(current_voltage)
                # Wait
                time.sleep(wait)
        # Correct for offset
        self.set_voltage(p_target_voltage)
    #        time.sleep(1)
        # return success
    #        print "Done moving"
        return 1


""" BUNCH OF COMMENTED FUNCTIONS FROM THE ORIGINAL KT2400 DRIVER"""

#    def operation_complete(self):
#        if not self.DEBUG:
#            self.write('*OPC')
#        # Returns a 1 after all the commands are complete
#
#
#    def configure_voltage_source(self):
#        if not self.DEBUG:
#            self.write(':SOUR:FUNC:MODE VOLT')
#
#    def set_current_compliance(self,compliance):
#        if not self.DEBUG:
#            self.write(':SENS:CURR:PROT:LEV '+ str(compliance))
#
#
#    def close(self):
#        if not self.DEBUG:
#            self.disable_output()
#            self.write('*RST')
#            self.write('*CLS')
#            self.write(':*SRE 0')
#            super(Instrument,self).close()
#
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

if __name__ == "__main__":

    BPO = Instrument("GPIB0::11")
    print(BPO.identify())
    BPO.set_voltage(0)
    print(BPO.ask(':SOUR:VOLT:LEV?'))
    print(BPO.ask(':SOUR:VOLT:LEV?'))
#    BPO.measure('V')
#    print BPO.measure('V')
