# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:38:20 2013

@author: Ben

This is a script to be used with DataTaker.py, part of the LabGui.py
program. This example just loops until the thread is killed. It runs within 
the namespace of DataTaker.
"""

print("INIT DONE")
# print self.instruments
while self.isStopped() == False:

    # This initiates the measure sequence in datataker
    self.read_data()
    time.sleep(1)
    self.check_stopped_or_paused()
