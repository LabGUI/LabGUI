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
        'range':[-100, 100], # float range for QIntValidator
        'unit':'U' # optional unit
    },
    'Int only': {
        'type':'int',
        'range':[-100, 100], # integer range for QIntValidator
        'unit':'U' # optional unit
    },
    'Boolean type':{
        'type':'bool',
        'range':True #Can either be True or False, or disregarded
    },
    'Text type':{
        'type':'text',
        'range':'Placeholder text'
    },
    'Horizontal Bar': { # name is irrelevant, however it cannot be repeated in list. Suggested: naming them 'hbar1','hbar2',etc
        'type':'hbar',
    },
    'Label':{ # this places a label, who's text cannot be changed dynamically. Name is irrelevant. Suggested: naming them 'label1','label2',etc
        'type':'label',
        'range':'Label Text',
        'arrange':'L', # possible values are 'L','R','None', with 'None' being the default value.
                        # 'L' places label in first column (with names of channels)
                        # 'R' places label in second column (with values/inputs)
                        # 'None' places label in row without column, meaning it can span the entire line
    },
}

"""
The following variable, 'functions', is a dictionary object, where the key is function channel, and value is parameter list.
It has the following structure:
functions = {
    'channel' : parameter_list
}
the parameter_list is an ordered list, where each element is an argument object, of the following form:
parameter_list = [argument1_obj, argument2_obj, ...]
An argument object has the following required properties:
argument_object = {
    'name': 'name of parameter', name. Should be able to convert it to argument position in run
    'type': 'type of parameter', options are 'text', 'selector', 'float', 'int', 'boolean'
    'range': dependent on type
    'units': unit of parameter as a string -or- None; optional
    'required': boolean, whether it is required to call function
    'default': Optional argument to set default value
}
'range' for different types:
    text :      string, placeholder text
    int  :      list, containing range: [min, max]
    float:      list, containing range: [min, max]
    selector:   list, containing all options for dropdown menu: ['option 1', 'option 2', etc]   
    bool :      boolean, placeholder value (overriden by default)

A builtin function Tool.generate_function_obj(name=callable) can generate a function object template
"""
functions = {
    'Function 1': [
        {
            'name':'TextEdit',
            'type':'text',
            'range':'Placeholder text',
            'units':None,
            'required':True
        }, #param for text
        {
            'name':'Integer',
            'type':'int',
            'range':[-100, 100],
            'units':'Z',
            'required':True
        }, #param for int
        {
            'name': 'Float',
            'type': 'float',
            'range': [-100, 100],
            'units': 'R',
            'required': True,
            'default': 0.05
        },  # param for float
        {
            'name': 'DropdownMenu',
            'type': 'selector',
            'range':['A','B','C'],
            'units':None,
            'required':True
        }, # param for dropdown
        {
            'type':'hbar'
        }, # param for horizontal bar
        {
            'type':'label',
            'range':'Label Text',
            'arrange':'R', # either 'L', 'R', or 'None', see above
        }, # param for label
        {
            'name': 'Boolean',
            'type':'bool',
            'range':True, # shouldnt matter
            'units':None,
            'required':True
        } # param for boolean
    ]
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

    def run(self, channel, arguments):
        """
            :param channel:
                Will be a string, which is the function channel being called
            :param arguments:
                This is a dictionary of form:
                    'name' : 'value'
                Where 'name' is parameter name, and value is user inputted. Always a good idea to type cast.
            :return: A lot of flexibility here, but it should be a list of tuples which contain data points; Necessary condition for plotting capabilities
        """
        if channel == 'Function 1':
            """
            here you are going to check all of the passed arguments, and either run user-specific code or pass the sanitized arguments to a driver function
            """
            return some_obj



    # you may add any other functions here


if __name__ == "__main__": # this mean driver is being ran alone
    i = Instrument("PORT", debug=False)
    # if you want a template of a driver function to work with, call the following:
    function_obj = Tool.generate_function_obj(func1=i.funct1, funct2=i.funct2)
    # the returned function is generating via inspect.signature
    print(function_obj)
    # do stuff, like for example
    print(i.measure('Name'))







