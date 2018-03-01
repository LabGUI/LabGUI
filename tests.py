# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:23:23 2017

@author: admin
"""

import unittest
import warnings

import os
import subprocess


from LabDrivers import utils 



def test_start_normal():
    print("Normal start")
    os.system("python LabGui.py")

def test_config_option_missing():
    print("config_option_missing")
    os.system("python LabGui.py -c")
    
def test_config_option_wrong_type():
    print("config_option_wrong_type")
    os.system("python LabGui.py -c 12")
    
def test_config_option_file_not_exists():
    print("config_option_file_not_exists")
    os.system("python LabGui.py -c Monsieur.txt")    

def test_config_option_wrong_file():
    print("config_option_wrong_file")
    os.system("python LabGui.py -c requirements.txt") 
    
def test_config_option_multiple_file():
    print("config_option_multiple_file")
    os.system("python LabGui.py -c requirements.txt config.txt") 

def test_config_option_correct():
    print("config_option_correct")
    os.system("python LabGui.py -c config_mass_spec_alone.txt") 
    
    
#class TestConfigInlineOption(unittest.TestCase):   
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


import sys
#import unittest

from LocalVars import USE_PYQT5

if  USE_PYQT5:

    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt


else:
    
    import PyQt4.QtGui as QtGui
    from PyQt4.QtTest import QTest
    from PyQt4.QtCore import Qt

import LabGui

app = QtGui.QApplication(sys.argv)

# relaunches the application
def relaunch(): 
    app.quit()
    #app.exec_()
    
def create_test_setting_file(fname = "test_settings.set"):
    """create a file with settings so the test can be run anywhere"""
    
    settings_file = open(os.path.join("settings",fname), 'w')

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
    
    
class LabGuiTest(unittest.TestCase):    
#
#        
#    '''Test the LabGui GUI'''  
    def setUp(self):
        '''Create the GUI'''
        self.form = LabGui.LabGuiMain(['-c','config_test.txt'])
        
        self.setting_fname = "test_settings.set"    

#    def test_no_plot_window(self):
#        '''Test that there is no window at the start
#        '''
#
#        self.assertRaises(IndexError, self.form.get_last_window())
#            
        
    def set_simple_instrument_list(self, instr_name = 'DICE', 
                                         instr_port = 'COM99', 
                                         instr_param = 'Roll',
                                         connect = False):
        
        """Populate the InstrumentWidget with 3 instruments
        
            The one in the middle is userdefined, the other are time and dt
            if connect is set to True, the button connect will be clicked
        
        """
        
        instr_widget = self.form.widgets['InstrumentWidget']
        
        instr = ['TIME', instr_name, 'TIME']
        port = ['', instr_port, '']
        param = ['Time', instr_param, 'dt']
        
        QTest.mouseClick(instr_widget.bt_add_line, Qt.LeftButton)

        #Fill the lines with Time and dt encercling the instrument
        for i in range(len(instr)):
            
            #instrument name
            cbb = instr_widget.lines[i].instr_name_cbb
            cbb.setCurrentIndex(cbb.findText(instr[i]))
            
            #instrument port
            cbb = instr_widget.lines[i].port_cbb            
            cbb.setCurrentIndex(cbb.findText(''))
            QTest.keyClicks(cbb, port[i])
            
            #instrument parameter
            cbb = instr_widget.lines[i].param_cbb            
            cbb.setCurrentIndex(cbb.findText(param[i]))           
        
        if connect:
            #Click on connect
            QTest.mouseClick(instr_widget.bt_connecthub, Qt.LeftButton)
    
    def test_number_of_instrument_connected_at_start(self):
        """the number of instrument connected at start should be 0"""
        
        num_instr = self.form.instr_hub.get_instrument_nb()
        
        self.assertEqual(num_instr,0)
        
        
    def test_instr_widget_click_add_line_button(self):
        """click on the button 'Add line' should create a line"""
        
        #intrument widget instance
        instr_widget = self.form.widgets['InstrumentWidget']
        
        num_lines_before = len(instr_widget.lines)  
        
        QTest.mouseClick(instr_widget.bt_add_line, Qt.LeftButton)
        
        num_lines_after = len(instr_widget.lines)
        
        #test that the number of lines increased by one 
        self.assertEqual(num_lines_before + 1, num_lines_after)        
        
        
    def test_instr_widget_click_connect_button(self):
        """
            check how many instuments are connected to the instrument hub
            after the user added an instrument line in the InstrumentWidget
            and clicked the InstrumentWidget 'Connect' button
        """
        
        self.set_simple_instrument_list(connect = True)
        
        num_instr_after = self.form.instr_hub.get_instrument_nb()
        
        self.assertEqual(num_instr_after,3)    
    
#        
#    def test_dice_connect_and_play(self):
#        '''test the modification of the instrument list
#        click connect to connect the instrument hub
#        '''
#        
#        self.set_simple_instrument_list()
#    
#        # Push OK with the left mouse button
#        connect_bt = self.form.widgets['InstrumentWidget'].bt_connecthub
#        QTest.mouseClick(connect_bt, Qt.LeftButton)
#
#        self.assertEqual(1,1)        
#        
#    def test_save_instrument_settings(self):
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#        print("\ntest_save_instrument_settings\n")        
#        
#        self.set_simple_instrument_list()
#        
#     
#        
#        self.form.file_save_settings(self.setting_fname)
#        
#        self.assertTrue(os.path.exists(self.setting_fname))
#        
#        ofs = open(self.setting_fname, 'r')
#
#        for line in ofs:
#            print(line)
#        
#    def test_load_instrument_settings(self):
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#      
#        print("\ntest_load_instrument_settings\n")    
#        
#        self.form.file_load_settings(self.setting_fname)  
#        
##        if os.path.exists(self.setting_fname):  
##        
##            self.assertIsNotNone(self.form.plot_window_settings)
#        
#        
#        self.assertEqual(self.form.instrument_connexion_setting_fname,
#                     self.setting_fname)
#        
#        self.form.file_load_settings("doesnt_exist.fname")  
#        
#        self.assertIsNone(self.form.plot_window_settings)
#    
#    
#    #Shammamah's tests (incomplete!)
#    # Tests connect button  
#    def test_add_remove(self): 
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#
#        print("\ntest_add_remove\n")
#        
#        remove_bt = self.form.widgets['InstrumentWidget'].bt_remove_last         
#        add_bt = self.form.widgets['InstrumentWidget'].bt_add_line
#        connect_bt = self.form.widgets['InstrumentWidget'].bt_connecthub
#        
#        QTest.mouseClick(add_bt, Qt.LeftButton)
#        QTest.mouseClick(connect_bt, Qt.LeftButton)        
#        QTest.mouseClick(remove_bt, Qt.LeftButton)
#        QTest.mouseClick(connect_bt, Qt.LeftButton)
#        
#        
#    # Config file testing: save config settings -> see if settings are loaded correctly 
#    # check data path, script, settings, datafile, debug mode 
#    def test_config_debug(self):
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#        print("\ntest_config_debug\n")
#        filemenu = self.form.fileMenu
#        optionmenu = self.form.optionMenu
#        change_debug = optionmenu.actions()[1]
#        save_config = filemenu.actions()[4]
#
#        print("\nChanging debug state...")
#        change_debug.trigger()
#        f = open("config.txt","r")
#        lines = f.readlines()
#        for i in range(len(lines)): 
#            if("DEBUG" in lines[i]): 
#                print("config.txt: "+lines[i])
#        f.close()
#        print("\nChanging back debug state...")
#        change_debug.trigger()
#        f = open("config.txt","r")
#        lines = f.readlines()
#        for i in range(len(lines)): 
#            if("DEBUG" in lines[i]): 
#                print("config.txt: "+lines[i])
#        f.close()
#        #save_config.trigger()
#            
#        #a = subprocess.check_output("type logging.conf | findstr 'DEBUG*'")
#        #print(a)     
#        # close LabGui and reopen to see if settings have loaded correctly 
#        # not quite sure how to simulate closing the program   
#
#
#    # check if logger output level is changed correctly 
#    def test_logger_output_level(self):
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#        print("\ntest_logger_output_level\n")
#        save_config = self.form.fileMenu.actions()[4]
#        logmenu = self.form.loggingSubMenu.actions()
#        debug = logmenu[0]
#        info = logmenu[1] 
#        warning = logmenu[2] 
#        error = logmenu[3] 
#        
#        for item in logmenu: 
#            print(item.iconText())
# 
#        print("\nToggling debug...")
#        debug.trigger() 
#        #save_config.toggle() 
#            
#        print("\nToggling info...")
#        info.trigger() 
#        
#        print("\nToggling warning...")
#        warning.trigger()
#        
#        print("\nToggling error...")
#        error.trigger()
#        
#    def test_relaunch(self) :
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#        print("\ntest_relaunch\n")
#        relaunch() 
#        
#        
#    # Tests from utils.py
#    # (raising errors if the functions are copy/pasted into this file; 
#    #   right now, I just call the test functions in utils.py from here) 
#    
#    print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#    print("\ntest_prologix_controller_creation_with_com\n")
#    utils.test_prologix_controller_creation_with_com(com_port = None)
#    
#    print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#    print("\ntest_prologix_controller_creation_with_wrong_com\n")
#    utils.test_prologix_controller_creation_with_no_arg_conflict()
#    
#    print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#    print("\ntest_prologix_controller_creation_with_no_arg_conflict()\n")
#    utils.test_prologix_controller_creation_with_wrong_com()
#        
##Logger output level
##Change debug mode
## Test for successful output to console
#    
#    # check if bad scripts are handled correctly    
#    def test_bad_script(self):
#        print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#        print("\ntest_bad_script\n")
#        script = self.form.widgets['SciptWidget'].scriptFileLineEdit
#        
#        f = open("syntaxError.py", "w+")
#        f.write('''
#                prnt("this script doesn't compile")
#                ''')
#        f.close()
#        
#        badScripts = ["\'%s/notarealscript.py\'"%(os.getcwd()),
#                      "\'%s/notapythonscript.c\'"%(os.getcwd()),
#                      "\'%s/directory/\'"%(os.getcwd()),
#                      "\'   \'",
#                      "\'%s/script_example.py\'"%(os.getcwd())]
#        
#        for badScriptName in badScripts:
#            print("Testing %s\n"%badScriptName)
#            script.setText(badScriptName)
#            self.form.datataker.run()
#            print()
#        
#        os.remove("syntaxError.py")
  
if __name__ == "__main__":

    unittest.main()    
    
#    test_start_normal()
    
#    test_config_option_missing()
    
#    test_config_option_wrong_type()
#    
#    test_config_option_file_not_exists()
#    
#    test_config_option_wrong_file()
    
#    test_config_option_multiple_file()

#    test_config_option_correct()