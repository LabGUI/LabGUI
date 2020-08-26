# -*- coding: utf-8 -*-
"""
Created on Wed Jun 5 2019
Driver Template, without documentation for easy copy/paste
@author: zackorenberg

Note, all drivers must be placed in LabDrivers/ to work
"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool

import socket



INTERFACE = Tool.INTF_NONE
NAME = 'Triton'

ADDR = 'localhost'
PORT = 33576
TIMEOUT = 10000
BYTES = 2048


CHANNELS = {
    'PT2 Head':1,
    'PT2 Plate':2,
    'Still Plate':3,
    'Cold Plate':4,
    'MC Plate Cernox':5,
    'PT1 Head':6,
    'PT1 Plate':7,
    'MC Plate RuO2':8,
    'Magnet':9
}

param = {
    'Magnetic Field X':'T',
    'Magnetic Field Y':'T',
    'Magnetic Field Z':'T'
}

for c in CHANNELS.keys():
    param['Temp of %s'%c] = 'K'

CARTESIAN = 'CART'
CYLINDRICAL = 'CYL'
SPHERICAL = 'SPH'
class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, ip_address=ADDR, port_number = PORT, timeout = TIMEOUT, bytes_to_read = BYTES, debug=False, **kwargs):
        super(Instrument, self).__init__(ip_address,
                                          name=NAME,
                                          debug=debug,
                                          interface=INTERFACE,
                                          **kwargs)
        self.address = (str(ip_address), int(port_number))
        self.timeout = timeout
        self.bytes_to_read = bytes_to_read
        self.termchar = '\r\n'


        ## constants
        self.CARTESIAN = 'CART'
        self.CYLINDRICAL = 'CYL'
        self.SPHERICAL = 'SPH'

        ## determine channels
        pass


    def write(self, msg):
        msg = msg.strip("\n").strip("\r").strip("\n")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
            s.sendall((msg + self.termchar).encode())

    def read(self, numbytes = None):
        if numbytes is None:
            numbytes = self.bytes_to_read
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
            response = s.recv(numbytes).decode()
        return response.strip('\n').strip('\r').strip('\n')
    def ask(self, msg):
        try:
            msg = msg.strip("\n").strip("\r").strip("\n")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.address)
                s.settimeout(self.timeout)
                s.sendall((msg + self.termchar).encode())
                response = s.recv(self.bytes_to_read).decode()
            return response.strip('\n').strip('\r').strip('\n')
        except ConnectionResetError:
            return self.ask(msg)
    def query(self,msg):
        return self.ask(msg)
    def identify(self):
        return "Triton"

    def UID(self, hardware_type):
        avail = ['COOL','STIL','MC','PT1','PT2','SORB']
        if hardware_type.upper() not in avail:
            return "invalid hardware type"
        resp = self.ask("READ:SYS:DR:CHAN:%s"%hardware_type.upper())
        return resp.split(":")[-1][1:]

    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")
        answer = None
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel[:len('Temp of ')] == 'Temp of ':
                    chan = channel[len('Temp of '):]
                    answer = self.temperature(CHANNELS[chan])
                elif channel[:len('Magnetic Field ')] == 'Magnetic Field ':
                    coordinate = channel[len('Magnetic Field '):]
                    coordresp = {}
                    coordresp['X'], coordresp['Y'], coordresp['Z'] = self.magnetic_field(self.CARTESIAN)
                    answer = coordresp[coordinate]

            else:
                answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        self.last_measure[channel] = answer
        return answer

    def temperature(self, UID):
        resp = self.ask('READ:DEV:T%d:TEMP:SIG:TEMP'%int(UID)).split(":")[-1]

        if resp == 'NOT_FOUND':
            return float('nan')
        else:
            return float(resp[:-1])

    def magnetic_field(self, coord_sys = CARTESIAN):
        possible_coord_sys = [self.CARTESIAN,self.CYLINDRICAL,self.SPHERICAL]
        if coord_sys not in possible_coord_sys:
            print("Invalid coordinate system: " % coord_sys)
        else:
            self.write('SET:SYS:VRM:COO:%s'%coord_sys)
        resp = self.ask('READ:SYS:VRM:VECT').split(":")[-1]
        if resp == 'INVALID' or resp == 'communication timeout':
            print("VRM is off")
            return float('nan'),float('nan'),float('nan')

        vector = resp.strip("[]").split(' ')
        vector = [float(''.join([x for x in y if x.isdigit() or x in ['.','-']])) for y in vector] # get rid of unit
            #[float(i[:-1]) for i in vector] # get rid of unit
        return tuple(vector)
        #return [float(i) for i in vector]
if __name__ == "__main__":
    i = Instrument("127.0.0.1", debug=False)
    x, y, z = i.magnetic_field(i.CARTESIAN)
    print(i.temperature(8))








