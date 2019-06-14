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



class Script(UserScript):
    def __init__(self, devices = {}, properties = {}, parent=None, debug=False):
        super(UserScript, self).__init__(devices=devices, properties=properties, parent=parent, debug=debug)
        self.devices = devices

    def run(self):
        # does something
        data_set = []
        ## stuff to add data




        self.addData(*data_set) # to do live update

    def stop(self):
        print("Any safety precautions in regards to disconnecting")

    def pause(self):
        print("Any safety precautions regarding pausing")





if __name__ == '__main__':
    s = Script()