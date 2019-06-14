#try:
#    from . import UserTool
#except:
#    import UserTool
try:
    from __init__ import UserScript # if running standalone
except:
    from LabTools.UserScriptModule import UserScript # if running from LabGui

devices = ['KT2500']
params = {
    'Voltage':'V',
    'Current':'A'
}

import time
import sys
import math

class Script(UserScript):
    def __init__(self, name = '', devices = devices, parent=None, debug=False):
        super(Script, self).__init__(name = name, devices=devices , params = params, parent=parent, debug=debug)
        self.devices = devices

    def run(self):
        # does something
        data_set = []
        print("got to run in script")
        for i in range(0, 100):
            try:
                self.addData(i+1, math.cos(i/10))
            except:
                print(sys.exc_info())
            time.sleep(1)
        ## stuff to add data
        print("done")



        self.addData(*data_set) # to do live update

    def stop(self):
        print("Any safety precautions in regards to disconnecting")

    def pause(self):
        print("Any safety precautions regarding pausing")





if __name__ == '__main__':
    s = Script()