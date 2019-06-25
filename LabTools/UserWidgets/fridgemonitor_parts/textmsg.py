# -*- coding: utf-8 -*-
"""
Created on Wed Sep 05 14:21:56 2012

@author: Ben
"""

import smtplib
import string


def send_txt(msg):
    SUBJECT = ""

    
    BODY = string.join((
        "From: %s" % msg['FROM'],
        "To: %s" % msg['TO'],
        "Subject: %s" % msg['SUBJECT'] ,
        "",
        msg['BODY']
        ), "\r\n")
    print(msg['HOST'])
    server = smtplib.SMTP(msg['HOST'])
    server.sendmail(msg['FROM'], [msg['TO']], BODY)
    server.quit()
