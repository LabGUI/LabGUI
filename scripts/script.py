# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:38:20 2013

@author: Ben

This is a script to be used with DataTakerThread.py, part of the recordsweep.py
program. This example just loops until the thread is killed. It runs within 
the namespace of DataTakerThread.
"""
#This is useful to turn the alarm on

#import alarm_toolbox as alarm
#
#snooze_timers={}
#instr_id_names=[]
#
#for inst in self.active_instruments:
#    if inst!='TIME':
##        print insts
#        id_name=inst.ID_name
##        print id_name
#        snooze_timers[id_name]=-1
#        if not id_name in instr_id_names:
#            instr_id_names.append(id_name)

print("INIT DONE")
#print self.instruments
while self.isStopped() == False:
    
    
    #This initiates the measure sequence in datatakerthread
    self.read_data()
    time.sleep(1)
    self.check_stopped_or_paused()
    
    #The following is tha basic alarm sequence, uncomment this block to activate it

#    #look in the file alarm_settings.txt for instruments alarm settings, if found nothing set the flag to False
#    alarm_flags=alarm.set_flags(instr_id_names)
#    #look in the file alarm_settings.txt for instruments alarm settings, if found nothing set the timer
#    snooze_time=alarm.get_snooze_time(instr_id_names)
#    #look in the file alarm_settings.txt to fetch the email adress
#    mailinglist=alarm.get_settings('MAILING_LIST')    
##    if len(mailinglist)==0:
##        print "The email alarm system is desactivated, to reactivate, please add a line MAILING_LIST=pfduc@physics.mcgill.ca;pierre-francois.duc@a3.epfl.ch into the alarm_settings.txt file"
##        print "If error occurs emails will be sent to the following recipients : ",mailinglist
#    
##    print "---ALARM SEQUENCE---"
##    print snooze_timers
#    for inst in self.active_instruments: 
#        if inst!='TIME':
#            id_name=inst.ID_name
#            #collect whatever the responses from the query alarm() of the instruments
#            alarm_stack=inst.query_alarm()
#
#            curtime=time.time() - self.t_start
# 
#            if snooze_timers[id_name]==-1 or snooze_timers[id_name]<curtime:
#                for al_h in alarm_stack:
#                    alarm_status=al_h.manage(alarm_flags[id_name],mailinglist)
#                    if alarm_status:
#                        print "Timer was set until ", snooze_timers[id_name]
#                        print "It is now ",curtime
#                        print al_h.get()
#                        snooze_timers[id_name]=alarm.set_snooze_timer(alarm_status,snooze_time[id_name],curtime)
#                        print snooze_timers
##    print "---ALARM SEQUENCE DONE---"
