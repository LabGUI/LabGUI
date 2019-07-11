"""
Created July 11th, 2019

@author: zackorenberg

This widget is meant to be used both internally/externally to synchronize independent datafiles. It will treat each data file as a set, and therefore support elementary set operations
"""


from LocalVars import USE_PYQT5

if USE_PYQT5:
    from PyQt5 import ( QtGui, QtCore )
else:
    from PyQt4 import ( QtGui, QtCore )

import numpy as np
import math

try:
    from LabTools.IO.IOTool import load_file_windows
except:
    load_file_windows = None

# the following should remain constant, however should any changes occur to TIME.py, such as renaming the file,
# or any of the drivers existing channels/functionality can cause this to change
# A cool feature would be to automatically determine which is the time driver, and find its abs/rel time (t/dt)
ABSOLUTE_TIME = "TIME[].Time"
RELATIVE_TIME = "TIME[].dt"

class DataSet(object):
    def __init__(self, file='', *args, **kwargs):
        # this will read each file, and create the data set object.
        # the dataset object will contain a headers variable, raw_data variable

        self.headers = {}
        self.instruments = []
        self.raw_data = []

        if 'splitchar' in kwargs:
            splitchar = kwargs['splitchar']
        else:
            splitchar = ', '

        if load_file_windows is None:
            with open(file, 'r') as f:
                for line in f.readlines():
                    if line.startswith("#"):
                        # get the label identifier :
                        #   I for instrument,
                        #   T for start time in seconds since epoch
                        label_id = line[1:2]
                        if label_id == 'T':
                            self.headers['start_time'] = float(line[2:].rstrip("\n").strip("'"))
                        elif label_id == 'I':
                            self.headers['instr'] = line[2:].split(splitchar)
                        # rest copied verbatim from IOTool
                        elif label_id == 'P':
                            self.headers['param'] = line[2:].split(splitchar)
                        elif label_id == 'C':
                            self.headers['channel_labels'] = line[2:].split(', u')
                            if len(self.headers['channel_labels']) == 1:
                                self.headers['channel_labels'] = \
                                    self.headers['channel_labels'][0].split(splitchar)
                            else:
                                self.headers['channel_labels'][0] = \
                                    self.headers['channel_labels'][0][1:]
                        elif label_id == 'D':
                            if 'data' not in self.headers.keys():
                                self.headers['data'] = []
                            self.headers['data'].append(line[2:].split(splitchar))
            self.raw_data = np.loadtxt(file)
        else:
            self.raw_data, self.headers = load_file_windows(file)

        if 'start_time' not in self.headers:
            print("Start time not specified, there may be unexpected results")
            self.headers['start_time'] = 0
        # make all time absolute
        self.times = []
        if RELATIVE_TIME in self.headers['instr']:
            column = self.headers['instr'].index(RELATIVE_TIME)
            self.abs_data = self.raw_data.copy()
            self.rel_data = self.raw_data.copy()
            for i, entry in enumerate(self.abs_data):
                self.abs_data[i][column] += self.headers['start_time']
                self.times.append( self.abs_data[i][column] ) # needed for min/max
        elif ABSOLUTE_TIME in self.headers['instr']:
            column = self.headers['instr'].index(ABSOLUTE_TIME)
            self.abs_data = self.raw_data.copy()
            self.rel_data = self.raw_data.copy()
            for i, entry in enumerate(self.rel_data):
                self.times.append( self.rel_data[i][column] ) # still in abs time
                self.rel_data[i][column] -= self.headers['start_time']


        # now to parse instrument list, and strip ports, leaving it in the same order as in headers
        self.instruments = self.instr_name = self.headers['instr']

        for index, instr in enumerate(self.instr_name):
            if instr in [RELATIVE_TIME, ABSOLUTE_TIME]:
                continue
            # we want to strip '[possible port name]' from instrument
            # assuming in form 'INSTRUMENT[PORT].PARAM'
            driver, rest = instr.split('[')
            param = rest.split(']')[1]
            self.instr_name[index] = driver + param

    def min_time(self):
        return min(self.times)
    def max_time(self):
        return max(self.times)

