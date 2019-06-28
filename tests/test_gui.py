# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:23:23 2017

@author: admin
"""
import sys
import unittest
import os
import time
from LocalVars import USE_PYQT5, MAIN_DIR
if USE_PYQT5:
    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt
else:
    import PyQt4.QtGui as QtGui
    from PyQt4.QtTest import QTest
    from PyQt4.QtCore import Qt
import LabGui

from LabGuiExceptions import DTT_Error, ScriptFile_Error

app = QtGui.QApplication(sys.argv)

from LabTools.IO import IOTool

TEST_CONFIG_FNAME = "config_test.txt"

TEST_SIMPLE_SCRIPT_FNAME = "script_test.py"

TEST_LOOP_SCRIPT_FNAME = "script_test_DTT.py"

TEST_EMPTY_FILE_FNAME = "empty_file_test.dat"

TEST_LOAD_DATA_FNAME = "data_file_test.dat"

# relaunches the application


def function_hdr(func):
    def new_function(*args, **kwargs):
        print("\n### %s ###\n" % func.__name__)
        return_value = func(*args, **kwargs)
        print("\n### %s ###\n" % ('-'*len(func.__name__)))
        return return_value
    return new_function


def relaunch():
    app.quit()
    # app.exec_()


def create_test_setting_file(fname="test_settings.set"):
    """create a file with settings so the test can be run anywhere"""

    settings_file = open(os.path.join("settings", fname), 'w')

    lines = [
        "dt(s), TIME, , dt, 'dt(s)', 0, 0, 0, 0, 0, #4477AA, 'None', '-'\n",
        "Roll(), DICE, COM14, Roll, 'Roll()', 0, 0, 0, 0, 0, #DDCC77, 'None', '-'\n",
        "Roll(), DICE, COM14, Roll, 'Roll()', 0, 0, 0, 0, 0, #DDCC77, 's', '-'\n",
        "Roll(), DICE, COM14, Roll, 'Roll()', 0, 0, 0, 0, 0, #DDCC77, 'None', '-'\n",
        "PRESSURE(psi), PARO1000, GPIB0::01, PRESSURE, 'PRESSURE(psi)', 0, 0, 0, \
        0, 0, #CC6677, 'None', '-'"
    ]

    settings_file.writelines(lines)

    settings_file.close()


def create_test_load_data_file(fname=TEST_LOAD_DATA_FNAME):

    data_file = open(fname, "w")
    lines=[
        "#C'dt(s)', 'Roll()'\n",
        "#I'TIME[].dt', 'DICE[COM1].Roll'\n",
        "#P'dt', 'Roll'\n",
        "0.0\t1.0\n",
        "1.0\t6.0\n",
        "2.0\t4.0\n",
        "3.0\t3.0\n"
    ]
    data_file.writelines(lines)

    data_file.close()


def create_test_empty_file(fname=TEST_EMPTY_FILE_FNAME):

    empty_file = open(fname, "w")
    empty_file.write("")
    empty_file.close()


def create_test_script_file(fname, lines):
    """create script file for testing purposes"""

    script_file = open(os.path.join("scripts", fname), 'w')

    script_file.writelines(lines)

    script_file.close()


def create_test_scripts():
    lines = [
        "self.read_data()\n",
        "time.sleep(1)"
    ]
    create_test_script_file(TEST_SIMPLE_SCRIPT_FNAME, lines)

    lines = [
        "while self.isStopped() == False:\n",
        "\tself.read_data()\n",
        "\ttime.sleep(1)\n",
        "\tself.check_stopped_or_paused()"
    ]
    create_test_script_file(TEST_LOOP_SCRIPT_FNAME, lines)


def create_test_config_file(fname=TEST_CONFIG_FNAME):
    """create a file with settings so the test can be run anywhere"""

    cwd = os.getcwd()

    config_path = os.path.join(cwd, fname)

    # create a config file
    IOTool.create_config_file(config_path)

    # change the value of the debug mode
    IOTool.set_config_setting(IOTool.DEBUG_ID, True,
                              config_file_path=config_path)

    # change the name of the script file
    script_path = IOTool.get_script_name(config_file_path=config_path)

    script_path = os.path.dirname(script_path)

    script_path = os.path.join(script_path, TEST_SIMPLE_SCRIPT_FNAME)

    IOTool.set_config_setting(IOTool.SCRIPT_ID, script_path,
                              config_file_path=config_path)


def delete_test_generated_files():

    cwd = os.getcwd()
    os.remove(os.path.join('scripts', TEST_SIMPLE_SCRIPT_FNAME))
    os.remove(TEST_EMPTY_FILE_FNAME)
    os.remove(TEST_LOAD_DATA_FNAME)
#                           script_test.py
#    IOTool.SCRIPT_ID

    # SAVE_DATA_PATH_ID = "DATA_PATH"
    # SETTINGS_ID = "SETTINGS"
    # WIDGETS_ID = "USER_WIDGETS"
    # LOAD_DATA_FILE_ID = "DATAFILE"
    # GPIB_INTF_ID = "GPIB_INTF"


class LabGuiTest(unittest.TestCase):
    #
    #
    #    '''Test the LabGui GUI'''
    def setUp(self):
        """Create the GUI"""
        print("")
        print("%"*20)
        print("Test setup")
        print("%"*20)
        print("")
        # create a configuration file specially for the tests

        self.form = LabGui.LabGuiMain(['-c', 'config_test.txt'])

        # the button for starting the DTT
        self.widget_start = self.form.instToolbar.widgetForAction(
            self.form.start_DTT_action)

        # the button for pausing the DTT
        self.widget_pause = self.form.instToolbar.widgetForAction(
            self.form.pause_DTT_action)

        # the button for stopping the DTT
        self.widget_stop = self.form.instToolbar.widgetForAction(
            self.form.stop_DTT_action)

        # the button for taking a simple measure
        self.widget_single_read = self.form.instToolbar.widgetForAction(
            self.form.read_DTT)

        # the button for loading previous data
        self.widget_load_data = self.form.instToolbar.widgetForAction(
            self.form.file_load_data_action)

        self.setting_fname = "test_settings.set"

#    def test_no_plot_window(self):
#        '''Test that there is no window at the start
#        '''
#
#        self.assertRaises(IndexError, self.form.get_last_window())
#

    def set_simple_instrument_list(self, instr_name='DICE',
                                   instr_port='COM99',
                                   instr_param='Roll',
                                   connect=False):
        """Populate the InstrumentWidget with 3 instruments

            The one in the middle is userdefined, the other are time and dt
            if connect is set to True, the button connect will be clicked

        """

        instr_widget = self.form.widgets['InstrumentWidget']

        instr = ['TIME', instr_name, 'TIME']
        port = ['', instr_port, '']
        param = ['Time', instr_param, 'dt']

        # check the number of instrument lines
        num_lines = len(instr_widget.lines)

        if num_lines > 3:

            # remove any excess from 3
            while num_lines != 3:

                QTest.mouseClick(instr_widget.bt_remove_last, Qt.LeftButton)
                num_lines = len(instr_widget.lines)

        elif num_lines < 3:

            # add up to 3 lines
            while num_lines != 3:

                QTest.mouseClick(instr_widget.bt_add_line, Qt.LeftButton)
                num_lines = len(instr_widget.lines)

        # Fill the lines with Time and dt sandwiching the instrument
        for i in range(len(instr)):

            # instrument name
            cbb = instr_widget.lines[i].instr_name_cbb
            QTest.keyClicks(cbb, instr[i])

            # instrument port
            cbb = instr_widget.lines[i].port_cbb
            # find the empty port
            cbb.setCurrentIndex(cbb.findText(''))
            QTest.keyClicks(cbb, port[i])

            # instrument parameter
            cbb = instr_widget.lines[i].param_cbb
            QTest.keyClicks(cbb, param[i])

        if connect:
            # Click on connect
            QTest.mouseClick(instr_widget.bt_connecthub, Qt.LeftButton)

    def set_script_fname(self, fname):
        """changed the script fname with one located in \scripts"""

        script_widget = self.form.widgets['ScriptWidget']

        cdir = os.path.abspath(os.path.curdir)

        fname = os.path.join(cdir, "tests", "scripts", fname)

        # erase the text in the lineEdit
        script_widget.scriptFileLineEdit.setText('')

        # write the script fname in the lineEdit
        QTest.keyClicks(script_widget.scriptFileLineEdit, fname)

        return fname

    # sets the script to the example script; avoids code repetition below
    def use_example_script(self):
        script = self.form.widgets['ScriptWidget'].scriptFileLineEdit
        for i in range(len(script.text())):
            QTest.keyClick(script, Qt.Key_Backspace)
        QTest.keyClicks(script, "%s/script_example.py" % (os.getcwd()))


    @function_hdr
    def test_load_data_not_existing_file(self):
        """test that it raises the correct exception"""
        with self.assertRaises(FileNotFoundError):
            self.form.create_plw("not_existing_file")

    @function_hdr
    def test_load_data_empty_file(self):
        """test that it raises the correct exception"""
        self.form.create_plw(TEST_EMPTY_FILE_FNAME)


    @function_hdr
    def test_load_good_format_data_file(self):
        """test that it doesn't raises exception"""
        self.form.create_plw(TEST_LOAD_DATA_FNAME)

if __name__ == "__main__":

    create_test_config_file()
    create_test_scripts()
    create_test_empty_file()
    create_test_load_data_file()
    unittest.main()

#    os.remove(TEST_CONFIG_FNAME)
#    test_start_normal()

#    test_config_option_missing()

#    test_config_option_wrong_type()
#
#    test_config_option_file_not_exists()
#
#    test_config_option_wrong_file()

#    test_config_option_multiple_file()

#    test_config_option_correct()
