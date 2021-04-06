# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 11:53:50 2016

Modified on Jun 20 2019

@author: schmidtb, pfduc, zackorenberg


This module contains useful fonctions and classes related to instrument connectic and drivers management
The interfaces we use are defined with the prefix INTF 

"""
import os
import inspect

from importlib import import_module
import logging

import glob
import sys

try:

    import serial
    serial_available = True

except ImportError:

    serial_available = False
    print("pyserial package not installed, run 'pip install pyserial'")

try:

    import visa
    visa_available = True

except ImportError:

    visa_available = False
    print("pyvisa package not installed, run 'pip install pyvisa'")

from LabTools.IO import IOTool

INTF_VISA = 'pyvisa'
INTF_PROLOGIX = 'prologix'
INTF_GPIB = IOTool.get_interface_setting()
INTF_SERIAL = 'serial'

VISA_BACKEND = IOTool.get_visa_backend_setting()

INTF_NONE = 'None'

PROLOGIX_COM_PORT = "COM5" # TODO: make/check dynamic
# cf section 8.2 of the manual : http://prologix.biz/downloads/PrologixGpibUsbManual-6.0.pdf
PROLOGIX_AUTO = 'prologix_auto_opt'
PROLOGIX_BAUD = 115200 # apparently, this is meaningless

PROLOGIX_SEARCH_PORTS = True

LABDRIVER_PACKAGE_NAME = "LabDrivers"

old_visa = True

# Check for python version; required to determine whether to include
# byte-like objects.
PYTHON_3 = False

if sys.version_info[0] == 3:
    PYTHON_3 = True

try:
    # poke at something that only exists in older versions of visa, as a probe for the version
    visa.term_chars_end_input
#    logging.info("using pyvisa version less than 1.6")
except:
    old_visa = False
#    logging.info("using pyvisa version higher than 1.6")


def list_GPIB_ports():
    """ Load VISA resource list for use in combo boxes """
    try:
        if old_visa:
            available_ports = visa.get_instruments_list()
        else:

            rm = visa.ResourceManager(VISA_BACKEND)
            available_ports = rm.list_resources()
            temp_ports = []
            for port in available_ports:
                if "GPIB" in port:
                    temp_ports.append(str(port))
            available_ports = temp_ports
    except:
        available_ports = []

    if PROLOGIX_SEARCH_PORTS:
        pc = PrologixController()
        #if pc.connection is not None:
        available_ports = available_ports + pc.get_open_gpib_ports()
#    pc = PrologixController(com_port = PROLOGIX_COM_PORT)
#    available_ports = available_ports + pc.get_open_gpib_ports()

    return available_ports


def list_serial_ports(max_port_num=20):
    """ Lists serial port names from COM1 to COM20 in windows platform and 
    lists all serial ports on linux platform

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(max_port_num)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port, 9600, timeout=0.1)
            logging.debug("Serial connection established with %s"%port)
            result.append(str(port))
            s.close()

        except (OSError, serial.SerialException):
            pass

    return result


def refresh_device_port_list(debug=False):
    """ Load VISA resource list for use in combo boxes """

    if debug:

        return ["GPIB0::%i" % i for i in range(30)]

    else:

        return list_GPIB_ports() + list_serial_ports()


def find_prologix_ports():
    """
        go through the serial ports and wee which one returns the prologix
        version command
    """

    serial_ports = list_serial_ports()

    result = []
    for port in serial_ports:
        try:
            s = serial.Serial(port, PROLOGIX_BAUD, timeout=0.2)
            if PYTHON_3:
                s.write('++mode 1\n++auto 1\n++ver\n'.encode())
            else:
                s.write('++mode 1\n++auto 1\n++ver\n')

            answer = s.readline()

            PROLOGIX_CONTROLLER = 'Prologix GPIB-USB Controller'

            if PYTHON_3:
                PROLOGIX_CONTROLLER = PROLOGIX_CONTROLLER.encode()

            if PROLOGIX_CONTROLLER in answer:
                result.append(port)
        except(OSError, serial.SerialException):
            pass

    return result


