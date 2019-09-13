# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:23:23 2017

@author: admin
"""

from LabTools.CoreWidgets import ScriptWidget, OutputFileWidget
from LabTools.IO import IOTool
import unittest
import warnings

import os
import subprocess

import time

import sys

from LabDrivers import utils

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

# relaunches the application


def relaunch():
    app.quit()
    # app.exec_()


class ScriptWidgetTest(unittest.TestCase):
    #
    #
    #    '''Test the LabGui GUI'''
    def setUp(self):
        '''Create the GUI'''

        self.form = ScriptWidget.ScriptWidget()

        self.widget_script_button = self.form.scriptFileButton

        self.setting_fname = IOTool.get_script_name()

    def test_inital_script_name_ok(self):

        # print the test function name
        print("\n\t### %s ###\n" % (sys._getframe().f_code.co_name))

        self.assertEqual(self.setting_fname, self.form.get_script_fname())


#    def test_start_DTT_produce_a_file(self):
#
#        #print the test function name
#        print("\n### %s ###\n"%(sys._getframe().f_code.co_name))
#
#
#        #Start the DTT
#        QTest.mouseClick(self.widget_script_button, Qt.LeftButton)
#
#        #print the name of the data file
##        ofname = self.form.output_file.name
##        print("DTT output file : %s"%(ofname))
# time.sleep(10)
#
##        QTest.mouseClick(self.widget_stop, Qt.LeftButton)


class OutputFileWidgetTest(unittest.TestCase):
    #
    #
    #    '''Test the LabGui GUI'''
    def setUp(self):
        '''Create the GUI'''

        self.form = OutputFileWidget.OutputFileWidget()

        self.widget_headerTextEdit = self.form.headerTextEdit

        self.widget_outputFileLineEdit = self.form.outputFileLineEdit

        self.widget_outputFileLineEdit.setText("")

        self.test_fname = "test__001.dat"
        of = open(self.test_fname, 'w')
        of.write("")
        of.close()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        os.remove(self.test_fname)

    def test_change_output_file_name(self):

        # print the test function name
        print("\n\t### %s ###\n" % (sys._getframe().f_code.co_name))

        random_text = "Hello"

        QTest.keyClicks(self.widget_outputFileLineEdit, random_text)

        self.assertEqual(self.form.get_output_fname(), random_text)

    def test_get_header_text(self):

        # print the test function name
        print("\n\t### %s ###\n" % (sys._getframe().f_code.co_name))

        random_text = "Hello"

        self.widget_headerTextEdit.insertPlainText(random_text)

        random_text = "# " + random_text.replace("\n", "\n#") + "\n"
        self.assertEqual(self.form.get_header_text(), random_text)

    def test_increment_file_name(self):

        # print the test function name
        print("\n\t### %s ###\n" % (sys._getframe().f_code.co_name))

        QTest.keyClicks(self.widget_outputFileLineEdit, self.test_fname)

        self.form.increment_filename()

        self.assertNotEqual(self.form.get_output_fname(), self.test_fname)


#
if __name__ == "__main__":

    unittest.main()
