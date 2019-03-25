import time
import random
import visa

try:
    from . import Tool
except:
    import Tool

param = {'T1': 'K', 'T2': 'K', 'T3': 'K'}

INTERFACE = Tool.INTF_GPIB


# READ THE MANUAL for RS232 interfacing page 9 chapter 3.3 have to find a 25 to 9 pin connector, we only care about pins 1-3

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False,**kwargs):
        print(kwargs)
        if "interface" in kwargs:
            itfc = kwargs.pop("interface")
        else:
            itfc = INTERFACE

        name='ITC503S'
        if "name" in kwargs:
            name = kwargs.pop("name")
            print(name)
        super(Instrument, self).__init__(resource_name, name=name, debug=debug, interface = itfc, read_termination = '\r', **kwargs)

        self.term_chars = '\r'

        #self.term_chars = '\r'
        #self.connection.read_termination = '\r'
        self.setControl(0, 1)
        #self.write('$W1000')

    def measure(self, channel):
        if channel in self.last_measure:
            if channel == 'T1':
                if not self.DEBUG:
                    self.write('R1')
                    is_empty = True
                    idx = 0
                    while is_empty:
#                        print(idx)
                        idx = idx + 1
                        answer = self.read()
#                        print(answer)
                        if answer:
                            is_empty = False
                    answer = float(answer.split('R')[1])
                    #self.read() # weird empty string after each reading - this is to get rid of that
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'T2':
                if not self.DEBUG:
                    self.write('R2')
                    is_empty = True
                    answer = ''
                    while is_empty:
                        temp_answer = self.read()
                        answer= answer + temp_answer
#                        print(answer)
                        if temp_answer:
                            is_empty = False
                    answer = float(answer.split('R')[1])
                    #self.read() # weird empty string after each reading - this is to get rid of that
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'T3':
                if not self.DEBUG:
                    # 0 #this is to be defined for record sweep
                    self.write('R3')
                    #self.write('$W1000')
                    answer = ''
                    idx = 0
                    is_empty = True
                    while is_empty:
                        idx = idx + 1
                        #print(idx)
                        temp_answer = self.read()
                        answer= answer + temp_answer
#                        print(answer)
                        if temp_answer:
                            is_empty = False
                    answer = answer.split('R')
#                    print("%s" % answer)
                    answer = float(answer[1])
                    #self.read() # weird empty string after each reading - this is to get rid of that
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer
        
           # set controls for locked (0 = False, 1 = True) and remote (0 = local, 1 = remote)
    def setControl(self, locked, remote):
        if locked and remote:
            self.write('$C1')
        elif locked:
            self.write('$C0')
        elif remote:
            self.write('$C3')
        else:
            self.write('$C2')

if (__name__ == '__main__'):
    i = Instrument("GPIB0::24")
#    print(i.write('R1'))
#    is_empty = True
#    idx = 0
#    while is_empty:
#        idx = idx+1
#        
#        answer = i.read()
#        print("%i:'%s'"%(idx, answer))
#        if answer:
#            is_empty = False
#    print(answer)
            
    print(i.measure('T1'))
    print(i.measure('T3'))
    print(i.measure('T2'))
    print(i.measure('T3'))
    print(i.measure('T1'))
    print(i.measure('T3'))
    print(i.measure('T2'))
    print(i.measure('T1'))
    print(i.measure('T3'))
    print(i.measure('T1'))
    print(i.measure('T3'))
    print(i.measure('T2'))
    print(i.measure('T1'))


    i.close()

#    term_char = '\r' 
#    rm = visa.ResourceManager()
#    i = rm.get_instrument("GPIB0::24")
#    i.write("$C3" + term_char)
#    i.write('R3' + term_char)
#    i.read()
#    i.close()
    #print(i.ask('V\r'))
    #i.write('$R2\r')
    #a = i.read()
    #print(a)
