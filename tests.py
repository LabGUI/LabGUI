# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:23:23 2017

@author: admin
"""


import os

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
if __name__ == "__main__":
    
#    test_start_normal()
    
#    test_config_option_missing()
    
#    test_config_option_wrong_type()
#    
#    test_config_option_file_not_exists()
#    
#    test_config_option_wrong_file()
    
#    test_config_option_multiple_file()

    test_config_option_correct()