class SyncData(object):

    def __init__(self, file_list = [], output_file='combination.dat', default=RELATIVE_TIME, *args, **kwargs):
        """

        :param file_list:
            list of paths to data files to sync
        :param output_file:
            name of output file (will be default for all save functions, unless otherwise specified
        :param default:
            either RELATIVE_TIME or ABSOLUTE_TIME, will save the sync'd data in the specified format
        :param args:
            to be passed to DataSet
        :param kwargs:
            to be passed to DataSet
        """
        self.files = file_list

        self.sets = []

        self.output_file = output_file
        self.default = default

        if 'exclude' in kwargs:
            if not isinstance(kwargs['exclude'], list):
                self.exclude = [kwargs['exclude']]
            else:
                self.exclude = kwargs['exclude']

        for file in file_list:
            self.sets.append(DataSet(file, *args, **kwargs))


        self.data_all = None
        self.headers_all = None
        self.mins = None
        self.maxs = None

    def parse_data(self):
        instrs = [ABSOLUTE_TIME]
        instrs_sep = []
        headers = {
            'instr':[],
            'param':[],
            'channel_labels':[],
            'data':[],
            'hdr':[]
        }
        data_combo = []
        margins = []
        start_times = []
        mins = [] # to be used for union/intersection/difference
        maxs = [] # ^
        for i, dset in enumerate(self.sets):
            head = dset.headers['instr']
            start = dset.headers['start_time']
            bounds = (dset.min_time(), dset.max_time())
            abs_data = dset.abs_data

            margin = len(instrs)
            # start parsing
            indices = list(range(len(head)))

            # Figure out where time is
            if ABSOLUTE_TIME in head:
                index = head.index(ABSOLUTE_TIME)
            elif RELATIVE_TIME in head: # doesnt matter, as abs_data is absolute
                index = head.index(RELATIVE_TIME)

            # make it first axis
            if index != 0:
                indices[0] = index
                indices[index] = 0

                head[index] = head[0]
                head[0] = ABSOLUTE_TIME

                # parse all headers, put them in some order
                for header in dset.headers.keys():
                    if header == 'instr':
                        headers['instr'] += head[1:]
                    else:
                        swapped_head = dset.headers[header]
                        if isinstance(swapped_head, list):
                            temp = swapped_head[index]
                            swapped_head[index] = swapped_head[0]
                            swapped_head[0] = temp
                            headers[header].append(swapped_head)
                        elif isinstance(swapped_head, dict):
                            temp = {}
                            for key, value in swapped_head.keys():
                                temp[str(key)+str(i)] = value
                            headers[header].append(temp)
                        else: # typically a string, such as 'hdr', can just be appended
                            headers[header].append(swapped_head)
                #for key in headers.keys():
                #    if len(headers[key]) < i+1: # meaning its missing, must as emtpy
                #        if key == 'data':
                #            headers[key].append({})
                #        elif key == 'hdr':
                #            headers[key].append("")
                #        else:
                #            headers[key].append([]) # may want to consider changing this

                # modify data
                abs_data.T[[0, index]] = abs_data.T[[index, 0]] # the most elegant way I could think of
            else:
                head[0] = ABSOLUTE_TIME # we want it all in abs, we can convert later


            # now make data
            instrs += head[1:] # so time is not added
            instrs_sep.append(head)
            margins.append(margin-1)
            mins.append(bounds[0])
            maxs.append(bounds[1])
            start_times.append(start) # easiest and most readable way to access
            data_combo.append(np.array(abs_data, dtype='float')) # just incase
        total = len(instrs)
        # time to flatten data
        self.data_all = None
        self.headers_all = {
            'instr':instrs,
            'param':[ABSOLUTE_TIME.split('.')[-1]],
            'channel_labels':[ABSOLUTE_TIME.split('.')[-1] + "(s)"],
            'data':{},
            'hdr':""
        }
        self.maxs = maxs
        self.mins = mins
        self.start_times = start_times
        for i, data in enumerate(data_combo):
            # since all lists were appended together, they have to be the same size. i iterates them all in order
            cols = [ data[:, j] for j in range(np.size(data, 1)) ] # we want each COLUMN

            # we need the resulting rows to have `total` columns. the before is margin[i]
            rows = np.full(( np.size(data, 0), total ), np.nan) # make a row x col matrix filled with nan
            for j in range(np.size(data, 1)):
                if j == 0:
                    rows[:,0] = cols[0]
                else:
                    index = margins[i] + j
                    rows[:, index] = cols[j]
            # add it to array
            if self.data_all is None:
                self.data_all = np.array(rows, dtype='float')
            else:
                self.data_all = np.append(self.data_all, rows, axis=0)

        for head in headers['param']:
            if len(head) > 0:
                self.headers_all['param'] += head[1:]
        for head in headers['channel_labels']:
            if len(head) > 0:
                self.headers_all['channel_labels'] += head[1:]
        for head in headers['data']:
            self.headers_all['data'].update(head)
        self.headers_all['hdr'] = "\n".join(headers['hdr'])
        self.data_all.sort(axis=0) # sort with respect to time
        return self.data_all

    def union(self, output_file=None):
        if output_file is None:
            output_file = self.output_file
        # just print everything together
        header = self.headers_all
        if self.default == RELATIVE_TIME:
            start_time = min(self.start_times)
            for i, row in enumerate(self.data_all):
                self.data_all[i][0] -= start_time # make relative time
            header['instr'] = RELATIVE_TIME,
            header['param'] = RELATIVE_TIME.split('.')[-1]
            header['channel_labels'] = RELATIVE_TIME.split('.')[-1] + "(s)"










if __name__ == "__main__":
    files = [r'C:\Users\admin\Documents\LabGUI\scratch\190711__004.dat',
             r'C:\Users\admin\Documents\LabGUI\scratch\190711__005.dat',
             r'C:\Users\admin\Documents\LabGUI\scratch\190711__006.dat',
             r'C:\Users\admin\Documents\LabGUI\scratch\190711__007.dat',
             r'C:\Users\admin\Documents\LabGUI\scratch\190711__008.dat'
    ]

    sync = SyncData(files, output_file=r'C:\Users\admin\Documents\LabGUI\scratch\190711__union.dat')

    dat = sync.parse_data()
    np.savetxt('test.dat', dat)
