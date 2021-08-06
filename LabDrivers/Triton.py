# -*- coding: utf-8 -*-
"""
Created on Wed Jun 5 2019
Driver Template, without documentation for easy copy/paste
@author: zackorenberg

Note, all drivers must be placed in LabDrivers/ to work


===== Examples =====

Making Setpoint (0.1T, 0.1T, 0.1T), and sweeping at a rate of 0.1 T/min

    self.set_setpoint((0.1,0.1,0.1), 'RATE', 0.1)
    self.to_setpoint()

Making Setpoint (0.1T, 0.1T, 0.1T), and arriving over the course of a minute

    self.set_setpoint((0.1,0.1,0.1), 'TIME', 1)
    self.to_setpoint()

Making Setpoint (0.5T, 0T, 0T) and going there as fast as possible

    self.set_setpoint((0.5,0,0), 'ASAP')
    self.to_setpoint()

Having magnetic field go to zero:

    self.to_zero()

Changing only the setpoint to (0T, 0.2T, 0T) and keeping all other values:

    self.set_only_setpoint((0,0.2,0))

Changing the sweep mode and rate only, keeping current setpoint values

    self.set_only_sweep('RATE', 0.1) ---- setting sweep mode to rate, with a rate of 0.1 T/min

    self.set_only_sweep('TIME', 1) ---- setting sweep mode to time, with a time of 1 minute

Request machine to hold at current magnetic strength, even if in the middle of a sweep

    self.hold()

Read current magnetic field:

    self.magnetic_field()

"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool

import socket
import time


INTERFACE = Tool.INTF_NONE
NAME = 'Triton'

ADDR = 'localhost'
PORT = 33576
TIMEOUT = 10000
BYTES = 2048

CARTESIAN = 'CART'
CYLINDRICAL = 'CYL'
SPHERICAL = 'SPH'

SWEEPMODE_ASAP = 'ASAP'
SWEEPMODE_TIME = 'TIME'
SWEEPMODE_RATE = 'RATE'

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
properties = {
    'Setpoint X':{
        'type':'float',
        'range':[-1, -1],
        'unit':'T'
    },
    'Setpoint Y':{
        'type':'float',
        'range':[-1, -1],
        'unit':'T'
    },
    'Setpoint Z':{
        'type':'float',
        'range':[-6, -6],
        'unit':'T'
    },
    'Sweep Mode':{
        'type':'selection',
        'range':[
            SWEEPMODE_ASAP,
            SWEEPMODE_TIME,
            SWEEPMODE_RATE,
        ]
    },
    'Ramp Time':{
        'type':'float',
        'range':[0,120],
        'unit':'min'
    },
    'Ramp Rate':{
        'type':'float',
        'range':[0,120],
        'unit':'T/min'
    },
    'Action':{
        'type':'selection',
        'range':[
            'None',
            'To Setpoint',
            'Hold',
            'To Zero',
        ]
    },
}

for c in CHANNELS.keys():
    param['Temp of %s'%c] = 'K'


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

        self.SWEEPMODE = {
            'ASAP':SWEEPMODE_ASAP,
            'TIME':SWEEPMODE_TIME,
            'RATE':SWEEPMODE_RATE
        }
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

    def get(self):
        ret = {
            'Setpoint X':None,
            'Setpoint Y': None,
            'Setpoint Z': None,
            'Sweep Mode': None,
            'Ramp Rate': None,
            'Ramp Time': None,
            'Action': None,
        }
        coords = self.read_setpoint(coord_sys=CARTESIAN)
        sweep_mode = self.read_sweep_mode()
        sweep_rate = self.read_sweep_rate()
        sweep_time = self.read_sweep_time()
        action = self.read_current_action()
        ret['Setpoint X'], ret['Setpoint Y'], ret['Setpoint Z'] = coords
        ret['Sweep Mode'] = sweep_mode
        ret['Ramp Rate'] = sweep_rate
        ret['Ramp Time'] = sweep_time
        if action in ['HOLD', 'RTOZ', 'RTOS']:
            ret['Action'] = {'HOLD':'Hold', 'RTOZ':'To Zero', 'RTOS':'To Setpoint'}[action]
        else:
            ret['Action'] = 'None'
        return ret
    def set(self, data):
        vals = {
            'X':None,
            'Y':None,
            'Z':None,
            'sweep_mode':None,
            'sweep_mode_param':None,
            'coord_sys':CARTESIAN
        }
        Action = 'None'
        if not self.DEBUG:
            for channel, value in data.items():
                if channel[:len('Setpoint ')] == 'Setpoint ': # X, Y, and Z values
                    vals[channel[len('Setpoint '):]] = float(value)
                elif channel == 'Sweep Mode':
                    vals['sweep_mode'] = value
                elif channel == 'Ramp Rate':
                    if data['Sweep Mode'] == self.SWEEPMODE['RATE']:
                        vals['sweep_mode_param'] = float(value)
                elif channel == 'Ramp Time':
                    if data['Sweep Mode'] == self.SWEEPMODE['TIME']:
                        vals['sweep_mode_param'] = float(value)
                elif channel == 'Action':
                    Action = value
                else:
                    print("If you reached here, something went wrong: ", channel)
            self.set_setpoint((vals['X'], vals['Y'], vals['Z']), vals['sweep_mode'], vals['sweep_mode_param'], vals['coord_sys'])
            if Action is not 'None':
                if Action == 'To Setpoint':
                    self.to_setpoint()
                elif Action == 'Hold':
                    self.hold()
                elif Action == 'To Zero':
                    self.to_zero()
                else:
                    print("Incorrect Action: ", Action)
        else:
            print("Debug mode enabled", data)

    # UTILITY FUNCTIONS
    def set_coordsys(self, coord_sys = CARTESIAN):
        possible_coord_sys = [self.CARTESIAN, self.CYLINDRICAL, self.SPHERICAL]
        if coord_sys not in possible_coord_sys:
            print("Invalid coordinate system: " % coord_sys)
            self.write('SET:SYS:VRM:COO:%s' % CARTESIAN)
            return CARTESIAN
        else:
            self.write('SET:SYS:VRM:COO:%s' % coord_sys)
            return coord_sys
    # READ FUNCTIONS
    def temperature(self, UID):
        resp = self.ask('READ:DEV:T%d:TEMP:SIG:TEMP'%int(UID)).split(":")[-1]

        if resp == 'NOT_FOUND':
            return float('nan')
        else:
            return float(resp[:-1])

    def magnetic_field(self, coord_sys = CARTESIAN):
        self.set_coordsys(coord_sys)
        resp = self.ask('READ:SYS:VRM:VECT').split(":")[-1]
        if resp == 'INVALID' or resp == 'communication timeout':
            print("VRM is off")
            return float('nan'),float('nan'),float('nan')

        vector = resp.strip("[]").split(' ')
        vector = [float(''.join([x for x in y if x.isdigit() or x in ['.','-']])) for y in vector] # get rid of unit
            #[float(i[:-1]) for i in vector] # get rid of unit
        return tuple(vector)
        #return [float(i) for i in vector]

    # VRM Action Functions
    def to_setpoint(self):
        """
        Tells VRM to sweep to setpoint

        :return: none
        """
        self.write("SET:SYS:VRM:ACTN:RTOS")

    def to_zero(self):
        """
        Tells VRM to sweep to zero

        :return: none
        """
        self.write("SET:SYS:VRM:ACTN:RTOZ")

    def hold(self):
        """
        Tells VRM to hold field

        :return: none
        """
        self.write("SET:SYS:VRM:ACTN:HOLD")

    def read_current_action(self):
        return self.ask("READ:SYS:VRM:ACTN").split(":")[-1]
    # Sweep Functions
    def read_sweep_mode(self):
        """
        :return: current sweep mode of VRM: (string) ASAP, TIME, or RATE
        """
        return self.ask("READ:SYS:VRM:RVST:MODE").split(":")[-1]

    def read_sweep_time(self):
        """
        :return: current sweep time in minutes of VRM: (float)
        """
        resp = self.ask("READ:SYS:VRM:RVST:TIME").split(":")[-1]
        return float(''.join([x for x in resp if x.isdigit() or x in ['.', '-']]))

    def read_sweep_rate(self):
        """
        :return: curernt sweep rate in Tesla/minute of VRM: (float)
        """
        resp = self.ask("READ:SYS:VRM:RVST:RATE").split(":")[-1]
        return float(''.join([x for x in resp if x.isdigit() or x in ['.', '-']]))

    def read_setpoint(self, coord_sys = CARTESIAN):
        """
        Get tuple in given coordsys for setpoint of VRM

        :param coord_sys: default CARTESIAN
        :return: (X, Y, Z) for CART, (rho, theta, Z) for cylinrical or (r, theta, phi) for spherical
        """
        self.set_coordsys(coord_sys)
        resp = self.ask("READ:SYS:VRM:VSET").split(":")[-1]
        if resp == 'INVALID' or resp == 'communication timeout':
            print("VRM is off")
            return float('nan'),float('nan'),float('nan')
        vector = resp.strip("[]").split(' ')
        vector = [float(''.join([x for x in y if x.isdigit() or x in ['.', '-']])) for y in vector]  # get rid of unit
        return tuple(vector)

    def set_setpoint(self, coords, sweep_mode, sweep_mode_param = None, coord_sys = CARTESIAN):
        """
        Set VRM setpoint in given coordinate system. The default is cartesian. See required order below

        :param coords: must be tuple in form of (X, Y, Z) for CART, (rho, theta, Z) for cylinrical or (r, theta, phi) for spherical
        :param sweep_mode: valid types are:
                    ASAP : Sweep as fast as possible
                    TIME : specific time to setpoint (see sweep_mode_param)
                    RATE : specific rate overall (see sweep_mode_param)
        :param sweep_mode_param: Specific to sweep_mode
                ASAP : this will be ignored, as it is unneeded
                TIME : (float) sweep time in minutes
                RATE : (float) sweep rate in T/min (tesla per minute)
        :param coord_sys: default CARTESIAN
        :return: Boolean, Returns TRUE if setpoint was properly set, else returns FALSE
        """
        self.set_coordsys(coord_sys)

        if sweep_mode not in self.SWEEPMODE.keys():
            print("Invalid sweep mode selected: %s"%sweep_mode)
            print("Valid sweep modes are: %s"%", ".join(self.SWEEPMODE.keys()))
            return

        cmd_prefix = 'SET:SYS:VRM'
        cmd_rvst = ''
        cmd_setpoint = 'VSET:[%f %f %f]'%coords
        if sweep_mode == self.SWEEPMODE['ASAP']:
            cmd_rvst = 'RVST:MODE:ASAP'
        else:
            cmd_rvst = 'RVST:MODE:%s:%s:%f'%(sweep_mode, sweep_mode, float(sweep_mode_param))
        cmd = ":".join([cmd_prefix, cmd_rvst, cmd_setpoint])
        resp = "BUSY"
        while resp == "BUSY":
            resp = self.ask(cmd).split(":")[-1]
            if resp == "INVALID":
                print("Invalid parameters for setpoint coordinates")
                return False
        return True



    def force_set_setpoint(self, coords, sweep_mode, sweep_mode_param = None, coord_sys = CARTESIAN, MAX_ITER=10000):
        """
        Same as "set_setpoint", but it makes sure that the machine accepts the new value (USE AT OWN RISK, MAY STALL PROGRAM).

        Please note, that if the setpoint coordinates are not within the range of those accepted by the machine, this command will never terminate
        """
        i = 0
        setp = self.read_setpoint(coord_sys)
        while setp != coords and i < MAX_ITER:
            self.set_setpoint(coords, sweep_mode, sweep_mode_param, coord_sys)
            setp = self.read_setpoint(coord_sys)
            i += 1
        if i == MAX_ITER: return False
        else: return True
    def set_only_setpoint(self, coords, coord_sys = CARTESIAN):
        """
        Set only setpoint values, keeping already set sweep mode parameters
        :param coords: must be tuple in form of (X, Y, Z) for CART, (rho, theta, Z) for cylinrical or (r, theta, phi) for spherical
        :param coord_sys:
        :return: None
        """
        sweep_mode = self.read_sweep_mode()
        sweep_param = None
        if sweep_mode == self.SWEEPMODE['TIME']:
            sweep_param = self.read_sweep_time()
        elif sweep_mode == self.SWEEPMODE['RATE']:
            sweep_param = self.read_sweep_rate()

        self.set_setpoint(coords, sweep_mode, sweep_param, coord_sys)

    def set_only_sweep(self, sweep_mode, sweep_param = None, coord_sys = CARTESIAN):
        """
        Sets only the sweep mode, preserving current values for the rest of the arguments
        :param sweep_mode:
        :return: None
        """
        if sweep_mode not in self.SWEEPMODE.keys():
            print("Invalid sweep mode selected: %s" % sweep_mode)
            print("Valid sweep modes are: %s" % ", ".join(self.SWEEPMODE.keys()))
            return
        coords = self.read_setpoint(coord_sys)

        self.set_setpoint(coords, sweep_mode, sweep_param, coord_sys)

if __name__ == "__main__":
    i = Instrument("127.0.0.1", debug=False)
    x, y, z = i.magnetic_field(i.CARTESIAN)
    print(i.temperature(8))








