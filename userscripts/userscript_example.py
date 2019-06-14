"""
Example user script using expected format
"""
import LabTools.UserScriptModule


devices = ['DICE']
properties = {
    'Number of rolls': {
        'type':'int',
        'range':[0,10]
    }
}
params = {
    'Roll':'#'
}

class Script(LabTools.UserScript):
