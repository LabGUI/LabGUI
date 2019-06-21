# -*- coding: utf-8 -*-
"""
Created on Wed Jun 5 2019
Driver Example with documentation
@author: zackorenberg


An example driver with documentation

Note, all drivers must be placed in LabDrivers/ to work
"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool


# what is written in param is measurable types of data, where the key represents the channel that will be passed to Instrument.measure(channel)
param = {
    'Name' : 'Unit',
    'Channel' : 'Unit'
}
"""
The following is the default interface to use. This can be overwritten in the constructor of this function
interface options are:

INTF_GPIB
INTF_VISA
INTF_SERIAL
INTF_PROLOGIX
INTF_NONE

"""
INTERFACE = Tool.INTF_GPIB


#defining the actual instrument class
class Instrument(Tool.MeasInstr): # Tool.MeasInstr is child class
    """"This class is the driver of the instrument *INSERT NAME HERE*"""""

    def __init__(self, resource_name, debug=False, **kwargs):
        """ To allow for dynamic name and/or interface, uncomment the following"""

        # if "interface" in kwargs:
        #     itfc = kwargs.pop("interface")
        # else:
        #     itfc = INTERFACE
        #
        # name='insert device name here, typically the same name as the file'
        # if "name" in kwargs:
        #     name = kwargs.pop("name")
        #     print(name)
        # super(Instrument, self).__init__(resource_name,
        #                                  name=name,
        #                                  debug=debug,
        #                                  interface = itfc,
        #                                  read_termination = '\r', # this is left here to show that it is possible to change read_termination value
        #                                  **kwargs)
        #
        super(Instrument, self).__init__(resource_name,
                                          name='insert device name here, typically the same name as the file',
                                          debug=debug,
                                          interface=INTERFACE,
                                          **kwargs)
        """ you may add any other important calls here """

    def measure(self, channel):
        #this function is a requirement, as it is called when reading script is initialized. The only possibilities for channel is given by param.keys()

        if self.DEBUG:
            # do stuff if in debug mode is globally set
            print("Debug mode activated")

        if channel in self.last_measure: # not required, but is a good idea to implement
            if not self.DEBUG:
                if channel == 'Name':
                    #this mean that the channel is the first in param dictionary
                    answer = 'value'
                    """
                    You can use any of the self.ask, self.write, self.read to obtain data from the machine
                    """
                elif channel == 'Channel':
                    # this means that this is the second channel in param dictionary
                    answer = 'other type of value'
                # add as many elif statements to catch all channels as necessary
            else:
                answer = 123.4

        else:
            # not a valid channel
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        # now we save the data and return it
        self.last_measure[channel] = answer
        return answer


    # you may add any other functions here


if __name__ == "__main__": # this mean driver is being ran alone
    i = Instrument("PORT", debug=False)

    # do stuff, like for example
    print(i.measure('Name'))







