# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 17:19:35 2013

@author: pfduc
"""
import sys
import io
from collections import OrderedDict
from importlib import import_module

import numpy as np

import logging
logging.basicConfig(level=logging.DEBUG)

try:
    import serial
    serial_available = True

except ImportError:

    serial_available = False
    print("pyserial package not installed")

try:
    import visa
    visa_available = True

except ImportError:

    visa_available = False
    print("pyvisa package not installed")


import socket

from LocalVars import USE_PYQT5

if USE_PYQT5:

    from PyQt5.QtCore import QObject, pyqtSignal

else:

    from PyQt4.QtCore import SIGNAL, QObject

try:

    from .utils import INTF_VISA, INTF_SERIAL, INTF_PROLOGIX, INTF_NONE, \
        INTF_GPIB, PROLOGIX_COM_PORT, PROLOGIX_AUTO, refresh_device_port_list,\
        is_IP_port, PrologixController, LABDRIVER_PACKAGE_NAME,\
        list_serial_ports, list_GPIB_ports

except:

    from utils import INTF_VISA, INTF_SERIAL, INTF_PROLOGIX, INTF_NONE, \
        INTF_GPIB, PROLOGIX_COM_PORT, PROLOGIX_AUTO, refresh_device_port_list,\
        is_IP_port, PrologixController, LABDRIVER_PACKAGE_NAME,\
        list_serial_ports, list_GPIB_ports

# Use these constants to identify interface type.
# Avoids case-sensitivity/typo issues if you were to use the strings directly
# these are imported by the instrument drivers so keep them there even if your
# editor tells you that utils.INTF_NONE isn't used

old_visa = True
try:
    # poke at something that only exists in older versions of visa, as a probe
    # for the version
    visa.term_chars_end_input
#    logging.info("using pyvisa version less than 1.6")

except:

    old_visa = False
#    logging.info("using pyvisa version higher than 1.6")


class MeasInstr(object):
    """
    Class of a measure instrument this is designed to be a parent class
    from which any new instrument driver should inherit, this way one
    avoid redefining features common to most instruments
    It entails connecting to the instrument (connect), talking to it
    (ask, read, write) and measuring (measure, only defined here as an
    empty method, any child class should redefine it)
    """

    # **kwargs can be any of the following param "timeout", "term_chars","chunk_size",
    # "lock","delay", "send_end","values_format"
    # example inst=MeasInstr('GPIB0::0','Inst_name',True,timeout=12,term_char='\n')
    # other exemple inst=MeasInstr('GPIB0::0',timeout=12,term_char='\n')
    def __init__(
            self,
            resource_name,
            name='default',
            debug=False,
            interface=None,
            **kwargs
    ):
        """
            use interface = None if the instrument will not inherit read and 
            write functionality from Tool for example TIME, DICE, ZH_HF2 and 
            other highly custom instruments
        """

        # identify the instrument in a unique way
        self.ID_name = name
        # store the pyvisa object connecting to the hardware
        self.connection = None
        # debug mode trigger
        self.DEBUG = debug
        # contains the different channels available
        self.channels = []
        # store the instrument last measure in the different channels
        self.last_measure = {}
        # contains the units of the different channels
        self.units = {}
        # contains the name of the different channels if the channels do not have
        # explicit names
        self.channels_names = {}

        # the name of the communication port it will be changed in the
        # connect method
        self.resource_name = None

        self.term_chars = ""

        self.interface = interface

        # check which interface the user choose to use
        if self.interface == INTF_VISA:

            # version of pyvisa
            if not old_visa:

                self.resource_manager = visa.ResourceManager()

        if self.interface == INTF_PROLOGIX:
            # there is only one COM port that the prologix has, then we go
            # through that for all GPIB communications
            prologix_kwargs = {}
            if PROLOGIX_AUTO in kwargs:
                # if one instrument cannot read after write, it will cause IO errors
                # cf. section 8.2 of the Prologix GPIB to USB manual
                # http://prologix.biz/downloads/PrologixGpibUsbManual-6.0.pdf
                prologix_kwargs['auto'] = kwargs[PROLOGIX_AUTO]

            if INTF_PROLOGIX in kwargs:

                # the connection is passed as an argument
                if isinstance(kwargs[INTF_PROLOGIX], str):
                    # it was the COM PORT number so we initiate an instance
                    # of prologix controller
                    if "COM" in kwargs[INTF_PROLOGIX]:
                        self.connection = PrologixController(
                            com_port=kwargs[INTF_PROLOGIX],
                            **prologix_kwargs
                        )

                else:
                    # it was the PrologixController instance
                    self.connection = kwargs[INTF_PROLOGIX]

                    if "Prologix GPIB-USB Controller" in self.connection.controller_id():
                        if 'auto' in prologix_kwargs:
                            # if one instrument cannot read after write, it will cause IO errors
                            # cf. section 8.2 of the Prologix GPIB to USB manual
                            # http://prologix.biz/downloads/PrologixGpibUsbManual-6.0.pdf
                            self.connection.auto = prologix_kwargs['auto']
                    else:
                        logging.error(
                            "The controller passed as an argument is not the good one")

            else:
                # the connection doesn't exist so we create it
                    self.connection = PrologixController(**prologix_kwargs)
        else:
            #Remove this
            if PROLOGIX_AUTO in kwargs:
                kwargs.pop(PROLOGIX_AUTO)

        # load the parameters and their unit for an instrument from the values
        # contained in the global variable of the latter's module
        if name != 'default':

            try:

                module_name = import_module(
                    "." + name, package=LABDRIVER_PACKAGE_NAME)

            except ImportError:
                module_name = import_module(
                    name, package=LABDRIVER_PACKAGE_NAME)
#            else:
#                module_name=import_module("."+name,package=LABDRIVER_PACKAGE_NAME)
            self.channels = []

            for chan, u in list(module_name.param.items()):
                # initializes the first measured value to 0 and the channels'
                # names
                self.channels.append(chan)
                self.units[chan] = u
                self.last_measure[chan] = 0
                self.channels_names[chan] = chan

        # establishs a connection with the instrument
        # this check should be based on interface, not resource_name
        # the check is now performed in self.connect, deprecating this if statement
        # if not resource_name is None:
        self.connect(resource_name, **kwargs)

    def initialize(self):
        """
        Instruments may overload this function to do something when the
        script first starts running (as opposed to immediately when connected)
        For example, noting the time the run started
        """
        pass

    def __str__(self):

        return self.identify()

    def getID_name(self):
        return self.ID_name

    def identify(self, msg=''):
        """ Try the IEEE standard identification request """

        if not self.DEBUG:

            id_string = str(self.ask('*IDN?'))

            if id_string is not None:

                return msg + id_string
            elif "?*IDN?" in id_string:
                print("Oxford")

            else:

                return "Unknown instrument"

        else:

            return msg + self.ID_name

    def read(self, num_bytes=None):
        """ Reads data available on the port (up to a newline char) """

        answer = None

        if not self.DEBUG:

            if self.interface == INTF_VISA:

                answer = self.connection.read()

            elif self.interface == INTF_SERIAL or self.interface == INTF_PROLOGIX:

                if num_bytes is not None:

                    answer = self.connection.read(num_bytes)

                else:

                    answer = self.connection.readline()

                # remove the newline character if it is at the end
                if len(answer) > 1:

                    if answer[-1:] == '\n':

                        answer = answer[:-1]

                if len(answer) > 1:

                    if answer[-1] == '\r':

                        answer = answer[:-1]

        return answer

    def write(self, msg):
        """ 
            Writes command to the instrument but does not check for a response
        """

        answer = None

        if not self.DEBUG:

            if self.interface == INTF_PROLOGIX:
                # make sure the address is the right one (might be faster to
                # check for that, might be not)
                self.connection.write("++addr %s" % self.resource_name)

            if not self.connection is None:

                answer = self.connection.write(msg + self.term_chars)

            else:

                logging.debug("There is no physical connection established \
with the instrument %s" % self.ID_name)

        else:

            answer = msg

        return answer

    def ask(self, msg, num_bytes=None): #also known as query
        """ Writes a command to the instrument and reads its reply """

        answer = None

        if not self.DEBUG:

            if self.interface == INTF_VISA:

                try:

                    answer = self.connection.query(msg) #ask is depricated

                    """ Alternative Method
                    
                    self.connection.write(msg)
                    
                    answer = self.connection.read()
                    
                    Might be necessary for Oxford devices
                    
                    """
                except:
                    print("\n\n### command %s bugged###\n\n" % msg)
                    answer = np.nan

            elif self.interface == INTF_SERIAL or self.interface == INTF_PROLOGIX:

                try:

                    self.write(msg)
                    answer = self.read(num_bytes)

                except:
                    print("\n\n### command %s bugged###\n\n" % msg)
                    answer = np.nan
        else:
            answer = msg
        return answer

    def connect(self, resource_name, **keyw):
        """Trigger the physical connection to the instrument"""

        logging.debug("keyw arguments for instrument %s" % self.ID_name)

        for a in keyw:

            logging.debug(a)

        if not self.DEBUG:

            if self.interface == INTF_VISA:

                # make sure the instrument is not already connected
                self.close()

                # connects differently depending on the version of pyvisa
                if old_visa:

                    self.connection = visa.instrument(resource_name, **keyw)

                else:

                    logging.debug("using pyvisa version higher than 1.6")
                    self.connection = self.resource_manager.get_instrument(
                        resource_name, **keyw)

                # keep track of the port used with the instrument
                self.resource_name = resource_name

            elif self.interface == INTF_SERIAL:

                # make sure the instrument is not already connected
                self.close()

                if "term_chars" in keyw:
                    # store the terminaison character and will add them
                    # automatically at the end of each commands sent through
                    # the connection
                    self.term_chars = keyw["term_chars"]
                    keyw.pop("term_chars")

                if "baud_rate" in keyw:
                    # the baud rate need to be passed as an argument not a kwarg
                    baud_rate = keyw["baud_rate"]
                    keyw.pop("baud_rate")

                    self.connection = serial.Serial(
                        resource_name, baud_rate, **keyw)

                else:

                    self.connection = serial.Serial(resource_name, **keyw)

                # keep track of the port used with the instrument
                self.resource_name = resource_name

            elif self.interface == INTF_PROLOGIX:
                # only keeps the number of the port
                self.resource_name = resource_name.replace('GPIB0::', '')

                self.connection.write(("++addr %s" % self.resource_name))
                self.connection.readline()
                # the \n termchar is embedded in the PrologixController class
                self.term_chars = ""

            elif self.interface == INTF_NONE:
                # instruments like TIME and DICE don't have a resource name
                # so just set it to their ID name
                if resource_name is None:
                    # keep track of the port used with the instrument
                    self.resource_name = self.ID_name

                else:
                    # keep track of the port used with the instrument
                    self.resource_name = resource_name

                logging.debug("setting default resource name of instrument %s\
to '%s'" % (self.ID_name, self.resource_name))
                # all others must take care of their own communication

            else:
                logging.error("The interface you passed as an argument to \
connect the instrument %s to the port %s is not implemented, check utils.py \
file to see which are the ones implemented" % (self.ID_name, resource_name))

            logging.info("connected to %s (INTF : %s)" % (str(resource_name),
                                                          self.interface))

    def close(self):
        """Close the connection to the instrument"""
        if self.connection is not None:

            try:

                self.connection.close()
                logging.debug("disconnect " + self.ID_name)

            except:

                logging.debug("unable to disconnect  " + self.ID_name)

    def clear(self):
        """Clear the conneciton to the instrument"""
        if self.connection is not None:

            try:

                if self.interface == INTF_VISA:

                    self.connection.clear()
                    print("cleared " + self.ID_name)

            except:

                print("unable to clear  " + self.ID_name)

    def measure(self, channel):
        """
            define this method so any instrument has a defined method measure()        
        """
        return None

    def get_last_measure(self, channel):
        """
            define to access the last measure made to a channel and not send
            too many request to the instrument if it is used by different sources
        """
        if channel in self.last_measure:

            return self.last_measure[channel]

        else:

            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            return np.nan


def create_virtual_inst(parent_class):
    """
    returns a instrument which connect to a server as a client to fetch 
    values uploaded by an actual instrument 
    """
    class VirtualInstrument(parent_class):

        def __init__(self, resource_name, debug=False, **kwargs):

            super(VirtualInstrument, self).__init__(resource_name,

                                                    debug=debug,

                                                    interface=INTF_NONE,

                                                    **kwargs)

            self.DEBUG = debug

            if is_IP_port(resource_name):

                self.host, self.port, self.device_port = is_IP_port(
                    resource_name, return_vals=True)

#                self.host = int(self.host)
#

            else:

                print("'%s' doesn't have the right format" % resource_name)

        def identify(self):

            return "Virtual %s at %s"(self.ID_name. self.host)

        def use_method(self, method_name, *args, **kwargs):
            """
            This sends a request to call a method of the server instrument
            it provides the potential arguments and keyword arguments
            """

            # parsing the arguments into a string to send the request
            arguments = ""

            # arguments
            if len(args) > 0:

                for arg in args:

                    arguments = "%s,%s" % (arguments, arg)

            # keyword arguments
            if len(kwargs) > 0:

                for key in kwargs:

                    arguments = "%s,%s=%s" % (arguments, key, kwargs[key])

            # if the string isn't empty
            if arguments:

                # if there is a comma in the first spot we remove it
                if arguments[0] == ',':

                    arguments = arguments[1:]

            # prepare the request in the format
            # "inst_ID.method(*args,**kwargs)@device_port"
            req = "%s.%s(%s)@%s" % (self.ID_name, method_name,
                                    arguments, self.device_port)

#            print(req)
#
#            print("HOST : %s"%(self.host))
#
#            print("PORT : %s"%(self.port))

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
            # initiates the connection
            try:

                s.connect((self.host, self.port))

            except socket.error:

                logging.error("Wrong IP or IP port number for the \
virtual instrument %s" % self.ID_name)

                return "NetworkError : the IP address might be wrong or the \
server might be down"

            # sends the request
            s.sendall(req)

            # collect the answer form the server
            stri = s.recv(1024)

            s.close()

            return stri

        def measure(self, channel):

            if channel in self.last_measure:

                if not self.DEBUG:

                    # prepare the request and sends it to the instrument
                    answer = self.use_method(
                        'get_last_measure', channel=channel)

                    # if there is an error we display it and return nan
                    # so that it doesn't affect the data taking process
                    if 'Error' in answer:

                        logging.error(answer)

                        answer = np.nan

                    else:

                        answer = float(answer)
                else:
                    # random answer for the debug mode
                    answer = np.random.random()

                self.last_measure[channel] = answer

            else:

                print("you are trying to measure a non existent channel of %s \
instrument : '%s'" % (self.ID_name, channel))

                print("existing channels :", self.channels)

                answer = np.nan

            return answer

    # return an instance of the virtualInstrument class which inherited from
    # the class passed as an argument
    return VirtualInstrument


class InstrumentHub(QObject):
    """
        this class manages a list of instruments (that one would use for an 
        experiment)

    """

    if USE_PYQT5:
        # creating a signal
        changed_list = pyqtSignal()

        instrument_hub_connected = pyqtSignal()

    def __init__(self, parent=None, debug=False, **kwargs):

        #        self.

        if parent is not None:

            super(InstrumentHub, self).__init__(parent)
            self.parent = parent
            # connect with its parent to change the debug mode throught a
            # signal
            if USE_PYQT5:

                #                self.trigger = pyqtSignal(bool, name = "DEBUG_mode_changed(bool)")
                self.parent.debug_mode_changed.connect(self.set_debug_state)

            else:
                self.connect(parent, SIGNAL(
                    "DEBUG_mode_changed(bool)"), self.set_debug_state)

        else:

            self.parent = None

        logging.debug("InstrumentHub created")

        self.DEBUG = debug
        logging.debug("debug mode of InstrumentHub Object :%s" % self.DEBUG)

        # this is an ordered dictionary where the keys are the port names
        # and the values are the Instrument objects (which should inherit from
        # Tool.MeasInstr and implement a measure(string) function)
        self.instrument_list = OrderedDict()

        # this will be the list of [GPIB address, parameter name] pairs
        # the read data command can then call instrument_list[port].measure param for
        # each element in this list
        self.port_param_pairs = []

        # check if the connectic interface is prologix if you use serial or
        # other GPIB to usb converter you can ignore any prologix code
        if INTF_PROLOGIX in kwargs:
            # the connection is passed as an argument

            if isinstance(kwargs[INTF_PROLOGIX], str):
                # it was the COM PORT number so we initiate an instance
                # of prologix controller
                if "COM" in kwargs[INTF_PROLOGIX]:

                    self.prologix_com_port = PrologixController(
                        kwargs[INTF_PROLOGIX])

            else:
                # it was the PrologixController instance
                self.prologix_com_port = kwargs[INTF_PROLOGIX]

                # check that the instance is a prologix controller (version can
                # change but this sentence is in all of their model when I coded
                # this)
                if "Prologix GPIB-USB Controller" in self.prologix_com_port.controller_id():
                    pass

                else:
                    logging.error("The prologix controller passed as an \
argument is not the good one")

        else:

            if INTF_GPIB == INTF_PROLOGIX:
                # the connection doesn't exist so we create it
                self.prologix_com_port = PrologixController()

            else:

                self.prologix_com_port = None

    def __del__(self):
        # free the existing connections
        self.clean_up()

        logging.info("InstrumentHub deleted")

    def change_interface(self, intf):
        """Change the way one connects to GPIB interface"""

        if intf == INTF_PROLOGIX:
            # the connection doesn't exist so we create it
            self.prologix_com_port = PrologixController()

        elif intf == INTF_VISA:

            self.prologix_com_port = None

        else:

            logging.error("Problem with change of interface in the the \
instrument hub. Interface passed as an argument : %s" % intf)
    # debug note may23rd2019 - HP34401A throws error in this function
    def connect_hub(self, instr_list, dev_list, param_list):
        """ 
            triggers the connection of a list of instruments instr_list,
            dev_list contains the port name information and param_list should
            refer to one of the parameters each instrument would measure.

            The 3 lists should be the same size and the order of the items in
            each list matters.
        """
        # first close the potential connections and clear the lists
        self.clean_up()

        # loop over the lists to connect each instrument to the corresponding
        # port to measure the given parameter
        for instr_name, device_port, param in zip(instr_list,
                                                  dev_list,
                                                  param_list):

            logging.debug("Trying to connecting %s to %s to measure %s" % (
                instr_name, device_port, param))

            self.connect_instrument(
                instr_name, device_port, param, send_signal=False)

        if self.parent is not None:
            # notify that the list of instuments has been modified

            if USE_PYQT5:

                self.changed_list.emit()

                self.instrument_hub_connected.emit()

            else:

                self.emit(SIGNAL("changed_list()"))

                self.emit(SIGNAL("instrument_hub_connected()"))

        logging.debug("Connect_hub : the lists of instrument and port-params")
        logging.debug(self.port_param_pairs)
        logging.debug(self.instrument_list)

    def connect_instrument(self, instr_name, device_port, param, send_signal=True):
        # device_port should contain the name of the GPIB or the COM port
        #        class_inst=__import__(instr_name)
        logging.debug("args : %s, %s, %s" % (instr_name, device_port, param))

        # the relative import works differently if this module is executed as
        # the main or imported
        if __name__ == "__main__":

            class_inst = import_module(instr_name)

        else:

            class_inst = import_module("." + instr_name,
                                       package=LABDRIVER_PACKAGE_NAME)

        # check if the port is already used in our list
        if device_port in self.instrument_list:
            print('Instrument already exists at' + device_port)

            # the instrument we are trying to connect is not the same as the
            # instrument already connected to this device_port
            if instr_name != self.instrument_list[device_port].ID_name:

                print("You are trying to connect " +
                      instr_name + " to the port " + device_port)
                print("But " + self.instrument_list[
                      device_port].ID_name + " is already connected to " + device_port)

                # make sure that the instrument will not be added to the port_param list
                instr_name = 'NONE'
                # make sure that no signal is sent that the list was changed
                send_signal = False

            else:
                print("Connect_instrument: added the measurement of %s to %s \
which is connected to %s " % (param, instr_name, device_port))

        # the port is not used yet
        else:
            logging.debug("The port %s is not in the list already" %
                          (device_port))

            # let the instrument be connected if it isn't one of these two strings
            if instr_name != '' and instr_name != 'NONE':

                if is_IP_port(device_port):

                    logging.debug("Creation of a virtual instrument")

                    virtual_class = create_virtual_inst(class_inst.Instrument)

                    obj = virtual_class(device_port, debug=self.DEBUG)

                elif class_inst.INTERFACE == INTF_PROLOGIX and self.prologix_com_port is not None:
                    print("The instrument uses prologix")
                    obj = class_inst.Instrument(
                        device_port, self.DEBUG, prologix=self.prologix_com_port)

                elif class_inst.INTERFACE == INTF_PROLOGIX and self.prologix_com_port is None:

                    logging.error(
                        "The interface is PROLOGIX but the controller object is not provided")

                else:
                    # the instrument interface is INTF_NONE, INTF_SERIAL or INTF_GPIB

                    # I should do the check here if the device port can be
                    # assimilated to an IP address
                    #                    if is_IP_port(device_port):
                    #                        print "the address passed is of the good format"
                    #                        virtual_class = create_virtual_inst(class_inst.Instrument)
                    #
                    #                        obj = virtual_class(device_port, debug = self.DEBUG)
                    #                        #create a virtual instrument passing class_inst.Instrument
                    #                        #as an argument for inheritance
                    #                    else:
                    obj = class_inst.Instrument(device_port,
                                                debug=self.DEBUG)

                if not self.DEBUG:

                    device_port = obj.resource_name

                self.instrument_list[device_port] = obj

                print("Connect_instrument: Connected %s to %s to measure %s" %
                      (instr_name, device_port, param))

        if instr_name != '' and instr_name != 'NONE':

            self.port_param_pairs.append([device_port, param])

        else:

            self.port_param_pairs.append([None, None])

        if send_signal:

            if USE_PYQT5:

                self.changed_list.emit()

            else:
                #            print "sending the signal"
                self.emit(SIGNAL("changed_list()"))

    def get_instrument_list(self):
        """get the port name together with the instrument instance"""
        return self.instrument_list

    def get_port_param_pairs(self):
        """get the port name together with the associated parameter measured"""
        return self.port_param_pairs

    def get_instrument_nb(self):
        """get the number of instrument in the hub"""
        return len(self.port_param_pairs)

    def get_connectable_ports(self):
        """get the names of all ports on the computer that see an instrument"""
        return list_serial_ports() +\
            self.prologix_com_port.get_open_gpib_ports() +\
            list_GPIB_ports()

    def set_debug_state(self, state):
        """change the DEBUG property of the IntrumentHub instance"""
        self.DEBUG = state
        logging.debug("debug mode of InstrumentHub Object :%s" % self.DEBUG)

    def clean_up(self):
        """ closes all instruments and reset the lists and dictionnaries """

        for port, inst in list(self.instrument_list.items()):
            try:

                logging.debug("Disconnect instrument %s, port %s" %
                              (inst, port))

            except AttributeError:
                # when the instrument is None (I have to check why we add a
                # port param with None connecting to None)
                pass

            # if the port is valid then we close the connection to the instrument
            if port:

                inst.close()

        self.instrument_list = {}
        self.port_param_pairs = []
        # I am not sure why this is useful anymore
        self.instrument_list[None] = None


def whoisthere():
    """
        try to connect to all ports availiable and send *IDN? command
        this is something than can take some time
    """

    if old_visa:

        port_addresses = visa.get_instruments_list()

    else:

        rm = visa.ResourceManager()
        port_addresses = rm.list_resources()

    connection_list = {}

    for port in port_addresses:

        try:

            print(port)
            device = MeasInstr(port)
            device.connection.timeout = 0.5
#            print port +" OK"
            try:

                name = device.identify()
                connection_list[port] = name

            except:

                pass

        except:

            pass

    return connection_list


def test_prologix_simple():
    import time
    ts = time.time()
    i = MeasInstr("GPIB0::7", interface=INTF_PROLOGIX)
    print(time.time() - ts)
    print(i.ask("*IDN?\n"))
    print(time.time() - ts)


def test_prologix_dual():
    import time
    ts = time.time()
    i = MeasInstr("GPIB0::7", interface=INTF_PROLOGIX)
    print(time.time() - ts)
    j = MeasInstr("GPIB0::12", interface=INTF_PROLOGIX, prologix=i.connection)
    print(time.time() - ts)
    print(i.ask("*IDN?\n"))
    print(time.time() - ts)
    print(j.ask("*IDN?\n"))
    print(time.time() - ts)


def test_prologix_Hub():

    h = InstrumentHub()  # prologix = PROLOGIX_COM_PORT)
    h.connect_hub(["CG500", "LS340", "PARO1000"],
                  ["GPIB0::7", "GPIB0::12", "COM4"],
                  ["HeLevel", "A", "PRESSURE"]
                  )

    insts = h.get_instrument_list()

    for inst in insts:

        if inst is not None:

            print(insts[inst].identify())

    print(h.get_prologix_gpib_ports())


def test_hub_debug_mode(i=0):
    h = InstrumentHub()
    h.DEBUG = True
    if i == 0:
        h.connect_hub(['TIME', 'DICE', 'TIME'], [
                      '', 'COM14', ''], ['Time', 'Roll', 'dt'])
    elif i == 1:
        h.connect_hub(['TIME', 'DICE', 'TIME'], [
            'COM2', 'COM14', 'COM1'], ['Time', 'Roll', 'dt'])


def test_hub_connect_inst():
    h = InstrumentHub()
    h.DEBUG = False
    h.connect_hub(['TIME', 'PARO1000', 'PARO1000', 'TIME'], [
                  'COM1', 'COM4', '132.206.186.166:48371:COM4', ''], ['Time', 'PRESSURE', 'PRESSURE', 'dt'])

    print(h.instrument_list)
    print(h.port_param_pairs)


def test_hub_connect_virtual_inst():
    h = InstrumentHub()
    h.DEBUG = False
    h.connect_hub(
        ['TIME', 'PARO1000', 'LS370', 'TIME'],
        ['COM1', '132.206.186.166:48372:COM4', '132.206.186.71:48371:GPIB0::12::INSTR', ''],
        ['Time', '4K flange', '50K flange', 'dt']
        )

    print(h.instrument_list)
    print(h.port_param_pairs)

#    ls = h.instrument_list['132.206.186.71:48371:GPIB0::12::INSTR']
#    print ls.measure('4K flange')
#    print ls.measure('50K flange')
    ls = h.instrument_list['132.206.186.166:48372:COM4']

    print(ls.use_method("measure", 2, 87))
    print(ls.use_method("identify", 3, 87))
    print(ls.resource_name)


if __name__ == "__main__":

    #    test_prologix_dual()
    #    test_prologix_Hub()
    #    test_hub_debug_mode(1)
    test_hub_connect_virtual_inst()
#    instr_hub=InstrumentHub(debug=True)

#    instr_hub.connect_hub(["CG500"],["COM1"],["HeLevel"])
#    i=MeasInstr('GPIB0::23::INSTR')
#    print i.identify()


#    from PyQt4.QtGui import QApplication
#    import sys
#    app = QApplication(sys.argv)
#    ex = SimpleConnectWidget()
#    ex.show()
#    sys.exit(app.exec_())
