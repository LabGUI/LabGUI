# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:30:32 2013

@author: Ben
"""

import socket
import sys

def get_fridge_data(data_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        s.connect(('localhost', 4589))
     
        s.send((data_name + '?\n').encode())
        stri = s.recv(1024)
        print(stri)
        dat = float(stri.split('=')[-1].strip())
        print(dat)
        s.close()
        
        return dat
        
    except IOError:
        print("connection failure")
        print(sys.exc_info())
        return 0
        
if __name__ == '__main__':
    get_fridge_data('LS2')    
#catch 
