# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 01:30:02 2018

@author: pfduc
"""
from importlib import import_module
import unittest

from LabDrivers import utils


def function_hdr(func):
    def new_function(*args, **kwargs):
        print("\n### %s ###\n" % func.__name__)
        return_value = func(*args, **kwargs)
        print("\n### %s ###\n" % ('-' * len(func.__name__)))
        return return_value
    return new_function


class LabDriversTest(unittest.TestCase):
    #
    #
    #    '''Test the LabGui GUI'''
    def setUp(self):
        """Create the GUI"""

        self.instrument_drivers = utils.list_drivers()[0]

    @function_hdr
    def test_import_driver(self):

        for instr_name in self.instrument_drivers:

            class_inst = import_module("." + instr_name,
                                       package=utils.LABDRIVER_PACKAGE_NAME)

            try:
                interface = class_inst.INTERFACE
            except:
                print("%s doesn't seem to have an INTERFACE..." % (instr_name))
                interface = utils.INTF_NONE

            if interface in [utils.INTF_SERIAL, utils.INTF_PROLOGIX, utils.INTF_VISA, utils.INTF_NONE]:
                pass
            else:
                print("%s doesn't seem to have correct interface (%s)..." %
                      (instr_name, interface))

    @function_hdr
    def test_params_driver(self):

        for instr_name in self.instrument_drivers:

            class_inst = import_module("." + instr_name,
                                       package=utils.LABDRIVER_PACKAGE_NAME)

            try:

                params = class_inst.param

            except:
                print("%s doesn't seem to have params..." % instr_name)
                params = []

    @function_hdr
    def test_connect_driver(self):

        for instr_name in self.instrument_drivers:

            class_inst = import_module("." + instr_name,
                                       package=utils.LABDRIVER_PACKAGE_NAME)

            interface = class_inst.INTERFACE

            if interface == utils.INTF_PROLOGIX:

                interface = utils.INTF_VISA
                obj = class_inst.Instrument('COM1', True, interface=interface)

            else:

                obj = class_inst.Instrument('COM1', True)

    @function_hdr
    def test_driver_name(self):

        for instr_name in self.instrument_drivers:

            class_inst = import_module("." + instr_name,
                                       package=utils.LABDRIVER_PACKAGE_NAME)

            interface = class_inst.INTERFACE

            if interface == utils.INTF_PROLOGIX:

                interface = utils.INTF_VISA
                obj = class_inst.Instrument('COM1', True, interface=interface)

            else:

                obj = class_inst.Instrument('COM1', True)

            self.assertEqual(obj.ID_name, instr_name)

    @function_hdr
    def test_measure_params(self):

        for instr_name in self.instrument_drivers:

            class_inst = import_module("." + instr_name,
                                       package=utils.LABDRIVER_PACKAGE_NAME)

            interface = class_inst.INTERFACE

            if interface == utils.INTF_PROLOGIX:
                interface = utils.INTF_VISA
                obj = class_inst.Instrument('COM1', True, interface=interface)
            else:
                obj = class_inst.Instrument('COM1', True)

            try:
                params = class_inst.param
            except:
                params = []

            for param in params:
                try:
                    obj.measure(param)
                except:
                    print("%s of %s doesn't seem to be measurable in debug mode..." % (
                        param, instr_name))


if __name__ == "__main__":

    unittest.main()
