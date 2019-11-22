"""
Created July 11th, 2019

@author: zackorenberg

This widget is meant to be used both internally/externally to synchronize independent datafiles. It will treat each data
file as a set, and therefore support elementary set operations

This can be used to merge separate datafiles in such a way

files = ["191008__001.dat", "KT2400_VoltagePulseSweep_191008__001.dat"] # files to load

sync = SyncData(files)                                                  # creates SyncData object, which loads data from all files

sync.union("union_dat.dat")                                             # performs union, saves to union_dat.dat

sync.symmetric_difference("sdat_symdiff.dat")                           # performs symmetric difference on all data,
                                                                        # saves to sdat_symdiff.dat

sync.difference(0, "dat_diff.dat")                                      # performs difference of first dataset with the
                                                                        # rest (index from 0 to n-1) and saves to dat_diff.dat

sync.intersect("dat_intersect.dat")                                     # performs intersect and saves to dat_intersect.dat
"""


from LocalVars import USE_PYQT5

if USE_PYQT5:
    from PyQt5 import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

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

DEFAULT_OUTPUT = None # alternatively, you can set it to a file like "combination.dat"

class DataSet(object):
    def __init__(self, file="", *args, **kwargs):
        # this will read each file, and create the data set object.
        # the dataset object will contain a headers variable, raw_data variable

        self.headers = {"hdr": ""}
        self.instruments = []
        self.raw_data = []

        if "splitchar" in kwargs:
            splitchar = kwargs["splitchar"]
        else:
            splitchar = ", "

        if load_file_windows is None:
            with open(file, "r") as f:
                for line in f.readlines():
                    if line.startswith("#"):
                        # get the label identifier :
                        #   I for instrument,
                        #   T for start time in seconds since epoch
                        label_id = line[1:2]
                        if label_id == "T":
                            self.headers["start_time"] = float(
                                line[2:].rstrip("\n").strip("'")
                            )
                        elif label_id == "I":
                            self.headers["instr"] = line[2:].split(splitchar)
                        # rest copied verbatim from IOTool
                        elif label_id == "P":
                            self.headers["param"] = line[2:].split(splitchar)
                        elif label_id == "C":
                            self.headers["channel_labels"] = line[2:].split(", u")
                            if len(self.headers["channel_labels"]) == 1:
                                self.headers["channel_labels"] = self.headers[
                                    "channel_labels"
                                ][0].split(splitchar)
                            else:
                                self.headers["channel_labels"][0] = self.headers[
                                    "channel_labels"
                                ][0][1:]
                        elif label_id == "D":
                            if "data" not in self.headers.keys():
                                self.headers["data"] = []
                            self.headers["data"].append(line[2:].split(splitchar))
                        else:
                            self.headers["hdr"] += line[1:]

            self.raw_data = np.loadtxt(file)
        else:
            self.raw_data, self.headers = load_file_windows(file)

        if "start_time" not in self.headers:
            print("Start time not specified, there may be unexpected results")
            self.headers["start_time"] = 0

        if "data" not in self.headers:
            self.headers["data"] = {}
        # make all time absolute
        self.times = []
        if RELATIVE_TIME in self.headers["instr"]:
            column = self.headers["instr"].index(RELATIVE_TIME)
            self.abs_data = self.raw_data.copy()
            self.rel_data = self.raw_data.copy()
            for i, entry in enumerate(self.abs_data):
                self.abs_data[i][column] += self.headers["start_time"]
                self.times.append(self.abs_data[i][column])  # needed for min/max
            self.column = column
        elif ABSOLUTE_TIME in self.headers["instr"]:
            column = self.headers["instr"].index(ABSOLUTE_TIME)
            self.abs_data = self.raw_data.copy()
            self.rel_data = self.raw_data.copy()
            for i, entry in enumerate(self.rel_data):
                self.times.append(self.rel_data[i][column])  # still in abs time
                self.rel_data[i][column] -= self.headers["start_time"]
            self.column = column
        else:
            """
             it is now imperative to determine whether or not the datafile is in absolute or relative time.
             In order to do this, it is safe to compare the supplied time with the first datapoint from the first
             column, which is assumed to be the time datapoints if it is not specified. The difference between these
             times can help us determine whether or not it is relative or absolute time. NOTE: if start_time = 0,
             then the opposite must be applied
            """
            temporary_boolean = (
                math.fabs(self.headers["start_time"] - self.raw_data[0][0]) < 30000000
            )  # aprx 1 yr
            self.abs_data = self.raw_data.copy()
            self.rel_data = self.raw_data.copy()
            if self.headers["start_time"] == 0:  # can still produce unexpected results
                temporary_boolean = not temporary_boolean
            if temporary_boolean:  # must be absolute, parse it as such
                for i, entry in enumerate(self.rel_data):
                    self.times.append(self.rel_data[i][0])  # still in abs time
                    self.rel_data[i][0] -= self.headers["start_time"]
            else:
                for i, entry in enumerate(self.abs_data):
                    self.abs_data[i][0] += self.headers["start_time"]
                    self.times.append(self.abs_data[i][0])  # needed for min/max

        # now to parse instrument list, and strip ports, leaving it in the same order as in headers
        self.instruments = self.instr_name = self.headers["instr"]

        for index, instr in enumerate(self.instr_name):
            if instr in [RELATIVE_TIME, ABSOLUTE_TIME]:
                continue
            # we want to strip '[possible port name]' from instrument
            # assuming in form 'INSTRUMENT[PORT].PARAM'
            if "[" in instr:
                driver, rest = instr.split("[")
                param = rest.split("]")[1]
                self.instr_name[index] = driver + param
            else:
                self.instr_name[index] = instr

    def min_time(self):
        try:
            return min(self.times)
        except:
            return 0

    def max_time(self):
        try:
            return max(self.times)
        except:
            return 0


