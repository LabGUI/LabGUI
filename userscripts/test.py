#try:
#    from . import UserTool
#except:
#    import UserTool
try:
    from __init__ import UserScript # if running standalone
except:
    from LabTools.UserScriptModule import UserScript # if running from LabGui

devices = ['KT2500']



class Script(UserScript):
    def __init__(self, instr_hub, devices = {}, params = {}, properties = {}, parent=None, debug=False):



    def run(self):
        # does something





if __name__ == '__main__':
    s = Script()