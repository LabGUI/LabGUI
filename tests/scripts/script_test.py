# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:38:20 2013

@author: Ben

This is a script to be used with DataTakerThread.py, part of the recordsweep.py
program. This example just loops until the thread is killed. It runs within 
the namespace of DataTakerThread.
"""


print("INIT DONE")
print self.instruments

for i in range(10):
    print(i)
    self.read_data()
#    print(i)
    time.sleep(0.2)
    self.check_stopped_or_paused()
    print self.stopped
    print self.paused
#while self.isStopped() == False:
#    
#    #This initiates the measure sequence in datatakerthread
#    self.read_data()
#    time.sleep(2)
#    self.check_stopped_or_paused()
    

