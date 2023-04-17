"""
Created on January 23rd, 2020

@author: zackorenberg


Rohde & Schwarz Vector Network Analyzer driver

Supported models: ZVR/ZVRE/ZVRL/ZVC/ZVCE/ZVM/ZVK
"""

try:
    from . import Tool
except:
    import Tool


param = {
    'Channel' : 'Unit'
}

INTERFACE = Tool.INTF_GPIB
NAME = 'VNA'

class VNA(object):
    """
    This class contains all functions regarding communication between computer and device
    """
    def __init__(self, instr, model, firmware):
        self.instr = instr
        self.model = model
        self.firmware = firmware

    """ Utility functions """
    def write(self, msg):
        if self.instr.debug: print(msg)
        else: self.instr.write(msg)
    def read(self):
        if self.instr.debug: print("read")
        else: return self.instr.read()
    def ask(self, msg):
        if self.instr.debug: print(msg)
        else:
            self.write(msg)
            return self.read()



class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name,
                                          name=NAME,
                                          debug=debug,
                                          interface=INTERFACE,
                                          **kwargs)

        # determine model
        try:
            # records the make/model/serial number/firmware.
            # Should be returned in form  "Rohde&Schwarz, ZVxx, 123456/001, 1.03" as per manual v2p3.18
            self.make, self.model, self.serial, self.firmware = self.identify().split(",")
        except:
            raise Exception("Unsupported VNA device")
    """ driver commands """
    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'Channel':
                    answer = 'value'
            else:
                answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        self.last_measure[channel] = answer
        return answer

    def set(self, obj):
        for channel, data in obj.items():
            pass

    def get(self):
        pass

    def run(self, channel, arguments):
        pass

    """ channel """

    def set_active_channel(self, chan=1):
        """
        Selects channel as the active channel.

        INSTrument:NSELect <channel>
        """
        self.write(":INST:NSEL %d"%int(chan))
    def get_active_channel(self):
        """
        Retrieves active channel.

        INSTrument:NSELect?
        """
        return int(self.read(":INST:NSEL?" ))

    def set_averaging_clear(self, chan=1):
        """
        TODO:

        SENS<chan>:AVERage:CLEear
        """
        self.write(":SENS%d:AVER:CLE"%int(chan))
    def set_averaging_count(self, chan=1, factor=10):
        """
        TODO:

        SENS<chan>:AVERage:COUNt <number>
        """
        self.write(":SENS%d:AVER:CLE"%(int(chan),int(factor)))
    def set_averaging_state(self, chan=1, ONOFF="ON"):
        """
        SENS<chan>:AVERage:STATe <on/off>
        """
        if ONOFF not in ["ON","OFF"]:
            raise Exception("Invalid state")
        else:
            self.write(":SENS%d:AVER:COUN %s"%(int(chan), ONOFF))

if __name__ == "__main__":
    i = Instrument("GPIB::20::INSTR", debug=False)

    functions_template = Tool.generate_function_obj(funct=i.run) #some callable

