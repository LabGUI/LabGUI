#!/usr/bin/env python
import time
try:
    from . import Tool
except:
    import Tool
import random

param = {'0A': 'V', '1A': 'V', '2A': 'V', '3A': 'V',
         '0DC': 'V', '1DC': 'V', '2DC': 'V', '3DC': 'V',
         '0F': 'Hz', '1F': 'Hz', '2F': 'Hz', '3F': 'Hz'}

INTERFACE = Tool.INTF_SERIAL


class Instrument(Tool.MeasInstr):
    """
    class to communicate with Highland Technologies T344 signal generator through RS-232

    Parameters
    ----------    
    Name of the port (ie. COM1)

    """

    def __init__(self, resource_name='COM1', debug=False, **kwargs):
        #super(Instrument, self).__init__(resource_name,'T344',debug)
        if resource_name == 'ASRL5::INSTR':
            resource_name = 'COM5'
        super(Instrument, self).__init__(resource_name, 'T344', debug=debug, interface=INTERFACE,
                                         baud_rate=38400, term_chars='\r\n', timeout=1, bytesize=8,
                                         parity='N', stopbits=1, xonxoff=False, dsrdtr=False, **kwargs)


    def write(self, message):
        self.connection.write(message.encode() + b'\r')

    def read(self, numbytes=None):
        if numbytes is None:
            line = self.connection.readline().decode()
            ret = ""
            while line != '':
                ret += line
                line = self.connection.readline().decode()
            return ret
        else:
            return self.connection.read(int(numbytes)).decode()

    def ask(self, message):
        self.write(message)
        return self.read()

    def readline(self):
        return self.connection.readline().decode()


    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                self.write(str(channel))
                return float(self.read().strip().replace(',', ''))
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None

        return answer

    def get_status(self):
        if self.DEBUG == False:
            self.write('ST')
            return self.read()
            """s = ""
            for i in range(25):
                s += self.read()
            return s"""

    def sync(self):
        if self.DEBUG == False:
            self.write('SYNC')
            return self.read()

    def set_freq(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'FREQ ' + '%.3f' % val)
            return self.read()

    def set_freq_raw(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'RAW ' + str(val))
            return self.read()

    def set_amp(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'AMP ' + '%.3f' % val)
            return self.read()

    def get_amp(self, chan):
        if self.DEBUG == False:
            self.write(str(chan) + 'A')
            return float(self.read().strip())

    def set_phase(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'PHASE ' + '%.3f' % val)
            return self.read()

    def set_width(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'W ' + str(val))
            return self.read()

    def set_DC(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'DC ' + '%.3f' % val)
            return self.read()

    def load_sine(self, chan):
        if self.DEBUG == False:
            self.write(str(chan) + 'LOAD SINE')
            return self.read()

    def chan_set(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'SET ' + val)
            return self.read()

    def set_width(self, chan, val):
        if self.DEBUG == False:
            self.write(str(chan) + 'W ' + str(val))
            return self.read()

#    def write(self, stri):
#        if self.DEBUG == False:
#            self.connexion.write(stri + '\r\n')
#
#    def readline(self):
#        if self.DEBUG==False:
#
#            return self.connexion.readline()

    def write_waveform(self, chan, wave):
        if self.DEBUG == False:
            self.write(str(chan) + "K -32000")
            print((self.read2()))
            addr = 0
            self.ser.flush()
            self.ser.flushInput()
            self.ser.flushOutput()

            while addr < 4096:
                piece = str(chan) + "B " + str(addr) + " "

                while addr < 4096 and len(piece + " " + hex(wave[addr])) < 1022:
                    piece = piece + " " + hex(int(wave[addr]))
                    addr = addr + 1
                print(piece)
                self.ser.flushInput()
                self.ser.flushOutput()
                self.write(piece)
                self.ser.flush()
                print((self.read2()))

    def read2(self):
        if self.DEBUG == False:
            ser = self.connexion
            time.sleep(0.5)
            out = ''
            while ser.inWaiting() > 0:
                out += ser.read(1)
            return (out)

    # initialization should open it already
    def reopen(self):
        if self.DEBUG == False:
            self.ser.open()


if __name__ == "__main__":
    t = Instrument('COM35')
    print(t.ask("ST"))
    # print(t.get_amp(0))
    # print(t.measure('Amp1'))
    t.close()
