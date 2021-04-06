# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 11:24 2020
Rhodes and Schwarz ZVA VNA Driver
@author: Anthony Ubah
Last Updated: Feb 25 2020
"""

import random
from . import Tool

param = {'1': '1', '2': '2', '3': '3', '4':'4'}

INTERFACE = Tool.INTF_VISA

import numpy as np

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'RS_ZVM', debug=debug,
                                         interface = INTERFACE, **kwargs)
        # determine model
        try:
            # records the make/model/serial number/firmware.
            # Should be returned in form  "Rohde&Schwarz, ZVxx, 123456/001, 1.03" as per manual v2p3.18
            self.make, self.model, self.serial, self.firmware = self.identify().split(",")
        except:
            raise Exception("Unsupported VNA device")

        self.traces ={'1':None, '2':None,'3':None,'4':None}
    """ driver commands """
    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in self.last_measure:
            if self.traces[channel] is None:
                self.traces[channel] = np.array(self.read_trace(int(channel)))
            else:
                self.traces[channel] = np.vstack(self.traces[channel],self.read_trace(int(channel)))

            print(self.traces)
            """
            if not self.DEBUG:
                if channel == 'Channel':
                    answer = 'value'
            else:
                answer = 123.4
            """
            answer = float('nan')

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        self.last_measure[channel] = answer
        return answer

    def set(self, obj):
        for channel, data in obj.items():
            pass

    def get(self):
        pass

    def run(self, channel, arguments):
        pass

    """ trace """
    def read_trace(self, chan=1):
        self.write("DISP:FORM QQSP")
        return [float(i) for i in self.query("TRAC? CH%dDATA" % chan).split(", ")]



    """ channel """

    def set_active_channel(self, chan=1):
        """
        Selects channel as the active channel.

        INSTrument:NSELect <channel>
        """
        self.write(":INST:NSEL %d"%int(chan))
    def get_active_channel(self):
        """
        Retrieves active channel.

        INSTrument:NSELect?
        """
        return int(self.read(":INST:NSEL?" ))

    def set_averaging_clear(self, chan=1):
        """
        TODO:

        SENS<chan>:AVERage:CLEear
        """
        self.write(":SENS%d:AVER:CLE"%int(chan))
    def set_averaging_count(self, chan=1, factor=10):
        """
        TODO:

        SENS<chan>:AVERage:COUNt <number>
        """
        self.write(":SENS%d:AVER:CLE"%(int(chan),int(factor)))
    def set_averaging_state(self, chan=1, ONOFF="ON"):
        """
        SENS<chan>:AVERage:STATe <on/off>
        """
        if ONOFF not in ["ON","OFF"]:
            raise Exception("Invalid state")
        else:
            self.write(":SENS%d:AVER:COUN %s"%(int(chan), ONOFF))

    #Triggers calibration query and subsequently query the calibration status. Any responses >0 indicate errors.
    def calibration_query(self):
        msg = '*CAL?'
        ans = self.ask(msg)
        #Need to add in error checking.
        return ans

    #Sets the status byte (STB), the standard event register (ESR) and the EVENt-part of the QUEStionable and the OPERation register to zero. The
    def clear_status(self):
        msg = '*CLS'
        ans = self.write(msg)
        return ans

    #Sets the event status enable register to the value indicated. Query *ESE? returns the contents of the event status enable register in decimal form.
    def event_status_enable(self,value):
        #Need to implement value validation. 0 <= value <= 255
        msg = '*ESE ' + value
        self.write(msg)

    #Returns the contents of the event status enable register in decimal form.
    def event_status_enable_query(self,value):
        #Need to implement value validation. 0 <= value <= 255
        msg = '*ESE ' + value
        ans = self.ask(msg)
        return ans

    #Returns the contents of the event status register in decimal form (0 to 255) and subsequently sets the register to zero
    def standard_event_status_query(self):
        msg = '*ESR?'
        ans = self.ask(msg)
        return ans
    #Queries and returns the instrument identification.
    def identification_query(self):
        msg = '*IDN?'
        ans = self.ask(msg)
        return ans

    #Returns the contents of the IST flag in decimal form (0 | 1).
    def individual_status_query(self):
        msg = '*IST?'
        ans = self.ask(msg)
        return ans

    #Sets bit 0 in the event status register when all preceding commands have been executed.
    def operation_complete(self):
        msg = '*OPC'
        self.write(msg)

    #Writes message "1" into the output buffer as soon as allpreceding commands have been executed
    def operation_complete_query(self):
        msg = '*OPC?'
        ans = self.ask(msg)
        return ans

    #Queries the options included in the instrument and returns a list of the options installed. The options are separated from each other by means of commas.
    def option_identification_query(self):
        msg = '*OPT?'
        ans = self.ask(msg)
        return ans

    #Indicates the controller address which the IEC-bus control is to be returned to after termination of the triggered action.
    def pass_control_back(self, addr):
        #Need to implement value validation. 0 <= value <= 30
        msg = '*PCB ' + value
        self.write(msg)

    #Sets parallel poll enable register to the value indicated.
    def parallel_poll_register_enable(self,value):
        #Need to implement value validation. 0 <= value <= 255
        msg = '*PRE ' + value
        self.write(msg)

    #Queries and returns the contents of the parallel poll enable register in decimal form.
    def parallel_poll_register_enable_query(self):
        msg = '*PRE?'
        ans = self.ask(msg)
        return ans

    #Determines whether the contents of the ENABle registers is maintained or reset in switching on.
    def power_on_status_clear(self,value):
        msg = '*PSC ' + value
        self.write(msg)

    #Reads out the contents of the power-on-status-clear flag. The response can be 0 or 1.
    def power_on_status_clear_query(self):
        msg = '*PSC?'
        ans = self.ask(msg)
        return ans

    #Sets the instrument to a defined default status
    def reset(self):
        msg = '*RST'
        self.write(msg)

    #Sets the service request enable register to the value indicated. Bit 6 (MSS mask bit) remains 0.
    #This command determines under which conditions a service request is triggered.
    def service_request_enable(self,value):
        #Need value validation. 0 <= value <= 255
        msg = '*SRE ' + value
        self.write(msg)

    #Query and returns the contents of the service request enable register in decimal form. Bit 6 is always 0.
    def service_request_enable_query(self):
        msg = '*SRE?'
        ans = self.ask(msg)
        return ans

    #Reads out the contents of status byte in decimal form.
    def read_status_byte_query(self):
        msg = '*STB?'
        ans = self.ask(msg)
        return ans

    #Triggers all actions waiting for a trigger event.
    def trigger(self):
        msg = '*TRG'
        self.write(msg)

    #Triggers all self tests of the instrument and outputs an error code in decimal form.
    def self_test_query(self):
        msg = '*TST?'
        ans = self.ask(msg)
        return ans

    #Only permits the servicing of the subsequent commands after all preceding commands have been executed and all signals have settled.
    def wait_to_continue(self):
        msg = '*WAI'
        self.write(msg)

    #---------------------
    #CALCUALTE SUBSYSTEM |
    #--------------------

    #There are a whole host of commands that can be added here. Unless specified in table and comments here, every command has a query
    #function associated with it.


    #This command defines in which format the complex measured quantity is displayed.
    def set_display_format(self,channel,format):
        #Need input validation on format and channel.
        msg = 'CALC' + channel + ':FORM ' + format
        self.write(msg)

    #This command defines the physical units for the direct measured wave quantities.
    def set_port_units(self,channel,port,unit):
        #Need input calidation on unit, port and channel.
        msg = 'CALC' + channel + ':UNIT:POW:' + port + ' ' + unit
        self.write(msg)

    #----------------------
    # Intitiate Subsystem |
    #---------------------

    #Unless specified in table and comments here, every command has a query function associated with it.

    #This command determines if the trigger system is continuously initiated ("Free Run").
    def initiate_continuous_trigger(self,state):
        #Need input validation on state.
        msg = 'INIT:CONT ' + state
        self.write(msg)

    #The command initiates a new sweep or starts a single sweep - NO QUERY.
    def initiate_immediate_trigger(self,state):
        msg = 'INIT:IMM'
        self.write(msg)

    #------------------
    # Input Subsystem |
    #-----------------

    #This command determines the attenuation of the attenuator in the signal path of the incident wave b1 or b2.
    def set_attenuation(self,value):
        #Need to implement input validation on level. 0 <= value <= 70
        msg = 'INP:ATT ' + level + 'dB'
        self.write(msg)

    