def is_IP_port(device_port, return_vals=False):
    """
        decides whether the given port can be considered as an IP address with
        a port and a unique identifier (for client instrument use)
    """

    # I should make sure I identify the IP device port in a unique way
    # maybe the presence of two ":" character plus the presence of three "." in
    # the IP part should be good enough
    # IP:ip_port:device_port
    # IP : IP address XXX.XXX.XXX.XXX
    # port : something like 4XXXX
    # device_port, the device port of the instrument which has a physical
    # connection on the server side (to be able to uniquely identify)
    info = device_port.split(':')

    # format should be IP:ip_port:device_port
    if len(info) == 3:

        ip, ip_port, device_port = info

    # if device_port contains ':' it might be still a correct format
    elif len(info) > 3:

        # gets the first two parameters, IP and ip_port
        ip, ip_port = info[0:2]

        # the beginning of the server_port
        device_port = info[2]

        # iterate through successive instances of ':' to get the server_port
        for part in info[3:]:

            device_port = '%s:%s' % (device_port, part)

    else:
        # format of the input is wrong
        return False

    # the IP address should have 3 dots and 4 components
    ip_nums = ip.split('.')

    if len(ip_nums) == 4:

        for ip_num in ip_nums:

            # test if the component is a number
            try:

                num = int(ip_num)

            except ValueError:
                # the component isn't an integer number
                return False

            # test if the component is between 0 and 255
            if num < 0 or num > 255:

                return False

    else:
        # the format of the IP address is wrong
        return False

    # test the format of the port number
    try:

        int(ip_port)

    except ValueError:
        # the port isn't an integer number
        return False

    # the device port can oly be a COM or a GPIB port
    if not ("COM" in device_port or "GPIB" in device_port):
        logging.warning("The device port '%s' you specified is not GPIB nor \
COM" % device_port)
        return False

    if return_vals:
        return ip, int(ip_port), device_port
    else:
        return True

def get_driver_list():
    """
        Returns a list of all files in driver folder, minus utils.py, Tool.py and __init__.py

        Designed to replace:

            my_path = inspect.getfile(list_drivers).rstrip('utils.py')
            driver_files = os.listdir(my_path)

        with

            driver_files = get_driver_list()

        in

            list_properties
            list_functions
            list_plot_axes
            list_drivers

    """
    # Perhaps the implemented method is better?
    #my_path = inspect.getfile(list_drivers).rstrip('utils.py')
    #another option would be using pathlib.Path(__file__).parent, however I believe this should work
    my_path = os.path.dirname(__file__)
    driver_files = os.listdir(my_path)
    if 'Tool.py' in driver_files:
        driver_files.remove('Tool.py')
    if '__init__.py' in driver_files:
        driver_files.remove('__init__.py')
    if 'utils.py' in driver_files:
        driver_files.remove('utils.py')

    return driver_files

def list_driver_properties():
    """
        This returns a dictionary of all drivers that have properties dictionary in form:
        return {
            'NAME': object
        }
    """
    interface = [INTF_VISA, INTF_PROLOGIX, INTF_SERIAL]

    properties = {}

    # list all the .py files in the drivers folder
    driver_files = get_driver_list()

    for file_name in driver_files:

        if file_name.endswith('.py') \
                and (
                not file_name == 'Tool.py' and not file_name == '__init__.py' and not file_name == 'utils.py'):  # yikes
            name = file_name.split('.py')[0]

            # import the module of the instrument in the package drivers
            driver = import_module('.' + name, package=LABDRIVER_PACKAGE_NAME)

            try:
                driver_interface = driver.INTERFACE

            except AttributeError:
                logging.error(
                    "The following module is probably not an instrument driver, "
                    "please remove it from the package %s" % LABDRIVER_PACKAGE_NAME
                )
                driver_interface = ''

            if hasattr(driver, 'properties'):
                properties[name] = driver.properties

    return properties

def list_driver_functions():
    """
        This returns a dictionary of all drivers that have function dictionary in form:
        return {
            'NAME': object
        }
    """
    interface = [INTF_VISA, INTF_PROLOGIX, INTF_SERIAL]

    functions = {}

    # list all the .py files in the drivers folder
    driver_files = get_driver_list()

    for file_name in driver_files:

        if file_name.endswith('.py') \
                and (
                not file_name == 'Tool.py' and not file_name == '__init__.py' and not file_name == 'utils.py'):  # yikes
            name = file_name.split('.py')[0]

            # import the module of the instrument in the package drivers
            driver = import_module('.' + name, package=LABDRIVER_PACKAGE_NAME)

            try:
                driver_interface = driver.INTERFACE

            except AttributeError:
                logging.error(
                    "The following module is probably not an instrument driver, "
                    "please remove it from the package %s" % LABDRIVER_PACKAGE_NAME
                )
                driver_interface = ''

            if hasattr(driver, 'functions'):
                functions[name] = driver.functions

    return functions

