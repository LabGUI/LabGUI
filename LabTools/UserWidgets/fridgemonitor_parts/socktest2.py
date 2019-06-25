# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:30:32 2013

@author: Ben
"""

import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind(('localhost', 4589))
serversocket.listen(5)





while 1:
    #accept connections from outside
    (clientsocket, address) = serversocket.accept()
    #now do something with the clientsocket
    #in this case, we'll pretend this is a threaded server
    #ct = client_thread(clientsocket)
    #ct.run()
    while 1:
        req = clientsocket.recv(1024)
        if req:
            print(req)
            for line in req.split('\n'):
                if line.find('LS1') != -1:
                    clientsocket.send("LS1="+str(1.37) + '\n')
                elif line.find('LS2')!= -1:
                    clientsocket.send("LS2="+str(2.37) + '\n')
                elif line.find('LS3')!= -1:
                    clientsocket.send("LS3="+str(3.37) + '\n')
                elif line.find('LS4')!= -1:
                    clientsocket.send("LS4="+str(4.37) + '\n')        
        else:
            break
        
    print("done")