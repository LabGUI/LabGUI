# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 2019
Driver for both reading and writing example with documentation
@author: zackorenberg


An example driver with documentation, where the device has writing capabilities

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
The following variable, 'properties', determines internally whether or not this device supports writing
Similar to the 'param' variable, 'properties' takes in the channel as a dictionary key, with its value being another object.
This object MUST contain two fields, 'type' and 'range'. Below is an example for each supported type
"""
properties = {
    'Selection box/Dropdown Menu': {
        'type':'selection',
        'range':[
            'option',
            'another option',
            'a third option',
            'unsurprisingly, a fourth option'
        ] # each item in range will be a selectable item in the dropdown menu
    },
    'Float only': {
        'type':'float',
        'range':[-100, 100] # float range for QIntValidator
    },
    'Int only': {
        'type':'int',
        'range':[-100, 100] # integer range for QIntValidator
    },
    'Boolean type':{
        'type':'bool',
        'range':True #Can either be True or False, or disregarded
    },
    'Text type':{
        'type':'text',
        'range':'Placeholder text'
    }
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

    def set(self, data):
        """
        An example setting function. A function of this name with a one parameter signature must be present for all drivers that have a 'properties' object
        :param data:
            data is a dictionary object, where each key represents a channel in the 'properties' object. The 'value' is that set by the user
        :return: Boolean, or None
        """
        if not self.DEBUG:
            for channel, value in data.items():
                if channel == 'Selection box/Dropdown Menu':
                    # code that sets channel property to value
                    # ex: self.set_shape(value)
                elif channel == 'Float only':
                    # do something with floating point value
                    value = float(value)
                elif channel == 'Int only':
                    # do something with integer (wise to type cast, as value may be string
                    value = int(value)
                elif channel == 'Boolean type':
                    # do something with boolean value True or False
                elif channel == 'Text type':
                    # do something with string value
                else:
                    print("If you reached here, something went wrong: ", channel)
        else:
            print("Debug mode enabled", data)

    def get(self):
        """
        This function is required to refresh the properties for the user.
        There is very much flexibility in how it is programmed. The only requirement is the format of the return value, specified below
        Attached is an example that cycles through each key, setting a default value. Not a necessary implementation
        :return:
            The return object must be a dictionary similar to properties. Each channel in properties must be present as a key, with its value being that of the current setting.
        """
        ### example one ###
        default_value = 0
        ret = dict((key,default_value) for key in properties.keys())
        ret['specific_channel'] = self.get_value_for_specific_channel() # user written function within driver
        ret['a_different_channel'] = self.get_value_for_a_different_channel() # another user written function within driver

        return ret
        ### example two ###
        ret = {}
        for channel in properties.keys():
            if channel == 'specific_channel':
                ret[channel] = self.get_value_for_specific_channel()  # user written function within driver
            elif channel == 'a_different_channel':
                ret[channel] = self.get_value_for_a_different_channel()  # another user written function within driver
            else:
                ret[channel] = default_value

        return ret
    # you may add any other functions here


if __name__ == "__main__": # this mean driver is being ran alone
    i = Instrument("PORT", debug=False)

    # do stuff, like for example
    print(i.measure('Name'))