class SyncData(object):
    def __init__(
        self,
        file_list=[],
        output_file=DEFAULT_OUTPUT,
        default=RELATIVE_TIME,
        *args,
        **kwargs
    ):
        """

        :param file_list:
            list of paths to data files to sync
        :param output_file:
            name of output file (will be default for all save functions, unless otherwise specified)
            if None, it will not save, only return data
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

        if "exclude" in kwargs:
            if not isinstance(kwargs["exclude"], list):
                self.exclude = [kwargs["exclude"]]
            else:
                self.exclude = kwargs["exclude"]

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
            "instr": [],
            "param": [],
            "channel_labels": [],
            "data": [],
            "hdr": [],
            "start_time": [],
        }
        data_combo = []
        margins = []
        start_times = []
        mins = []  # to be used for union/intersection/difference
        maxs = []  # ^
        for i, dset in enumerate(self.sets):
            head = dset.headers["instr"]
            start = dset.headers["start_time"]
            bounds = (dset.min_time(), dset.max_time())
            abs_data = dset.abs_data

            margin = len(instrs)
            # start parsing
            indices = list(range(len(head)))

            # Figure out where time is
            if ABSOLUTE_TIME in head:
                index = head.index(ABSOLUTE_TIME)
            elif RELATIVE_TIME in head:  # doesnt matter, as abs_data is absolute
                index = head.index(RELATIVE_TIME)

            # make it first axis
            if index != 0:
                indices[0] = index
                indices[index] = 0

                head[index] = head[0]
                head[0] = ABSOLUTE_TIME

                # parse all headers, put them in some order
                for header in dset.headers.keys():
                    # print(header)
                    if header == "instr":
                        headers["instr"] += head[1:]
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
                                temp[str(key) + str(i)] = value
                            headers[header].append(temp)
                        else:  # typically a string, such as 'hdr', can just be appended
                            headers[header].append(swapped_head)
                # for key in headers.keys():
                #    if len(headers[key]) < i+1: # meaning its missing, must as emtpy
                #        if key == 'data':
                #            headers[key].append({})
                #        elif key == 'hdr':
                #            headers[key].append("")
                #        else:
                #            headers[key].append([]) # may want to consider changing this

                # modify data
                abs_data.T[[0, index]] = abs_data.T[
                    [index, 0]
                ]  # the most elegant way I could think of
            else:
                head[0] = ABSOLUTE_TIME  # we want it all in abs, we can convert later
                for header in dset.headers.keys():
                    if header == "instr":
                        headers["instr"] += head[1:]
                    else:
                        swapped_head = dset.headers[header]
                        if isinstance(swapped_head, list):
                            headers[header].append(swapped_head)
                        elif isinstance(swapped_head, dict):  # data
                            temp = {}
                            for key, value in swapped_head.keys():
                                temp[str(key) + str(i)] = value
                            headers[header].append(temp)
                        else:  # typically a string, such as 'hdr', can just be appended
                            headers[header].append(swapped_head)

            # now make data
            instrs += head[1:]  # so time is not added
            instrs_sep.append(head)
            margins.append(margin - 1)
            mins.append(bounds[0])
            maxs.append(bounds[1])
            start_times.append(start)  # easiest and most readable way to access
            data_combo.append(np.array(abs_data, dtype="float"))  # just incase
        total = len(instrs)
        # time to flatten data
        self.data_all = None
        self.headers_all = {
            "instr": instrs,
            "param": [ABSOLUTE_TIME.split(".")[-1]],
            "channel_labels": [ABSOLUTE_TIME.split(".")[-1] + "(s)"],
            "data": {},
            "hdr": "",
            "start_time": [],
        }
        self.maxs = maxs
        self.mins = mins
        self.start_times = start_times
        for i, data in enumerate(data_combo):
            # since all lists were appended together, they have to be the same size. i iterates them all in order
            cols = [data[:, j] for j in range(np.size(data, 1))]  # we want each COLUMN

            # we need the resulting rows to have `total` columns. the before is margin[i]
            rows = np.full(
                (np.size(data, 0), total), np.nan
            )  # make a row x col matrix filled with nan
            for j in range(np.size(data, 1)):
                if j == 0:
                    rows[:, 0] = cols[0]
                else:
                    index = margins[i] + j
                    rows[:, index] = cols[j]
            # add it to array
            if self.data_all is None:
                self.data_all = np.array(rows, dtype="float")
            else:
                self.data_all = np.append(self.data_all, rows, axis=0)

        for head in headers["param"]:
            if len(head) > 0:
                self.headers_all["param"] += head[1:]
        for head in headers["channel_labels"]:
            if len(head) > 0:
                self.headers_all["channel_labels"] += head[1:]
        for head in headers["data"]:
            self.headers_all["data"].update(head)
        # parse hdr
        hdr_list = []
        for hdr in headers["hdr"]:
            if hdr != "":
                hdr_list.append(hdr)
        headers["hdr"] = hdr_list

        self.headers_all["hdr"] = "\n".join(headers["hdr"])
        self.headers_all["start_time"] = min(headers["start_time"])
        self.data_all = self.data_all[self.data_all[:, 0].argsort()]
        return self.data_all

    def union(self, output_file=None):
        """
        Performs union of all data sets (merges)
        :param output_file: place to save
        :return: data
        """
        if output_file is None:
            output_file = self.output_file

        if self.data_all is None:
            self.parse_data()
        # just print everything together
        header = self.headers_all
        data = self.data_all.copy()
        start_time = min(self.start_times)
        if self.default == RELATIVE_TIME:
            for i, row in enumerate(data):
                data[i][0] -= start_time  # make relative time
            header["instr"][0] = RELATIVE_TIME
            header["param"][0] = RELATIVE_TIME.split(".")[-1]
            header["channel_labels"][0] = RELATIVE_TIME.split(".")[-1] + "(s)"
        header["start_time"] = start_time

        self.save(header, data, output_file=output_file)

        return data

    def intersect(self, output_file=None):
        """
        Performs intersect of all data sets, so intervals covered are present in all
        :param output_file: place to save
        :return: data
        """
        if output_file is None:
            output_file = self.output_file

        if self.data_all is None:
            self.parse_data()

        header = self.headers_all
        # we need max of mins, and mins of maxs for itnersect
        start_time = max(
            self.start_times
        )  # cuz it is the last one that'll be in the intersection
        st_point = max(
            [
                min(self.data_all[~np.isnan(self.data_all[:, i + 1])][:, 0])
                for i in range(np.size(self.data_all, 1) - 1)
            ]
        )  # take max of mins of time
        sp_point = min(
            [
                max(self.data_all[~np.isnan(self.data_all[:, i + 1])][:, 0])
                for i in range(np.size(self.data_all, 1) - 1)
            ]
        )  # take mins of maxs of time

        boolean_arr = np.array(
            [st_point <= row[0] and row[0] <= sp_point for row in self.data_all]
        )

        data = self.data_all[boolean_arr]

        if self.default == RELATIVE_TIME:
            for i, row in enumerate(data):
                data[i][0] -= start_time  # make relative time
            header["instr"][0] = RELATIVE_TIME
            header["param"][0] = RELATIVE_TIME.split(".")[-1]
            header["channel_labels"][0] = RELATIVE_TIME.split(".")[-1] + "(s)"
        header["start_time"] = start_time

        self.save(header, data, output_file=output_file)

        return data

    def align_min(self, output_file=None):
        """
        Intersect for just the lower bounds; aligns the startpoints (max of mins)
        """
        if output_file is None:
            output_file = self.output_file

        if self.data_all is None:
            self.parse_data()

        header = self.headers_all
        # we need max of mins, and mins of maxs for itnersect
        start_time = max(
            self.start_times
        )  # cuz it is the last one thatll be in the intersection
        st_point = max(
            [
                min(self.data_all[~np.isnan(self.data_all[:, i + 1])][:, 0])
                for i in range(np.size(self.data_all, 1) - 1)
            ]
        )  # take max of mins of time

        boolean_arr = np.array([st_point <= row[0] for row in self.data_all])

        data = self.data_all[boolean_arr]

        if self.default == RELATIVE_TIME:
            for i, row in enumerate(data):
                data[i][0] -= start_time  # make relative time
            header["instr"][0] = RELATIVE_TIME
            header["param"][0] = RELATIVE_TIME.split(".")[-1]
            header["channel_labels"][0] = RELATIVE_TIME.split(".")[-1] + "(s)"
        header["start_time"] = start_time

        self.save(header, data, output_file=output_file)

        return data

    def align_max(self, output_file=None):
        """
        Intersect for just the upper bounds; aligns the endpoints (min of maxs)
        """
        if output_file is None:
            output_file = self.output_file

        if self.data_all is None:
            self.parse_data()

        header = self.headers_all
        # we need max of mins, and mins of maxs for itnersect
        start_time = min(self.start_times)  # WILL BE FIRST FOR THIS ONE
        sp_point = min(
            [
                max(self.data_all[~np.isnan(self.data_all[:, i + 1])][:, 0])
                for i in range(np.size(self.data_all, 1) - 1)
            ]
        )  # take mins of maxs of time

        boolean_arr = np.array([row[0] <= sp_point for row in self.data_all])

        data = self.data_all[boolean_arr]

        if self.default == RELATIVE_TIME:
            for i, row in enumerate(data):
                data[i][0] -= start_time  # make relative time
            header["instr"][0] = RELATIVE_TIME
            header["param"][0] = RELATIVE_TIME.split(".")[-1]
            header["channel_labels"][0] = RELATIVE_TIME.split(".")[-1] + "(s)"
        header["start_time"] = start_time

        self.save(header, data, output_file=output_file)

        return data

    def difference(self, A, output_file=None, sets=None):
        """
        Applies set operation A\{set} for all datasets in 'sets' list,
        where A is the index of the dataset to subtract from (0..n-1)

        A list of datasets can be specified to perform the operation exclusively on those datasets
        :param A: Set to subtract from
        :param output_file: File to save new data to
        :param sets: sets to subtract from A
        :return: new_data
        """
        if output_file is None:
            output_file = self.output_file
        if sets is None:
            sets = self.sets
        if A not in list(range(len(sets))):
            print("Invalid range")
            return

        A_set = sets[A]
        A_arr = A_set.abs_data
        idx = A_set.column

        bounds = []
        for i, set in enumerate(sets):
            if i != A:
                bounds.append((set.min_time(), set.max_time()))

        def bool_from_bounds(t, bounds):
            for min, max in bounds:
                if min <= t and t <= max:
                    return True
            return False

        data = A_arr.copy()
        boolean_arr = [bool_from_bounds(row[idx], bounds) for row in data]
        for j in [i for i in range(np.size(A_arr, 1)) if i != A_set.column]:
            data[boolean_arr, j] = np.inf

        header = A_set.headers
        start_time = header["start_time"]
        if self.default == RELATIVE_TIME:
            for i, row in enumerate(data):
                data[i][idx] -= start_time  # make relative time
            header["instr"][idx] = RELATIVE_TIME
            header["param"][idx] = RELATIVE_TIME.split(".")[-1]
            header["channel_labels"][idx] = RELATIVE_TIME.split(".")[-1] + "(s)"

        self.save(header, data, output_file=output_file)

        return data

    def symmetric_difference(self, output_file):
        """
        Computes the symmetric difference of the union and intersect.

        This can also be considered the intersect compliment
        """

        self.union(output_file)
        uset = DataSet(output_file)

        self.intersect(output_file)
        iset = DataSet(output_file)

        # now to difference: union \ intersect

        return self.difference(0, output_file, [uset, iset])

    def save(self, header, data, output_file=None):
        """
        this function is used in operation functions in order to save processed data
        """
        if output_file is None:
            return # do not save
        if header["hdr"] != "":
            header_str = "# " + header["hdr"].replace("\n", "\n#") + "\n"

        if len(header["data"]) > 0:
            for key, value in header["data"].items():
                header_str += "#D'%s', '%s'\n" % (key, value)
        header_str = "#C" + str(header["channel_labels"]).strip("[]") + "\n"
        header_str += "#I" + str(header["instr"]).strip("[]") + "\n"

        header_str += "#P" + str(header["param"]).strip("[]") + "\n"
        header_str += "#T'" + str(header["start_time"]) + "'\n"
        np.savetxt(output_file, data, header=header_str.rstrip("\n"), comments="")


if __name__ == "__main__":
    # files = ['dat1.dat', 'dat2.dat']
    files = ["191008__001.dat", "KT2400_VoltagePulseSweep_191008__001.dat"]
    sync = SyncData(files)
    # ssync = SyncData([ 's'+file for file in files ])
    sync.union("union_dat.dat")
    sync.symmetric_difference("sdat_symdiff.dat")
    # exit(0)
    # sync = SyncData(files)
    sync.difference(0, "dat_diff.dat")

    # exit(0)
    sync.intersect("dat_intersect.dat")

    exit(0)

    files = [
        r"C:\Users\admin\Documents\LabGUI\scratch\190711__004.dat",
        # r'C:\Users\admin\Documents\LabGUI\scratch\190711__005.dat',
        r"C:\Users\admin\Documents\LabGUI\scratch\190711__006.dat",
        r"C:\Users\admin\Documents\LabGUI\scratch\190711__007.dat",
        r"C:\Users\admin\Documents\LabGUI\scratch\190711__008.dat",
    ]

    sync = SyncData(
        files, output_file=r"C:\Users\admin\Documents\LabGUI\scratch\190711__union.dat"
    )

    dat = sync.parse_data()
    header = sync.headers_all
    sync.save(data=dat, header=header, output_file="realtest.dat")