def list_driver_plot_axes():
    """
            This returns a dictionary of all axes labels for drivers that have function dictionary in form:
            return {
                'NAME': [axes list] -or- None
            }
        """
    interface = [INTF_VISA, INTF_PROLOGIX, INTF_SERIAL]


    plot = {}

    # list all the .py files in the drivers folder
    driver_files = get_driver_list()

    for file_name in driver_files:

        if file_name.endswith('.py') \
                and (
                not file_name == 'Tool.py' and not file_name == '__init__.py' and not file_name == 'utils.py'):  # yikes
            name = file_name.split('.py')[0]

            # import the module of the instrument in the package drivers
            driver = import_module('.' + name, package=LABDRIVER_PACKAGE_NAME)

            try:
                driver_interface = driver.INTERFACE

            except AttributeError:
                logging.error(
                    "The following module is probably not an instrument driver, "
                    "please remove it from the package %s" % LABDRIVER_PACKAGE_NAME
                )
                driver_interface = ''

            if hasattr(driver, 'functions'):
                if hasattr(driver, 'plot'):
                    plot[name] = driver.plot
                else:
                    plot[name] = None

    return plot


def list_drivers(interface=[INTF_VISA, INTF_PROLOGIX, INTF_SERIAL, INTF_NONE]):
    """
        Returns the drivers names, their parameters and the corresponding 
        units of all drivers modules in this folder.
        The driver module needs to contain a class "Instrument" and a 
        dictionnary "param" containing the different parameters and their units.
    """

    if interface == 'real':
        interface = [INTF_VISA, INTF_PROLOGIX, INTF_SERIAL]

    instruments = []
    params = {}
    units = {}
    params[''] = []

    # list all the .py files in the drivers folder
    driver_files = get_driver_list()

    for file_name in driver_files:

        if file_name.endswith('.py') \
                and (not file_name == 'Tool.py' and not file_name == '__init__.py' and not file_name == 'utils.py'): #yikes
            name = file_name.split('.py')[0]

            # import the module of the instrument in the package drivers
            driver = import_module('.' + name, package=LABDRIVER_PACKAGE_NAME)

            try:
                driver_interface = driver.INTERFACE

            except AttributeError:
                logging.error(
                    "The following module is probably not an instrument driver, "
                    "please remove it from the package %s" % LABDRIVER_PACKAGE_NAME
                )
                driver_interface = ''

            if driver_interface in interface:
                # add to instruments list
                instruments.append(name)

                # create an array for the parameters
                params[name] = []
                #properties[name] = {}

                # load the parameters and their units from the module
                try:
                    for chan, u in list(driver.param.items()):
                        units[chan] = u
                        params[name].append(chan)

                except:
                    logging.error(('Invalid driver file: ' +
                                   file_name + ' (no param variable found)'))

                # add properties if it exists
                #if hasattr(driver, 'properties'):
                #    properties[name] = driver.properties

    return [instruments, params, units]


def test_prologix_controller_creation_with_com(com_port=None):
    if com_port is None:
        com_port = 'COM3'

    pc = PrologixController(com_port)
    print(pc)
    print(pc.get_open_gpib_ports())


def test_prologix_controller_creation_with_wrong_com():
    pc = PrologixController('COM1')
    print(pc)
    print(pc.get_open_gpib_ports())


def test_prologix_controller_creation_with_no_arg_conflict():
    pc = PrologixController()
    print(pc)
    pc2 = PrologixController()
    print(pc2)


