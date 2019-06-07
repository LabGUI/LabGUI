# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@author: zackorenberg

Agilent 33220A Function Waveform Generator
"""
try:
    from . import Tool
except:
    import Tool


param = {
    'Amplitude' : 'V',
    'MaxVolt' : 'V',
    'MinVolt' : 'V',
    'Frequency' : 'Hz',
    'Offset' : 'V_DC'
}

INTERFACE = Tool.INTF_GPIB
NAME = 'A33220A'

REMOTE_LOCK = False

class Instrument(Tool.MeasInstr):
    """"This class is the driver of the instrument *NAME*"""""

    def __init__(self, resource_name, debug=False, **kwargs):
        if "interface" in kwargs:
            itfc = kwargs.pop("interface")
        else:
            itfc = INTERFACE
        super(Instrument, self).__init__(resource_name,
                                          name=NAME,
                                          debug=debug,
                                          interface=itfc,
                                          **kwargs)
        if not REMOTE_LOCK:
            self.connection.control_ren(0)

    def measure(self, channel):

        if self.DEBUG:
            print("Debug mode activated")

        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'Amplitude':
                    answer = self.ask("VOLT?")
                    try:
                        answer = float(answer)
                    except ValueError:
                        print("Unable to convert response: ", answer)
                        answer = 0
                elif channel == 'MaxVolt':
                    answer = self.ask("VOLT? MAX")
                    try:
                        answer = float(answer)
                    except ValueError:
                        print("Unable to convert response: ", answer)
                        answer = 0
                elif channel == 'MinVolt':
                    answer = self.ask("VOLT? Min")
                    try:
                        answer = float(answer)
                    except ValueError:
                        print("Unable to convert response: ", answer)
                        answer = 0
                elif channel == 'Frequency':
                    answer = self.ask("FREQ?")
                    try:
                        answer = float(answer)
                    except ValueError:
                        print("Unable to convert response: ", answer)
                        answer = 0
                elif channel == 'Offset':
                    answer = self.ask("VOLT:OFFS?")
                    try:
                        answer = float(answer)
                    except ValueError:
                        print("Unable to convert response: ", answer)
                        answer = 0
            else:
                answer = 123.4

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        self.last_measure[channel] = answer
        return answer




    def reset(self):
        self.write("*RST")

    def clear(self):
        self.write("*CLS")

    def get_function(self):
        resp = self.ask("APPL?")[1:-2] #enclosed by quotes then newline for some reason

        resp = resp.split(' ')
        funct = resp[0]
        values = resp[1].replace('\n','').split(',')

        return {
            'Function' :funct,
            'Frequency':float(values[0]),
            'Amplitude':float(values[1]),
            'Offset'   :float(values[2])
        }
    def set_function(self, shape, frequency, amplitude, offset=0):
        """
        Uses APPLY command to change all at the same time
        :param shape: Shape, conforming to same as set_shape
        :param frequency: in Hz
        :param amplitude: in Volt (pp)
        :param offset: in Volt (DC)
        :return:
        """
        # do checks
        shape = self.is_valid(shape)
        if not shape:
            print("Invalid shape, must be of the following type: ", " ".join(self.valid_shapes_full()))
            return False

        try:
            frequency = float(frequency)
        except:
            if frequency is None or frequency.lower() == 'def':
                frequency = 'DEF'
            else:
                print("Invalid frequency")

        try:
            amplitude = float(amplitude)
        except:
            if amplitude is None or amplitude.lower() == 'def':
                amplitude = 'DEF'
            else:
                print("Invalid amplitude")

        try:
            offset = float(offset)
        except:
            if offset is None or offset.lower() == 'def':
                offset = 'DEF'
            else:
                print("Invalid offset")

        self.write("APPL:"+str(shape)+" "+str(frequency)+", "+str(amplitude)+", "+str(offset))

    def set_shape(self, shape):
        """
        Options are;
        SIN - or sin
        SQU - or square
        DC  - or DC
        :param shape:
        :return:
        """
        # do check, return valid shape
        shape = self.is_valid(shape)
        if shape:
            self.write("FUNC:SHAP "+str(shape))
        else:
            print("Invalid shape, must be of the following type: " + " ".join(self.valid_shapes_full()))
            return False

    def set_frequency(self, frequency):
        """

        :param frequency: frequency in HZ
        :return:
        """
        if type(frequency) == str:
            if not frequency.isdigit():
                print("Invalid frequency")
                return False
        elif type(frequency) != int and type(frequency) != float:
            print("Invalid frequency")
            return False
        self.write("FREQ "+str(frequency))
        return True



    def set_amplitude(self, amplitude):
        """

        :param amplitude: in VOLTS
        :return:
        """
        #check for upward bound?
        if type(amplitude) == str:
            if not amplitude.isdigit():
                print("Invalid amplitude")
                return False
        elif type(amplitude) != int and type(amplitude) != float:
            print("Invalid amplitude")
            return False
        self.write("VOLT "+str(amplitude))
        return True

    def set_offset(self, offset=0):
        """
        Offset (in VOLTS
        :param offset:
        :return:
        """
        if type(offset) == str:
            if not offset.isdigit():
                return False
        elif type(offset) != int and type(offset) != float:
            return False
        self.write("VOLT:OFFS " + str(offset))
        return True

    def valid_shapes_full(self):
        return [
            'sinusoid',
            'square',
            'triangle',
            'ramp',
            'noise',
            'dc',
            'user'
        ]
    def is_valid(self, wave_type:str):
        valid_full = [
            'sinusoid',
            'square',
            'triangle',
            'ramp',
            'noise',
            'dc',
            'user'
        ]
        valid_short = [
            'SIN',
            'SQU',
            'TRI',
            'RAMP',
            'NOIS',
            'DC',
            'USER'
        ]
        if wave_type.upper() in valid_short:
            return wave_type.upper()
        elif wave_type.lower() in valid_full:
            return valid_short[valid_full.index(wave_type.lower())]
        else: #try to find best fit
            if len(wave_type) < 2:
                return False #otherwise it can match the wrong one, specificall sin/squ combo
            for x in valid_short:
                if wave_type.upper() in x:
                    return x
            #if it reaches here, it didnt match a short one, so check long ones
            for y in valid_full:
                if wave_type.lower() in y:
                    return valid_short[valid_full.index(wave_type.lower())]
            #if it reached here, invalid function
            return False
if __name__ == "__main__":
    i = Instrument("GPIB::1", debug=False)








