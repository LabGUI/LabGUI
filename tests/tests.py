# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:23:23 2017

@author: admin
"""
# import unittest
# import warnings
# os.chdir("..")
#
# import subprocess
#
# import sys
#
# from PyQt5.QtTest import QSignalSpy
#
# from time import sleep
#
#
# def test_start_normal():
#     print("Normal start")
#     os.system("python LabGui.py")
#
#
# def test_config_option_missing():
#     print("config_option_missing")
#     os.system("python LabGui.py -c")
#
#
# def test_config_option_wrong_type():
#     print("config_option_wrong_type")
#     os.system("python LabGui.py -c 12")
#
#
# def test_config_option_file_not_exists():
#     print("config_option_file_not_exists")
#     os.system("python LabGui.py -c Monsieur.txt")
#
#
# def test_config_option_wrong_file():
#     print("config_option_wrong_file")
#     os.system("python LabGui.py -c requirements.txt")
#
#
# def test_config_option_multiple_file():
#     print("config_option_multiple_file")
#     os.system("python LabGui.py -c requirements.txt config.txt")
#
#
# def test_config_option_correct():
#     print("config_option_correct")
#     os.system("python LabGui.py -c config_mass_spec_alone.txt")
#
#

# class TestConfigInlineOption(unittest.TestCase):
#
#    def test_config_option_file_not_exists(self):
#        print("config_option_file_not_exists")
#
#        with warnings.catch_warnings(record=True) as w:
#            # Cause all warnings to always be triggered.
#            warnings.simplefilter("always")
#            # Trigger a warning.
#            os.system("python LabGui.py -c Monsieur.txt")
#            # Verify some things
#            print(w)
#            assert issubclass(w[-1].category, UserWarning)
from LabTools.IO import IOTool
from LabGuiExceptions import DTT_Error, ScriptFile_Error
import LabGui
import sys
import unittest
import os
import time
from LocalVars import USE_PYQT5
if USE_PYQT5:
    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt
else:
    import PyQt4.QtGui as QtGui
    from PyQt4.QtTest import QTest
    from PyQt4.QtCore import Qt


app = QtGui.QApplication(sys.argv)


TEST_CONFIG_FNAME = "config_test.txt"

TEST_SIMPLE_SCRIPT_FNAME = "script_test.py"

TEST_LOOP_SCRIPT_FNAME = "script_test_DTT.py"
# relaunches the application


def function_hdr(func):
    def new_function(*args, **kwargs):
        print("\n### %s ###\n" % func.__name__)
        return_value = func(*args, **kwargs)
        print("\n### %s ###\n" % ('-' * len(func.__name__)))
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
        print("%" * 20)
        print("Test setup")
        print("%" * 20)
        print("")
        # create a configuration file specially for the tests

        self.form = LabGui.LabGuiMain(['-c', 'config_test.txt'])

        # the button for starting the DTT
        self.widget_start = self.form.instToolbar.widgetForAction(
            self.form.start_DTT_action)

        # the button for stoping the DTT
        self.widget_pause = self.form.instToolbar.widgetForAction(
            self.form.pause_DTT_action)

        # the button for stoping the DTT
        self.widget_stop = self.form.instToolbar.widgetForAction(
            self.form.stop_DTT_action)

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
    def test_number_of_instrument_connected_at_start(self):
        """the number of instrument connected at start should be 0"""

        num_instr = self.form.instr_hub.get_instrument_nb()

        self.assertEqual(num_instr, 0)

    @function_hdr
    def test_instr_widget_click_add_line_button(self):
        """click on the button 'Add line' should create a line"""

        # intrument widget instance
        instr_widget = self.form.widgets['InstrumentWidget']

        num_lines_before = len(instr_widget.lines)

        QTest.mouseClick(instr_widget.bt_add_line, Qt.LeftButton)

        num_lines_after = len(instr_widget.lines)

        # test that the number of lines increased by one
        self.assertEqual(num_lines_before + 1, num_lines_after)

    @function_hdr
    def test_instr_widget_click_connect_button(self):
        """
            check how many instuments are connected to the instrument hub
            after the user added an instrument line in the InstrumentWidget
            and clicked the InstrumentWidget 'Connect' button
        """

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        self.set_simple_instrument_list(connect=True)

        num_instr_after = self.form.instr_hub.get_instrument_nb()

        self.assertEqual(num_instr_after, 3)

    @function_hdr
    def test_change_script_name_changes_it_when_start_DTT(self):

        script_fname = self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        self.assertEqual(self.form.datataker.script_file_name, script_fname)

    @function_hdr
    def test_start_DTT_produce_a_file(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        # print the name of the data file
        ofname = self.form.output_file.name
        print("DTT output file : %s" % ofname)
    #        time.sleep(10)

    #        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

    @function_hdr
    def test_start_DTT_disable_start_button(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        self.assertFalse(self.form.start_DTT_action.isEnabled())

    @function_hdr
    def test_start_DTT_enable_stop_button(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        self.assertTrue(self.form.stop_DTT_action.isEnabled())

    @function_hdr
    def test_start_DTT_enable_pause_button(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        self.assertTrue(self.form.pause_DTT_action.isEnabled())

    @function_hdr
    def test_start_DTT_isrunning_true(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        self.assertTrue(self.form.datataker.isRunning())

    @function_hdr
    def test_start_DTT_isstopped_false(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        self.assertFalse(self.form.datataker.isStopped())

    @function_hdr
    def test_start_DTT_ispaused_false(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        self.assertFalse(self.form.datataker.isPaused())

    @function_hdr
    def test_pause_DTT_ispaused_true(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Pause the DTT
        QTest.mouseClick(self.widget_pause, Qt.LeftButton)

        time.sleep(0.1)

        self.assertTrue(self.form.datataker.isPaused())

    @function_hdr
    def test_pause_DTT_isrunning_true(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Pause the DTT
        QTest.mouseClick(self.widget_pause, Qt.LeftButton)

        time.sleep(0.1)

        self.assertTrue(self.form.datataker.isRunning())

    @function_hdr
    def test_pause_DTT_isstopped_false(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Pause the DTT
        QTest.mouseClick(self.widget_pause, Qt.LeftButton)

        time.sleep(0.1)

        self.assertFalse(self.form.datataker.isStopped())

    @function_hdr
    def test_pause_DTT_then_resume_isrunning_true_and_ispaused_false(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Pause the DTT
        QTest.mouseClick(self.widget_pause, Qt.LeftButton)

        # Resume the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        self.assertTrue((self.form.datataker.isRunning() is True)
                        and (self.form.datataker.isPaused() is False))

    @function_hdr
    def test_pause_DTT_then_stop_isrunning_false_and_isstopped_true(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Pause the DTT
        QTest.mouseClick(self.widget_pause, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        time.sleep(0.1)

        self.assertTrue((self.form.datataker.isRunning() is False)
                        and (self.form.datataker.isStopped() is True))

    @function_hdr
    def test_stop_DTT_enable_start_button(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        self.assertTrue(self.form.start_DTT_action.isEnabled())

    @function_hdr
    def test_stop_DTT_disable_stop_button(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        self.assertFalse(self.form.stop_DTT_action.isEnabled())

    @function_hdr
    def test_stop_DTT_disable_pause_button(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        time.sleep(0.1)

        self.assertFalse(self.form.pause_DTT_action.isEnabled())

    @function_hdr
    def test_stop_DTT_isrunning_false(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        time.sleep(0.1)

        self.assertFalse(self.form.datataker.isRunning())

    @function_hdr
    def test_stop_DTT_ispaused_false(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        time.sleep(0.1)

        self.assertFalse(self.form.datataker.isPaused())

    @function_hdr
    def test_stop_DTT_isstopped_true(self):

        # connect a DICE and two TIME
        self.set_simple_instrument_list(connect=True)

        print("Intruments in the hub")
        print(self.form.instr_hub.get_instrument_nb())

        # select a script which is a loop
        self.set_script_fname("script_test_DTT.py")

        # Start the DTT
        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        time.sleep(0.1)

        # Stop the DTT
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

        time.sleep(0.1)

        self.assertTrue(self.form.datataker.isStopped())

    @function_hdr
    def test_start_DTT_without_connecting_first(self):

        nb_instr = self.form.instr_hub.get_instrument_nb()

        if nb_instr == 0:

            # No instrument is connected to the Hub so there should be an error
            with self.assertRaises(DTT_Error):

                QTest.mouseClick(self.widget_start, Qt.LeftButton)

        else:

            raise(ValueError, "The instrument number should be 0")

    # @function_hdr
    # def test_start_DTT_with_non_existing_script(self):
    #
    #     # connect a DICE and two TIME
    #     self.set_simple_instrument_list(connect=True)
    #
    #     print("Intruments in the hub")
    #     print(self.form.instr_hub.get_instrument_nb())
    #
    #     # select a script which is a loop
    #     self.set_script_fname("this_script_does_not_exist.py")
    #
    #     with self.assertRaises(IOError):
    #         # Start the DTT
    #         QTest.mouseClick(self.widget_start, Qt.LeftButton)

    def test_dice_connect_and_play(self):
        """test the modification of the instrument list
        click connect to connect the instrument hub
        """

        self.set_simple_instrument_list()

        # Push OK with the left mouse button
        connect_bt = self.form.widgets['InstrumentWidget'].bt_connecthub
        QTest.mouseClick(connect_bt, Qt.LeftButton)

        self.assertEqual(1, 1)

    def test_save_instrument_settings(self):
        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("\ntest_save_instrument_settings\n")

        self.set_simple_instrument_list()

        self.form.file_save_settings(self.setting_fname)

        self.assertTrue(os.path.exists(self.setting_fname))

        ofs = open(self.setting_fname, 'r')

        for line in ofs:
            print(line)

    def test_load_instrument_settings(self):
        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        print("\ntest_load_instrument_settings\n")

        self.form.file_load_settings(self.setting_fname)

    #        if os.path.exists(self.setting_fname):
    #
    #            self.assertIsNotNone(self.form.plot_window_settings)

        self.assertEqual(self.form.instrument_connexion_setting_fname,
                         self.setting_fname)

        self.form.file_load_settings("doesnt_exist.fname")

        self.assertIsNone(self.form.plot_window_settings)

    # Shammamah's tests (incomplete!)
    # Tests connect button
    def test_add_remove(self):
        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        print("\ntest_add_remove\n")

        remove_bt = self.form.widgets['InstrumentWidget'].bt_remove_last
        add_bt = self.form.widgets['InstrumentWidget'].bt_add_line
        connect_bt = self.form.widgets['InstrumentWidget'].bt_connecthub

        QTest.mouseClick(add_bt, Qt.LeftButton)
        QTest.mouseClick(connect_bt, Qt.LeftButton)
        QTest.mouseClick(remove_bt, Qt.LeftButton)
        QTest.mouseClick(connect_bt, Qt.LeftButton)

    # Config file testing: save config settings -> see if settings are loaded correctly
    # check data path, script, settings, datafile, debug mode
    def test_config_debug(self):
        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("\ntest_config_debug\n")
        filemenu = self.form.fileMenu
        optionmenu = self.form.optionMenu
        change_debug = optionmenu.actions()[1]
        save_config = filemenu.actions()[4]

        print("\nChanging debug state...")
        change_debug.trigger()
        f = open("config.txt", "r")
        lines = f.readlines()
        for i in range(len(lines)):
            if "DEBUG" in lines[i]:
                print("config.txt: " + lines[i])
        f.close()
        print("\nChanging back debug state...")
        change_debug.trigger()
        f = open("config.txt", "r")
        lines = f.readlines()
        for i in range(len(lines)):
            if "DEBUG" in lines[i]:
                print("config.txt: " + lines[i])
        f.close()
        # save_config.trigger()

        #a = subprocess.check_output("type logging.conf | findstr 'DEBUG*'")
        # print(a)
        # close LabGui and reopen to see if settings have loaded correctly
        # not quite sure how to simulate closing the program

    # check if logger output level is changed correctly
    def test_logger_output_level(self):
        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("\ntest_logger_output_level\n")
        save_config = self.form.fileMenu.actions()[4]
        logmenu = self.form.loggingSubMenu.actions()
        debug = logmenu[0]
        info = logmenu[1]
        warning = logmenu[2]
        error = logmenu[3]

        for item in logmenu:
            print(item.iconText())

        print("\nToggling debug...")
        debug.trigger()
        # save_config.toggle()

        print("\nToggling info...")
        info.trigger()

        print("\nToggling warning...")
        warning.trigger()

        print("\nToggling error...")
        error.trigger()

    def test_relaunch(self):
        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("\ntest_relaunch\n")
        relaunch()

    # Tests from utils.py
    # (raising errors if the functions are copy/pasted into this file;
    #   right now, I just call the test functions in utils.py from here)

    # print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # print("\ntest_prologix_controller_creation_with_com\n")
    # utils.test_prologix_controller_creation_with_com(com_port=None)
    #
    # print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # print("\ntest_prologix_controller_creation_with_wrong_com\n")
    # utils.test_prologix_controller_creation_with_no_arg_conflict()
    #
    # print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # print("\ntest_prologix_controller_creation_with_no_arg_conflict()\n")
    # utils.test_prologix_controller_creation_with_wrong_com()

# Logger output level
# Change debug mode
# Test for successful output to console

    # @function_hdr
    # def test_bad_script(self):
    #     """check if bad scripts are handled correctly"""
    #
    #     script = self.form.widgets['ScriptWidget'].scriptFileLineEdit
    #
    #     # create invalid scripts
    #     f = open("%s/tests/syntaxError.py" % os.getcwd(), "w+")
    #     f.write("prnt(\"this script doesn't compile\")")
    #     f.close()
    #     f = open("%s/tests/notapythonscript.c" % os.getcwd(), "w+")
    #     f.write("printf(\"%s\",\"this is the wrong filetype\");")
    #     f.close()
    #
    #     badScripts = [
    #        # "%s/tests/notarealscript.py" % os.getcwd(),
    #         "%s/tests/notapythonscript.c" % os.getcwd(),
    #         "%s/tests/syntaxError.py" % os.getcwd(),
    #         "%s/script_example.py" % os.getcwd()
    #     ]
    #
    #     print(badScripts)
    #     for badScriptName in badScripts:
    #         # Change the script name
    #         for i in range(len(script.text())):
    #             QTest.keyClick(script, Qt.Key_Backspace)
    #         QTest.keyClicks(script, badScriptName)
    #         print("\nTesting %s\n" % script.text())
    #         with self.assertRaises(ScriptFile_Error) as context:
    #             QTest.mouseClick(self.widget_start, Qt.LeftButton)
    #             # this test gets buggy when there is no delay
    #             time.sleep(1)
    #             # need to ensure that the errors lead to the re-enabling
    #             # of the stop button, and the disabling of the
    #             # stop/pause buttons
    #             self.assertTrue(self.form.start_DTT_action.isEnabled() and
    #                             not self.form.pause_DTT_action.isEnabled() and
    #                             not self.form.stop_DTT_action.isEnabled())
    #
    #     os.remove("syntaxError.py")
    #     os.remove("notapythonscript.c")

    @function_hdr
    def test_debug_datataker(self):
        self.use_example_script()

        change_debug = self.form.optionmenu.actions()[1]
        for i in range(2):
            change_debug.toggle()
        self.set_simple_instrument_list(connect=True)
        QTest.mouseClick(self.widget_start, Qt.LeftButton)
        time.sleep(3)
        QTest.mouseClick(self.widget_stop, Qt.LeftButton)
        # how to test if there is any data being generated?

    @function_hdr
    def test_data_generated_datataker(self):

        self.use_example_script()

        self.set_simple_instrument_list(connect=True)

        dataGenerated = QSignalSpy(self.form.data_array_updated)

        QTest.mouseClick(self.widget_start, Qt.LeftButton)

        # at least one data point will be generated in this time
        self.assertTrue(dataGenerated.wait(2000))

        QTest.mouseClick(self.widget_stop, Qt.LeftButton)

    @function_hdr
    def test_config_option_file_not_exists(self):

        oldcfg = []

        # get the old config settings
        with open(TEST_CONFIG_FNAME, "r") as old:
            for line in old:
                oldcfg.append(line)

        # remove the file, then try to load settings
        os.remove(TEST_CONFIG_FNAME)
        self.form.fileMenu.actions()[0].trigger()

        # still need to work on simulating this with the mouse,
        # but this works for now and has the same effect.

        # not sure what kind of exception this should raise other
        # than a FileNotFoundError
        self.assertRaises(FileNotFoundError)

        # replace the original file
        with open(TEST_CONFIG_FNAME, "w+") as rewrite:
            for line in oldcfg:
                rewrite.write(line)

    @function_hdr
    def test_config_option_missing(self):

        oldcfg = []

        # get the old config settings
        with open(TEST_CONFIG_FNAME, "r") as old:
            for line in old:
                oldcfg.append(line)
        os.remove(TEST_CONFIG_FNAME)

        # replace the original file, but with one line removed
        with open(TEST_CONFIG_FNAME, "w+") as rewrite:
            for line in oldcfg:
                if oldcfg.index(line) == 0:
                    continue
                rewrite.write(line)

        # again, try to load settings
        self.form.fileMenu.actions()[0].trigger()

        self.assertRaises(Exception)

        # replace the original file
        with open(TEST_CONFIG_FNAME, "w+") as rewrite:
            for line in oldcfg:
                rewrite.write(line)

    # @function_hdr
    # def test_all_graphics_options(self):
    #
    #     self.use_example_script()
    #
    #     self.set_simple_instrument_list(connect=True)
    #
    #     QTest.mouseClick(self.widget_start, Qt.LeftButton)
    #
    #     graphicsOptions = self.form.plotToolbar
    #
    #     # turn every option on and off
    #     for opt in graphicsOptions.actions():
    #         opt.trigger()
    #         if 'Drag' not in opt.text():
    #             sleep(1)
    #         else:
    #             # need to figure out how to implement
    #             sleep(1)  # CHANGE THIS
    #         opt.trigger()
    #
    #     QTest.mouseClick(self.widget_stop, Qt.LeftButton)

    @function_hdr
    def test_all_window_options(self):
        # this should raise no exceptions, so no assertion is needed
        self.use_example_script()
        self.set_simple_instrument_list(connect=True)

        windowmenu = self.form.windowMenu
        for action in windowmenu.actions():
            action.toggle()
            QTest.mouseClick(self.widget_start, Qt.LeftButton)
            sleep(2)
            QTest.mouseClick(self.widget_stop, Qt.LeftButton)


if __name__ == "__main__":

    create_test_config_file()
    create_test_scripts()
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
