# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 16:16:02 2013

@author: Sam
"""


#!/usr/bin/env python
import time
import random
try:
    from . import Tool
except:
    import Tool


param = {'V': 'V'}

INTERFACE = Tool.INTF_VISA

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, V_step_limit=None):
        super(Instrument, self).__init__(resource_name, 'YOKO', debug = debug, interface = INTERFACE)
        self.standard_setup()
        self.V_step_limit = V_step_limit

    def __del__(self):
        super(Instrument, self).__del__()
        # self.disable_output()
        # self.close()

    def standard_setup(self):
        if not self.DEBUG:
            self.write(':OUTP 1')
            # self.enable_output()

    def measure(self, channel='V'):  # Do I nead to write the channel argument here?
        """ This method does not measure, it asks what value is
            displayed on the screen (asks the source level) """
        if not self.DEBUG:
            answer = self.ask(':SOUR:LEV?')
            answer = float(answer.split(',', 1)[0])
        else:
            answer = random.random()

        return answer

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

    def set_voltage(self, voltage, port=0):
        if not self.DEBUG:
            prev_voltage = self.measure()

            # first check if there is a step limit, then do the math (no error if
            # self.V_step_limit is None, thanks to lazy evaluation)
            do_it = False

            if self.V_step_limit == None:
                do_it = True
            elif abs(voltage - prev_voltage) < self.V_step_limit:
                do_it = True
            if do_it:
                s = ':SOUR:FUNC VOLT;:SOUR:LEV %f' % voltage
#                s = ':SOUR:FUNC VOLT;:SOUR:LEV %f;:SOUR:PROT:CURR 1E-3;' % voltage
                self.write(s)
            else:
                print("Voltage step is too large!")
        else:
            print("voltage set to " + str(voltage) + " on " + self.ID_name)

    def set_current(self, current):
        if not self.debug:
            s = ':SOUR:FUNC CURR;:SOUR:LEV %f' % current
#                s = ':SOUR:FUNC VOLT;:SOUR:LEV %f;:SOUR:PROT:CURR 1E-3;' % voltage
            self.write(s)

        else:
            print("current set to " + str(voltage) + " on " + self.ID_name)


    def enable_output(self):
        if not self.debug:
            self.write(':OUTP 1')

    def disable_output(self):
        if not self.debug:
            self.write(':OUTP 0')


#    def measure(self,channel='V'):
#        if self.last_measure.has_key(channel):
#            if not self.debug:
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
        if not self.debug:
            self.write('*RST')
            time.sleep(1)
        # Resets the instrument

    def configure_measurement(self, sensor):
        if not self.debug:
            # VOLT,CURR RES
            s = ':%s:RANG:AUTO ON' % sensor
            print(s)
            self.write(s)

    def configure_output(self, source_mode='VOLT', output_level=0, compliance_level=0.001):
        if not self.debug:
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
#        if not self.debug:
#            self.write('*OPC')
#        # Returns a 1 after all the commands are complete
#
#
#    def configure_voltage_source(self):
#        if not self.debug:
#            self.write(':SOUR:FUNC:MODE VOLT')
#
#    def set_current_compliance(self,compliance):
#        if not self.debug:
#            self.write(':SENS:CURR:PROT:LEV '+ str(compliance))
#
#
#    def close(self):
#        if not self.debug:
#            self.disable_output()
#            self.write('*RST')
#            self.write('*CLS')
#            self.write(':*SRE 0')
#            super(Instrument,self).close()
#
#    def configure_multipoint(self,sample_count=1,trigger_count=1,output_mode='FIX'):
#        if not self.debug:
#            s = ':ARM:COUN %d;:TRIG:COUN %d;:SOUR:VOLT:MODE %s;:SOUR:CURR:MODE %s;' % (sample_count,trigger_count,output_mode,output_mode)
#            self.write(s)
#
#    def configure_trigger(self,arming_source='IMM',timer_setting=0.01,trigger_source='IMM',trigger_delay=0.0):
#        if not self.debug:
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
#        if not self.debug:
#            # Clears the trigger, then initiates
#            s = ':TRIG:CLE;:INIT;'
#            self.write(s)
#            time.sleep(0.01)
#            # delay to replace OPC
#
#    def wait_for_OPC(self):
#        if not self.debug:
#            self.write('*OPC;')
#
#    def fetch_measurements(self):
#        if not self.debug:
#            print self.ask(':FETC')

if __name__ == "__main__":

    BPO = Instrument("GPIB0::19")
    print(BPO.identify())
    BPO.set_voltage(0)
#    print(BPO.measure('V'))

