# -*- coding: utf-8 -*-
"""
Created on Wed Jun 5 2019
Driver Template with read/write capabilities, without documentation for easy copy/paste
@author: zackorenberg

Note, all drivers must be placed in LabDrivers/ to work
"""
# to have base instrument class, from Tool.py
try:
    from . import Tool
except:
    import Tool


param = {
    'Channel' : 'Unit'
}
properties = {
    'Selection box': {
        'type':'selection',
        'range':[
            'option',
            'another option',
            'a third option',
            'unsurprisingly, a fourth option'
        ]
    },
    'Float only': {
        'type':'float',
        'range':[-100, 100]
    },
    'Int only': {
        'type':'int',
        'range':[-100, 100]
    },
    'Boolean type':{
        'type':'bool',
        'range':True
    },
    'Text type':{
        'type':'text',
        'range':'Placeholder'
    },
    'Multi type': {
        'type': 'multi',
        'range': ['option 1', 'option 2'],
        # the following is the mandatory 'properties' object which models based on this property object. Included is a nested multi
        'properties': {
            'Selection box': {
                'type': 'selection',
                'range': [
                    'option',
                    'another option',
                    'a third option',
                    'unsurprisingly, a fourth option'
                ]
            },
            'Float only': {
                'type': 'float',
                'range': [-100, 100]
            },
            'Int only': {
                'type': 'int',
                'range': [-100, 100]
            },
            'Boolean type': {
                'type': 'bool',
                'range': True
            },
            'Text type': {
                'type': 'text',
                'range': 'Placeholder'
            },
            'Nested Multi Type': {
                'type': 'multi',
                'range': ['option 1', 'option 2'],
                'properties': {
                    'Selection box': {
                        'type': 'selection',
                        'range': [
                            'option',
                            'another option',
                            'a third option',
                            'unsurprisingly, a fourth option'
                        ]
                    },
                    'Float only': {
                        'type': 'float',
                        'range': [-100, 100]
                    },
                    'Int only': {
                        'type': 'int',
                        'range': [-100, 100]
                    },
                    'Boolean type': {
                        'type': 'bool',
                        'range': True
                    },
                    'Text type': {
                        'type': 'text',
                        'range': 'Placeholder'
                    },
                }
            }
        }
    }
}
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
            'name': 'Boolean',
            'type':'bool',
            'range':True, # shouldnt matter
            'units':None,
            'required':True
        } # param for boolean
    ]
}

INTERFACE = Tool.INTF_GPIB
NAME = 'name'
""" Options:
INTF_GPIB
INTF_VISA
INTF_SERIAL
INTF_PROLOGIX
INTF_NONE
"""

class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name, debug=False, **kwargs):
        # DYNAMIC INTERFACING/NAME
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
                                          name=NAME,
                                          debug=debug,
                                          interface=INTERFACE,
                                          **kwargs)

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
            # set stuff

    def get(self):
        # return object with same keys as properties


if __name__ == "__main__":
    i = Instrument("GPIB::1", debug=False)








