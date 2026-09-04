# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:31:59 2013
This is the driver for PFEIFER Smart_Test leakdetector serial number:21255069
the serial address is chosen in front panel of smart test as 030 out of 255 possible
@author: PF

the comunication watchdog is buggy
"""
#import visa
import numpy as np
import random
import os.path
#import alarm_toolbox as alarm
try:
    from . import Tool
except:
    import Tool

import time
from LabTools.Fitting.Functions import exp_decay

param = {'FLOW': 'mbarl/s', 'P2': 'mbar'}

INTERFACE = Tool.INTF_SERIAL


class Instrument(Tool.MeasInstr):

    # 1 will enable a watchdog function that will check every telegramm from
    # master to slave and every answer from slave to master
    watchdog = 0

    # this is the serial address the GPIB-RS232 converter must use
    __serial_address = ''
    # after serial address, communication must indicate if it is read ('00')
    # or write('10')
    __const_read = '00'
    __const_write = '10'

    # Contains the different section of a typical message in the communication
    # protocole with the instrument
    __message_sections = ['Address', 'Action',
                          'Parameter#', 'DataLength', 'Data', 'Checksum']
    __command_list = []
    # if this value is set to any other values beside 0 it will print the
    # message sections and their value each time the method write or read is
    # called
    display_infos = 0

    def __init__(self, resource_name, debug=False, serial_address='001', **kwargs):
        super(Instrument, self).__init__(resource_name, 'HLT560',
                                         debug=debug, interface=INTERFACE, **kwargs)

        self.__serial_address = str(serial_address)

        self.__command_list = {}
#        self.__get_param_manual_info()
        self.start_time = None
#        self.watchdog=1
        if not self.DEBUG:
            self.connection.delay = 0.25  # instrument should be serial port COM#

    def identify(self, msg=""):
        if self.DEBUG == False:
            return msg + self.get_DeviceName()
        else:
            return msg + self.ID_name
#-----------------------------------------------------------------------------
   # Only for debugging, use the ID of a command and get the answer of the
   # instrument for a read instruction

    def debug_msg(self, ID):
        answer = self.read(self.__msg_read(ID))
        return answer[4]

    # the communication protocol is quite specicic to this instrument so we
    # redefine read and write as private methods
    def read(self, msg):
        print("this method is desactivated, please use get/set or debug methods")

    def write(self, msg):
        print("this method is desactivated, please use get/set or debug methods")

    def __read(self, msg):
        if not self.DEBUG:
            #            print 'Execute : ' +msg
            #            answer = self.ask(msg)
            self.connection.write(msg.encode())
            answer = ""
            c = self.connection.read(1).decode()
            while c != '\r':
                answer = answer + c
                c = self.connection.read(1).decode()
            if self.watchdog:
                self.__communication_watchdog(msg, answer)

            return self.message_parser(answer, self.display_infos)
        else:
            # print "DEBUG MODE : " + msg
            return self.message_parser(msg, self.display_infos)

    def __write(self, msg):
        if not self.DEBUG:
            #            print 'Execute : ' +msg
            answer = self.ask(msg)
            if self.watchdog:
                self.__communication_watchdog(msg, answer)
            return self.message_parser(answer, self.display_infos)
        else:
            # print "DEBUG MODE : " + msg
            return self.message_parser(msg, self.display_infos)

    # checksum() method calculates the checksum of all the ascii characters
    # recieved in argument if run as own program
    def __checksum(self, string):
        total = 0
        for i in range(len(string)):
            total = total + ord(string[i])
        return str(total % 256)

    # this function is used to prepare the telegrams to communicate with the
    # instrument
    def message_builder(self, action, param_num, data):
        data_length = len(str(data))
        # print data_length
        if data_length < 10:
            data_length = '0' + str(data_length)
        else:
            if data_length == 16:
                data_length = str(data_length)
            else:
                print(
                    "Not good data input, please refer to p19 of the pfeiffer vacuum communication protocole")

        msg = self.__serial_address + action + \
            param_num + data_length + str(data)
        msg = msg + self.__checksum(msg) + '\r'
        return msg

    # parse the telegraph style commandline matching the different
    # message_sections
    def message_parser(self, msg, display=0):

        data_length = int(msg[8:10])
        message = [msg[0:3], msg[3:5], msg[5:8], msg[8:10], msg[
            10:(10 + data_length)], msg[(10 + data_length):(13 + data_length)]]

        if display:
            self.__message_displayer(message)
            print("Calculated checksum : " +
                  self.__checksum(msg[0:(10 + data_length)]))
            print(" ")
        return message

    # display a message which is already in a parsed format
    def __message_displayer(self, msg_list):
        for section, section_value in zip(self.__message_sections, msg_list):
            print(section + ' : ' + section_value)

    # prepare a message to be sent to the instrument in writing mode
    def __msg_write(self, param_num, data):
        msg = self.message_builder(self.__const_write, param_num, data)
        return msg

    # prepare a message to be sent to the instrument in reading mode
    def __msg_read(self, param_num):
        msg = self.message_builder(self.__const_read, param_num, '=?')
        return msg

    # diplay information about a command provided its ID number
    def command_info(self, command_num):
        command_name = self.__command_list[0][command_num]
        if command_num == 643:
            param_list = self.__command_list[1][command_name]
            if self.watchdog:
                print(str(command_num) + " " +
                      command_name + " " + param_list[0])
            return param_list[1:3]
        else:
            print(str(command_num) + " " + command_name +
                  " " + self.__command_list[1][command_name])
#-----------------------------------------------------------------------------

    def measure(self, channel):
        if not self.DEBUG:
            #        print "HLT560 measure"+channel+"000"
            #        print self.last_measure
            if channel in self.last_measure:
                if channel == 'FLOW':
                    answer = self.measure_flow()
                elif channel == 'P2':
                    answer = self.measure_pressure_P2()
            else:
                print("you are trying to measure a non existent channel : " + channel)
                print("existing channels :", self.channels)
                answer = None
        else:
            if self.start_time == None:
                self.reset_start_time()
            dt = time.time() - self.start_time
            if dt < 10:
                answer = 0.05 * (random.random() - 0.5)
            else:
                answer = exp_decay(dt-10, 2, 15) * (1 + 0.05 *
                                                    (random.random() - 0.5))
        return answer

    # get the lastest value of the flow and update the last measure
    def measure_flow(self):
        flow = self.get_LeakRate_mbarls()
        self.last_measure['flow'] = flow
        return flow

    # get the lastest value of the pressure P2 and update the last measure
    def measure_pressure_P2(self):
        pressure = self.get_PressureP2()
        self.last_measure['P2'] = pressure
        return pressure

    def error_log(self):
        for i in range(1, 11):
            print(self.get_PastErr(i) + " @ " + self.get_DateTime(i))

    def reset_start_time(self):
        self.start_time = time.time()

    def get_MotorTMP(self):
        answer = self.__read(self.__msg_read('023'))
        return answer[4]

    def get_ErrorCode(self):
        answer = self.__read(self.__msg_read('303'))
        return answer[4]

    def get_ActRotSpd(self):
        answer = self.__read(self.__msg_read('309'))
        return answer[4]

    def get_DeviceName(self):
        answer = self.__read(self.__msg_read('349'))
        return answer[4]

    def get_PastErr(self, buffer_value):
        if buffer_value < 11 and buffer_value > 0:
            answer = self.__read(self.__msg_read(str(359 + buffer_value)))
            return answer[4]
        else:
            print("get_PastErr() -> wrong input parameter, should be bewteen 1 and 10")
            return "get_PastErr() -> wrong input parameter, should be bewteen 1 and 10"

    def get_DateTime(self, buffer_value):
        if buffer_value < 11 and buffer_value > 0:
            answer = self.__read(self.__msg_read(str(369 + buffer_value)))
            return answer[4]
        else:
            print("get_DateTime() -> wrong input parameter, should be bewteen 1 and 10")
            return "get_DateTime() -> wrong input parameter, should be bewteen 1 and 10"

    def get_AnalogMode(self):
        answer = self.__read(self.__msg_read('602'))
        return answer[4]

    def set_AnalogMode(self, value_abc):
        return self.__write(self.__msg_write('602', value_abc))

    def get_PhysUnits(self):
        answer = self.__read(self.__msg_read('643'))
        answer = '000'  # answer[4]
        Param_list = self.command_info(643)
        return [Param_list[0][int(answer[1])], Param_list[1][int(answer[2])]]

    def set_PhysUnits(self, value_abc):
        answer = self.__write(self.__msg_write('643', value_abc))
        answer = answer[4]
        Param_list = self.command_info(643)
        return "SET_PhysUnits : Leak Rate in " + Param_list[0][int(answer[1])] + " Pressure in " + Param_list[1][int(answer[2])]

    def get_ZeroTime(self):
        answer = self.__read(self.__msg_read('646'))
        return answer[4]

    def set_ZeroTime(self, value_sec):
        return self.__write(self.__msg_write('646', value_sec))

    def get_Zero(self):
        answer = self.__read(self.__msg_read('651'))
        return answer[4]

    def set_Zero(self, value_1_0):
        return self.__write(self.__msg_write('651', value_1_0))

    def get_FlowMin(self):
        answer = self.__read(self.__msg_read('664'))
        return answer[4]

    def set_FlowMin(self, value_sccm):
        return self.__write(self.__msg_write('664', value_sccm))

    def get_FlowMax(self):
        answer = self.__read(self.__msg_read('665'))
        return answer[4]

    def set_FlowMax(self, value_sccm):
        return self.__write(self.__msg_write('665', value_sccm))

    def get_CurrState(self):
        answer = self.__read(self.__msg_read('666'))
        return answer[4]

    def aknowledge_error(self):
        return self.write(self.__msg_write('009', 111111))

    def set_CurrState(self, value_0_15):
        if value_0_15 < 16 and value_0_15 > -1:
            answer = self.__write(self.__msg_write('666', value_0_15))
            return answer[4]
        else:
            print("set_CurrState() -> wrong input parameter, should be bewteen 0 and 15")
            return -1

    def get_LeakRate_mbarls(self):
        answer = self.__read(self.__msg_read('670'))
        if self.DEBUG == False:
            return self.__convert_str_to_Q(answer[4])
        else:
            return random.random()

    def get_PressureP2(self):
        answer = self.__read(self.__msg_read('680'))
        if self.DEBUG == False:
            return self.__convert_str_to_Q(answer[4])
        else:
            return random.random()

# This function seems not to be responding
#    def get_TMP_Imot(self):
#        return self.read(self.__msg_read('310'))

    # Convert the flow returned value into a float
    def __convert_str_to_Q(self, resp):
        # First 4 characters are the value of the mantissa
        # Last 2 are exponent with -20 offset
        #mantissa = float(resp[0])+float(resp[1])/10.+float(resp[2])/100.+float(resp[3])/1000.
        mantissa = float(resp[0:4]) / 1000.0
        expo = float(resp[4:6])

        return round(mantissa * np.power(10, expo - 20.0), int(abs(expo - 23.0)))

    # load information to help understanding the commands arguments
    def __get_param_manual_info(self):
        file_path = __file__.replace("HLT560.pyc", "HLT560_commands.txt")
#        file_pathHLT560_commands.txt
#        print file_path
        cmd_file = open(file_path)

        # settings will contain the two dictionnaries, dict1 contains the
        # command name referenced by the command number dict2 contain the
        # command description referenced by the command name
        settings = []
        dict1 = {}
        dict2 = {}
        for line in cmd_file:
            if line[0] != '#':
                # the symbol @ separates the field command number, command
                # name, command description
                [left, center, right] = line.split('@', 2)
                left = left.strip()
                center = center.strip()
                right = right.strip()

                # command name referenced by the command number
                dict1[int(left)] = center

                # special case for physical units
                if int(left) == 643:
                    d1 = {}
                    d2 = {}
                    cat = right.split(':')
                    # correspond to flow units
                    d = cat[1].split(';')
                    for el in d:
                        [idx, name] = el.split('=')
                        d1[int(idx)] = name

                    # correspond to pressure units
                    d = cat[2].split(';')
                    for el in d:
                        [idx, name] = el.split('=')
                        d2[int(idx)] = name

                    right = [right, d1, d2]

                # command description referenced by the command name
                dict2[center] = right

        cmd_file.close()
        settings.append(dict1)
        settings.append(dict2)
        return settings

    # make sure that the master->slave and slave->master communication made sense
    # this is activated setting self.watchdog=1
    def __communication_watchdog(self, msg_sent, msg_recieved, display=1):
        msg_in = self.message_parser(msg_sent)

        msg_out = self.message_parser(msg_recieved)

        self.command_info(int(msg_out[2]))

        index = 0
        error_code = [0, 0, 0, 0, 0]

        if msg_in[index] != msg_out[index]:
            error_code[index] = 1
            if display:
                print("error: the adress of the master (" +
                      msg_in[index] + ") and of the slave (" + msg_out[index] + ") are not the same!")

        index = 1
        if msg_in[index] != '00' and msg_in[index] != '10':
            error_code[index] = 1
            if display:
                print(
                    "error: the master question is neither in write or read mode ('10'/'00')")

        if msg_out[index] != '10':
            error_code[index] = 2
            if display:
                print("error: the slave response is not in write mode ('10')")

        index = 2
        if msg_in[index] != msg_out[index]:
            error_code[index] = 1
            if display:
                print("error: the parameter# of the master (" +
                      msg_in[index] + ") and of the slave (" + msg_out[index] + ") are not the same!")

        index = 3
        if msg_in[1] == '00':
            if msg_in[index] != '02':
                error_code[index] = 1
                if display:
                    print(
                        "error: the master question is in read mode but the datalength is not equal to '02'")
            if msg_in[index + 1] != '=?':
                error_code[index + 1] = 2
                if display:
                    print(
                        "error: the master question is in read mode but the data is not equal to '=?'")
            # possibility to add a test to see whether the size of the data
            # matches the normally sent values

        if msg_in[1] == '10':
            if msg_in[index] != msg_out[index]:
                error_code[index] = 3
                if display:
                    print("error: the datalength of the master (" +
                          msg_in[index] + ") and of the slave (" + msg_out[index] + ") are not the same!")
            if msg_in[index + 1] != msg_out[index + 1]:
                error_code[index + 1] = 4
                if display:
                    print("error: the data of the master (" +
                          msg_in[index + 1] + ") and of the slave (" + msg_out[index + 1] + ") are not the same!")

        return error_code


def checksum(string):
    total = 0
    for i in range(len(string)):
        total = total + ord(string[i])
    return str(total % 256)


if (__name__ == '__main__'):

    print(__file__.strip("HLT560.py"))
    myInst = Instrument("/dev/tty.usbserial-A105H5BS1")
#    print(myInst.identify())
    print(myInst.measure("FLOW"))
#    print(myInst.get_MotorTMP())
    myInst.close()