class PrologixController(object):
    """
    This class is an attempt to mimic the visa.Resource class. Specifically, visa.GPIBInstrument class, with documentation here:
    https://pyvisa.readthedocs.io/en/latest/api/resources.html#pyvisa.resources.GPIBInstrument
    TODO:   - implement lock
            - implement event callbacks
            - implement specific control commands (currently only local)

    Prologix GPIB-To-USB User manual is given here:
        http://prologix.biz/gpib-usb-3.x-manual.html
    """
    connection = None

    def __init__(
            self,
            com_port=None,
            debug=False,
            auto=1,
            baud_rate=PROLOGIX_BAUD,
            timeout=0.5,
            **kwargs
    ):

        self.debug = debug

        if not self.debug:
            if com_port is None:
                # the user didn't provide a COM port, so we look for one
                com_port = find_prologix_ports()

                if com_port:
                    if len(com_port) > 1:

                        logging.warning('There is more than one Prologix \
                         controller, we are connecting to %s' % com_port[0])

                    com_port = com_port[0]
                    logging.info(
                        "... found a Prologix controller on the port '%s'" %
                        com_port
                    )

                    try:
                        self.connection = serial.Serial(
                            com_port,
                            baud_rate,
                            timeout=timeout
                        )
                    except serial.serialutil.SerialException:
                        self.connection = None

                        logging.error(
                            'The port %s is not attributed to any device' % com_port
                        )
                else:
                    self.connection = None
                    logging.warning(
                        'There is no Prologix controller to connect to')

            else:

                try:
                    self.connection = serial.Serial(
                        com_port,
                        baud_rate,
                        timeout=timeout
                    )
                except serial.serialutil.SerialException:
                    self.connection = None

                    logging.error(
                        'The port %s is not attributed to any device' % com_port
                    )

            if self.connection is not None:
                # set the connector in controller mode and let the user

                self.write("++mode 1")
                # auto == 1 : ask for read without sending another command.
                # auto == 0 : simply send the command.
                self.auto = auto
                self.write("++auto %i" % self.auto)

                # check the version
                self.write("++ver")
                # important not to use the self.readline() method
                # at this stage if auto == 0, otherwise the connector is going
                # to prompt the instrument for a reading an generate an error
                version_number = (self.connection.readline()).decode()

                if 'Prologix GPIB-USB Controller' not in version_number:
                    self.connection = None
                    logging.error(
                        "The port %s isn't related to a Prologix controller "
                        "(try to plug and unplug the cable if it is there "
                        "nevertheless). Returned version number : %s" % (
                            com_port,
                            version_number
                        )
                    )
                logging.info(
                    "%s is connected on the port '%s'"
                    % (version_number[:-2], com_port)
                )
            else:
                logging.error('The connection to the Prologix connector failed')
        self.assertren = None
        self.ren_level = None
    def __str__(self):
        return self.controller_id()
        #print("you should not arrive at this") # to isolate error
        #return '0'
        #if self.connection is not None:
        #    self.write("++ver")
        #    return (self.connection.readline()).decode()
        #else:
        #    return ''

    def __getattr__(self, name): # catch-all for non-supported functions
        def method(*args):
            pstring = "%s is currently not supported under Prologix. "%name
            if args:
                pstring += "Called with arguments %s"%str(args)
            print(pstring)
        return method

    def controller_id(self):
        #return self.__str__() changed as having __str__ defined was causing errors
        if self.connection is not None:
            self.write('++ver')
            return (self.connection.readline()).decode()
        else:
            return ''

    def write(self, cmd):
        """use serial.write"""
        # add a new line if the command didn't have one already
        if not cmd.endswith('\n'):
            cmd += '\n'
        if self.connection is not None:
            logging.debug("Prologix in : %s" % cmd)
            self.connection.write(cmd.encode())
        else:
            logging.info("There is no prologix connection. Consider restarting LabGUI.")
    def readline(self):
        """ temp fix cuz pyserial dumb"""
        return self.read(128)
    def read(self, num_bit=0): # ADDED NUM_BIT==0 INVOKES READLINE LIKE IT WOULD WITH PYVISA
        """use serial.read"""
        if self.connection is not None:
            if num_bit == 0:
                return self.readline()
            if not self.auto:
                self.write('++read eoi'.encode())
            answer = self.connection.read(num_bit)
            logging.debug("Prologix out (read) : %s" % answer)
            if answer == b'':
                answer = 'nan'.encode()
            return answer.decode()
        else:
            logging.info("There is no prologix connection. Consider restarting LabGUI.")
            return '' # to fix conversion issues

    def readline(self):
        """use serial.readline"""
        if self.connection is not None:
            if not self.auto:
                self.write('++read eoi'.encode())
            answer = self.connection.readline()
            logging.debug("Prologix out (readline): %s " % answer)
            if answer == b'':
                answer = 'nan'.encode()
            return answer.decode()
        else:
            logging.info("There is no prologix connection. Consider restarting LabGUI.")
            return ''

    def ask(self, cmd):
        if self.connection is not None:
            self.write(cmd)
            return self.readline()
        else:
            return ''

    def query(self, cmd): # ask to be depricated
        return self.ask(cmd)

    def timeout(self, new_timeout=None):
        """
        query the timeout setting of the serial port if no argument provided
        change the timeout setting to new_timout if the latter is not None
        """
        if self.connection is not None:
            if new_timeout is None:
                return self.connection.timeout
            else:
                old_timeout = self.connection.timeout
                self.connection.timeout = new_timeout
                return old_timeout

    def get_open_gpib_ports(self, num_ports=30):
        """Finds out which GPIB ports are available for prologix controller"""
        open_ports = []
        if self.connection is None:
            return open_ports
        if not self.debug:

            # sets the timeout to quite fast
            old_timeout = self.timeout(0.1)
            # iterate the ports number
            for i in range(num_ports + 1):

                # change the GPIB address on the prologix controller
                # prove if an instrument is connected to the port
                self.write('++addr %i\n*IDN?\n' % i)

                # probe the answer
                s = self.readline()

                # if it is longer than zero it is an instrument
                # we store the GPIB address
                if len(s) > 0:
                    open_ports.append('GPIB0::%s::INSTR' % i) # should have INSTR for consistency

            # resets the timeout to its original value
            self.timeout(old_timeout)

        return open_ports

    def clear(self):
        self.write("++clr")

    def close(self):
        # TODO decide on what to do for this, as I am unsure if there is a close
        #self.write("++ifc") # interface clear
        #self.reset()
        pass

    def control_ren(self, level, addr = None):
        """
        :param level: REN mode, integer
        :param addr: GPIB address of device. If None, it will assert for all devices
        :return:
        ++loc and ++llo are located on page 11 of the GPIB USB manual, found here:
            https://prologix.biz/downloads/PrologixGpibUsbManual-6.0.pdf
        """
        if level is None:
            return
        ASSERT_REN = [1,3]
        DEASSERT_REN = [0,2]
        GTL = [2,6]
        LLO = [4,5]

        ADDR_DEV = [3,4]
        logging.debug("Currently, control_ren only asserts local mode")
        #### DO ASSERTS #####
        if level in ASSERT_REN:
            self.assertren = True
            logging.warning("Unabled to assert REN on prologix controller")
        elif level in DEASSERT_REN:
            self.assertren = False
            logging.warning("Unabled to deassert REN on prologix controller")
        if level in GTL:
            if level in ADDR_DEV and addr is not None:
                self.write('++loc %d'%addr)
            else:
                self.write('++loc')
        elif level in LLO:
            if level in ADDR_DEV and addr is not None:
                self.write('++llo %d'%addr)
            else:
                self.write('++llo')

        self.ren_level = level
    def reset(self):
        self.write("++rst")

def command_line_test(instrument_class):
    """
    Launch an interactive debugging session. The user is prompted to enter
    a port number to connect to. They can then enter commands (methods of 
    instrument_class), and the response is printed.

    Args:
        instrument_class (class): the class of instrument to be tested
    """

    print("\nWelcome to the LabDriver command line tester.")
    msg = "Use this tool to test if your instrument connects"
    msg += " and responds to commands."
    print(msg)

    stri = input("Please enter port to connect to: ")
    inst = instrument_class(stri)

    while True:
        stri = input("Enter command or type x to quit: ")
        if stri.lower() == 'x':
            break
        try:
            print(eval('inst.' + stri))
        except AttributeError:
            print("Command not recognized.")

    inst.close()


if __name__ == "__main__":
    print(get_driver_list())
    #print(find_prologix_ports())
    #test_prologix_controller_creation_with_no_arg_conflict()
    command_line_test(PrologixController)
    pass
