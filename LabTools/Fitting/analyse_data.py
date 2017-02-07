# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 16:07:25 2013

@author: pfduc
"""

import numpy as np
import matplotlib.pyplot as plt
import logging
try:
    import scipy as sp
    import scipy.optimize
except:
    logging.warning("You can't use the analyse data widget (fits) unless you install scipy module (pip install scipy)")

from collections import OrderedDict
from LabTools.IO import IOTool as io
from Functions import *
#from He4Properties import T_lambda
#from file_treatment_general_functions import load_experiment


PHYS_PARAMS={"exp_decay":["Flow(mbarl/s)", "P(psi)", "Tr(C)", "T(K)"],
"exp_decay_down":["Flow(mbarl/s)", "P(psi)", "T(K)"],
"integrate": ["Flow(mbarl/s)", "PV(mbarl)", "Time(s)"],
"linear":["Slope"]}


def concatenate_list(alist):
    """
    take the elements of a list and return them in a string 
    separated by a ;
    """
    answer = ""
    for i,el in enumerate(alist):
        if i == len(alist)-1:
            answer = answer+"%s"%(el)
        else:
            answer = answer+"%s;"%(el)
    return answer

def rebuild_list(str1):
    """"takes a string and arrange it into a list"""
    answer = str1.split(";")

    return answer

def rebuild_dict(str1,str2):
    """"takes two string and arrange them into a dict"""
    keys = str1.split(";")
    values = str2.split(";")
    answer = OrderedDict()
    for k,v in zip(keys,values):
        answer[k] = v
    return answer
    
class DataSet(object):

    def __init__(self, data, labels, bkg=None):
        #        print "a new data set"
        #        print labels
        self.labels = labels
        self.data = data
        self.params = labels['param']
        self.length = np.size(self.data, 0)
        self.MAXINDEX = self.length - 1

    def length(self):
        return np.size(self.data)

    def get_data(self, param=None):
        if param == None:
            return self.data
        else:
            if param in self.params:
                return self.data[:, self.params.index(param)]
            else:
                # print "analyse_data.DataSet.get_data the parameter you
                # choosed is ",self.params[param], "\n"
                return self.data[:, param]

    def subset(self, start, end, param=None):

        if not start:
            start = 0
        if not end:
            end = self.MAXINDEX

        if start > end:
            temp = end
            end = start
            start = temp

        if start < 0:
            start = 0
        if start > self.MAXINDEX:
            start = self.MAXINDEX

        if end < 0:
            end = 0
        if end > self.MAXINDEX:
            end = self.MAXINDEX

        if param == None:
            return self.data[start:end, :]
        else:
            if param in self.params:
                return self.data[start:end, self.params.index(param)]
            else:
                # print "analyse_data.DataSet.subset the parameter you choosed
                # is ",self.params[param], "\n"
                return self.data[start:end, param]


#        elif limtype=='value':
#            print self.match_value2index(start)
#            print self.match_value2index(end)
# return self
#            return data_set(self.data[self.match_value2index(start):self.match_value2index(end),:],self.labels)
#        else:
#            return None

def restrict_function_parameters(func,param_values):
#        func=io.import_module_func("Fitting","linear")
#    func=exp_decay
    new_func_name="new_func"
    var_names=func.func_code.co_varnames
    old_func_name=func.func_name
#    print old_func_name
    old_func_cmd="%s(%s"%(old_func_name,var_names[0])
    new_func_cmd="%s=lambda %s"%(new_func_name,var_names[0])
    for var,val in zip(var_names[1:],param_values):
#        print val
#        print var
        
        if not val==None:
            old_func_cmd=old_func_cmd+", %s"%(val)
        else:
            old_func_cmd=old_func_cmd+", %s"%(var)
            new_func_cmd=new_func_cmd+", %s"%(var)

    new_func_cmd=new_func_cmd+": "+old_func_cmd+")"
#    print new_func_cmd
    
    exec(new_func_cmd)#"%(new_func_name,var_names[0],var_names[1],var_names[0],var_names[1],var_names[2]))
    return new_func


class DataSubset():
    """
    this class is defined to hold the information attached to a subset
    such as the indexes defining the subset from the set,the physical parameter
    and the fitting parameter.
    it prevents duplicating the data to each subsets
    """

    def __init__(self, indexes=None, fitparam=None, physparam=None, limparam=None):
        self.bounds = indexes
        if not fitparam == None:
            self.fitparam = fitparam
        else:
            self.fitparam = []
        if not physparam == None:
            self.physparam = physparam
        else:
            self.physparam = []
        if not limparam == None:
            self.limparam = limparam
        else:
            self.limparam = []


def fit_exp_linear(t, y, C=0):
    y = y - C
    y = np.log(y)
    K, A_log = np.polyfit(t - t[0], y, 1)
    A = np.exp(A_log)
    return A, K


def fit_nonlinear(t, y, func_name=exp_decay, guess_param=None,bounds = None):
    #    print "analyse_data.fit_nonlinear: function ",func_name.__name__
    #    opt_parms, parm_cov = sp.optimize.curve_fit(func_name, t, y, maxfev=2000)
    return sp.optimize.curve_fit(func_name, t, y, p0=guess_param, maxfev=2000)


class FittingData():

    def __init__(self):

        self.data_set = []
        self.fname = "this_fname"
        # the original data is stored in the index 0 of the array
        # self.data_subset and have the value self.active_set set to -1
        self.data_subsets = [{'guess': OrderedDict([('m', None), ('h', None)]), 'phys_param': ['Slope'], 'Fit_line_idx': 1, 'limits': [], 'X_line_idx': 0, 'fit_func': 'linear', 'cov': np.array([[ 0.00455464, -0.02049587],
       [-0.02049587,  0.12980716]]), 'fit_func_params': OrderedDict([('m', 1.0848484824657372), ('h', -0.58181816674964493)]), 'mode': 1, 'fix_param': OrderedDict([('m', False), ('h', False)])}, {'guess': OrderedDict([('m', None), ('h', None)]), 'phys_param': ['Slope'], 'Fit_line_idx': 1, 'limits': [], 'X_line_idx': 0, 'fit_func': 'linear', 'cov': np.array([[ 0.00455464, -0.02049587],
       [-0.02049587,  0.12980716]]), 'fit_func_params': OrderedDict([('m', 1.0848484824657372), ('h', -0.58181816674964493)]), 'mode': 1, 'fix_param': OrderedDict([('m', False), ('h', False)])}, {'guess': OrderedDict([('m', None), ('h', None)]), 'phys_param': ['Slope'], 'Fit_line_idx': 1, 'limits': [], 'X_line_idx': 0, 'fit_func': 'linear', 'cov': np.array([[ 0.00455464, -0.02049587],
       [-0.02049587,  0.12980716]]), 'fit_func_params': OrderedDict([('m', 1.0848484824657372), ('h', -0.58181816674964493)]), 'mode': 1, 'fix_param': OrderedDict([('m', False), ('h', False)])}]
        self.active_set = -1

    def create_subset(self, fit_params, phys_param = None):

        if not phys_param == None:
            fit_params["phys_param"]=phys_param
        
              
        
        self.data_subsets.append(fit_params)
#        print(self.data_subsets)
        self.active_set = len(self.data_subsets) - 1
        
    def display(self,idx = 0):
        pass
#        print(self.data_subset[idx])




    def save_subsets(self,of):
        
        if len(self.data_subsets)>0 :        
            of.write("#Data are from file :%s\n"%(self.fname))
            of.write("#Xrow,Yrow,fonction,line_idx,param_name,param_value,physical_param\n")
            for ds in self.data_subsets:
                line = "%s,"*6 +"%s\n"
                line_idx = concatenate_list(ds["limits"][0:2])
#                print(line_idx)
                param_name = concatenate_list(ds["fit_func_params"].keys())
                param_value = concatenate_list(ds["fit_func_params"].values())
                phys_param = concatenate_list(ds["phys_param"])
                of.write(line%(ds["X_line_idx"], ds["Fit_line_idx"], ds["fit_func"],
                      line_idx, param_name, param_value, phys_param))
        else:
            logging.warning("The file %s is not being created because there is no set of fits"%(of.name))

    def load_subsets(self,inf):
        self.data_subsets = []
        for line in inf:
            if "#Data are from file :" in line:
                data_fname = line.split("#Data are from file :")[1]
                #now I need to load the data in self.data_set
            elif not line[0] == "#":
                params = {}
                #eliminate the "\n" at the end of the line
                line = line[:-1]
                line =line.split(',')
                
                params['X_line_idx'] = line[0]
                params['Fit_line_idx'] =line[1]
                params['fit_func'] = line[2]
                params['limits'] = rebuild_list(line[3]) #I should add xmin and xmax
                params['fit_func_params'] = rebuild_dict(line[4],line[5])
                params['phys_params'] = rebuild_list(line[6])
                
                self.data_subsets.append(params)
#                print params
                

        


if __name__=="__main__":

    fname = "test.txt"
    
    

#    print of.name
#    of.
    a = FittingData()
    
#    of = open(fname,"w")
#    a.save_subsets(of)
#    of.close()    
    
    inf = open(fname)
    a.load_subsets(inf)


#    def get_subset(self, param=None, bounds=None):
#
#        if not param == None:
#            if not bounds == None:
#                start = bounds[0]
#                end = bounds[1] - 1
#                answer = np.array(self.data_set[start:end, param])
##                print answer
#            else:
#                answer = np.array(self.data_set[:, param])
#        else:
#            print "analyse_data.get_subset_data : the column of the data to select is not correct : ", param
#
#        return answer

#    def get_active_physparams(self):
#        return self.data_subsets[0].physparam
#
#    def get_active_fit_params(self):
#        return self.data_subsets[0].fitparam
#
#    def get_active_lim_params(self):
#        return self.data_subsets[0].limparam



class live_experiment():

    def __init__(self):

        self.data_set = []
        # the original data is stored in the index 0 of the array
        # self.data_subset and have the value self.active_set set to -1
        self.data_subsets = []
        self.data_subsets.append(DataSubset(None))
        self.active_set = -1
        # this would be use to know when the fit is converging towards a stable
        # value (especially useful for exponentials)
        self.main_fit_param = []
#        print "LIVE_EXPERIMENT"
#    def __del__(self):
#        print "LIVE_EXPERIMENT DEAD"

    def update_data_set(self, data_set=None, fit_func=None, fit_params=None):
        """
        This method recieve the data stream and performs a fit on it based on the bounds given
        fit_params contains the information about which column is x and which one is y as well 
        as the x bounds. fit_params is an array which contains 4 values : x axis index, y axis 
        index, the axis limits, the mode (pan,zoom,selection)
        """
        if not data_set == None:
            self.data_set = data_set
            if not fit_func == None:
                x_bounds = [int(fit_params[2][0]), int(fit_params[2][1])]
                logging.warning(x_bounds)
                self.fit(fit_params[0], fit_params[1], fit_func, x_bounds)
        else:
            print("analyse_data.update_data_set() : there is no data set to change")

    def get_data(self):
        return self.data_set

    def get_subset_data(self, param=None, bounds=None):

        if not param == None:
            if not bounds == None:
                start = bounds[0]
                end = bounds[1] - 1
                answer = np.array(self.data_set[start:end, param])
#                print answer
            else:
                answer = np.array(self.data_set[:, param])
        else:
            print("analyse_data.get_subset_data : the column of the data to select is not correct : ", param)

        return answer

# to make this more robust to change we should inheritate from experiment
# and more specific experiment which will all have their specific way of
# dealing with this function
    def fit(self, paramX, paramY, fit_func, x_bounds=None):

        # Store for display on the widget
#        print "live_exp.fit: ", paramX,paramY,fit_func.func_name,x_bounds

#        print "live_exp.analyse_data.fit:",fit_func.func_name
        if fit_func.func_name == "exp_decay":
            # print "analyse_data.fit : active set :",self.active_set
            X = self.get_subset_data(paramX, x_bounds)
            Y = self.get_subset_data(paramY, x_bounds)
#            print X,Y
            try:
                #                print "in here"
                #                print self.main_fit_param
                #                print self.main_fit_param
                guess_param = [(Y[len(Y) - 1] - Y[0]),
                               np.average(self.main_fit_param[:, 1])]
            except:
                #                print "in there"
                guess_param = [(Y[len(Y) - 1] - Y[0]), (np.max(X) - np.min(X))]
#            print "analyse_data.fit: guess parame ",guess_param
            [deltaY, tau], cov = fit_nonlinear(
                X - X[0], Y - Y[0], fit_func, guess_param)
#            print "analyse_data.fit: variables ",deltaY,tau
#            print "analyse_data.live_exp.fit: covariant ",cov

            Q = Y[0] + deltaY

            try:
                T = np.average(self.get_subset_data('TEMPERATURE'))
            except:
                T = -1
# print "analyse_data.fit:could not get average temperature for set number
# "+str(self.active_set)
            try:
                P = np.average(self.get_subset_data('PRESSURE'))
            except:
                P = -1
# print "analyse_data.fit:could not get average pressure for set number
# "+str(self.active_set)

            # Store for display and save later
            self.data_subsets[0].fitparam = [
                deltaY, tau, Y[0], X[0], cov[0, 0]]
            self.data_subsets[0].physparam = [
                str(round(Q, 12)), str(round(P, 3)), str(round(T, 2))]
            self.add_main_fit(np.array([Q, tau]))

        elif fit_func.func_name == "integrate":
            pass

        elif fit_func.func_name == "linear":
            X = self.get_subset_data(paramX)
            Y = self.get_subset_data(paramY)
            [m, h], cov = fit_nonlinear(X, Y, fit_func)
#            print "analyse_data.fit: variables ",m,h
#            print "analyse_data.fit: covariant ",cov

            # Store for display and save later
            self.data_subsets[0].fitparam = [m, h, cov[0, 0]]
            self.data_subsets[0].physparam = [m]

        # Store for display and save later
        self.data_subsets[0].limparam = [x_bounds, X[0], X[-1]]

    def add_main_fit(self, main_fit):
        if self.main_fit_param == []:
            self.main_fit_param = main_fit
        self.main_fit_param = np.vstack((self.main_fit_param, main_fit))
        try:
            residual = (abs(
                self.main_fit_param[-1, 0] - self.main_fit_param[-2, 0])) / self.main_fit_param[-1, 0]
#            if residual<0.1:
#                print "NOW the residual is low",residual
        except:
            pass

    def get_active_physparams(self):
        return self.data_subsets[0].physparam
#

    def get_active_fit_params(self):
        return self.data_subsets[0].fitparam

    def get_active_lim_params(self):
        return self.data_subsets[0].limparam


class experiment():
    """
        this class handles the fitting procedures needed for post processing 
        analysis. It is not yet very modular...
    """

    def __init__(self, fname=None, data=None, bkg=None):

        #        self.bkg_val={}
        #        self.has_bkg=False
        if not data == None:
            self.data_set = data
#            self.data_set_bounds=[0,self.data_set.length]
            self.params = data.params
        elif not fname == None:
            self.load_data_set(fname)
        else:
            self.data_set = None
#            self.data_set_bounds=None
            self.params = None

        # the original data is stored in the index 0 of the array
        # self.data_subset and have the value self.active_set set to -1
        self.data_subsets = []
        self.active_set = -1

#        if not bkg:
#            if self.params:
#                for p in self.params:
#                    self.bkg_val[p]=0
#        else:
#            self.bkg_val=bkg
#            self.has_bkg=True
#        print "This is the BKG values of parameters",self.bkg_val
#        print "EXPERIMENT"
#    def __del__(self):
#        print "EXPERIMENT DEAD"

    def load_data_set(self, fname): #(only in this one)
        if not fname == None:
            extension = fname.rsplit('.')[len(fname.rsplit('.')) - 1]
            if extension == "adat":
                [data, labels] = io.load_file_windows(fname, '\t')
            elif extension == "adat2":
                [data, labels] = io.load_file_windows(fname)
            elif extension == "a5dat":
                data, param = load_experiment(fname)
                data = np.transpose(np.array(data))
                labels = {}
                labels["param"] = ["Vc", "T", "P"]
            else:
                [data, labels] = io.load_file_windows(fname)
    #        print "load data set "+fname
            new_data_set = DataSet(data, labels)
            self.change_data_set(new_data_set)

    def load_data_subsets(self, fname):
        extension = fname.rsplit('.')[len(fname.rsplit('.')) - 1]
        if extension == "aset":
            [data, labels] = io.load_aset_file(fname)
        else:
            print("analyse_data.load_data_subsets: wrong extensionfor the file ", fname, ", should be '.aset' but it is '", extension, "'")
#        print "load data set "+fname
        new_data_set = data_set(data, labels)
        self.change_data_set(new_data_set)

    def change_data_set(self, data=None):
        #        print "analyse_data.change_data_set :",data.params
        if data:
            self.data_set = data
#            self.data_set_bounds=[0,self.data_set.length]
            self.params = data.params
#            for p in self.params:
#                    self.bkg_val[p]=0
            self.data_subsets = []
            self.active_set = -1
        else:
            print("analyse_data.change_data_set() : there is no data set to change")

    def update_data_set(self, data_set=None):

        if not data_set == None:
            #            print "update data in experiment"
            self.data_set = data_set
#            self.data_set_bounds=[0,self.data_set.length]
        else:
            print("analyse_data.update_data_set() : there is no data set to change")

    def change_data_subsets(self, subsets=[]):
        self.data_subsets = subsets
        self.active_set = -1

    def create_subset(self, start=None, end=None, param=None):
        #        print "analyse_data.create_subset\n"
        if param == None:
            print("analyse_data.create_subset: you want to create a subset knowing the indexes")
            print("if not, you should specifiy a parameter in the list")
            print(self.params)
#        else:
#            start=self.match_value2index(start,param)
#            end=self.match_value2index(end,param)
#        print "analyse_data.create_subset : start, end",start,", ",end
        self.data_subsets.append(DataSubset([start, end]))
        self.active_set = len(self.data_subsets) - 1
#        return [start,end]

    def remove_subset(self):
        if self.active_set == -1:
            pass
        else:
            self.data_subsets.remove(self.get_active_subset())
            self.active_set = self.active_set - 1

    def get_data(self):
        return self.data_set.get_data()

    def get_subset_data(self, param=None):
        if self.active_set == -1:
            return self.data_set.get_data(param)
        else:
            [start, end] = self.data_subsets[self.active_set].bounds
#            print "analyse_data.Experiment.get_subset_data", start,end
            return self.data_set.subset(start, end, param)

    def get_active_subset(self):
        if self.active_set == -1:
            return None
        else:
            return self.data_subsets[self.active_set]

    def previous_data_set(self):
        if self.active_set == -1:
            self.active_set = len(self.data_subsets) - 1
        else:
            self.active_set = self.active_set - 1

    def next_data_set(self):
        if self.active_set == len(self.data_subsets) - 1:
            self.active_set = -1
        else:
            self.active_set = self.active_set + 1

# to make this more robust to change we should inheritate from experiment
# and more specific experiment which will all have their specific way of
# dealing with this function
    def fit(self, paramX, paramY, fit_func, x_bounds=None):

#        print "fit: ", paramX, paramY, fit_func.func_name, x_bounds

        if self.active_set == -1:
            print("analyse_data.fit: you cannot fit when you are in the raw data")
        else:
#            print "analyse_data.fit:", fit_func.func_name
            if fit_func.func_name == "exp_decay":
                # print "analyse_data.fit : active set :",self.active_set
                X = self.get_subset_data(paramX)
                Y = self.get_subset_data(paramY)
                guess_param = [(Y[len(Y) - 1] - Y[0]), (np.max(X) - np.min(X))]
#                print "analyse_data.fit: guess parame ",guess_param
                [deltaY, tau], cov = fit_nonlinear(
                    X - X[0], Y - Y[0], fit_func, guess_param)
#                print "analyse_data.fit: variables ", deltaY, tau
#                print "analyse_data.fit: covariant ", cov
                self.data_subsets[self.active_set].fitparam = [
                    deltaY, tau, Y[0], X[0], cov[0, 0]]
                Yfit = Y[0] + deltaY

                try:
                    T = np.average(self.get_subset_data('D(T)'))
                    dT = np.std(self.get_subset_data('D(T)'))
                except:
                    T = np.average(self.get_subset_data('D'))
                    dT = np.std(self.get_subset_data('D'))

                try:
                    Tr = np.average(self.get_subset_data('TEMPERATURE'))
                    dTr = np.std(self.get_subset_data('TEMPERATURE'))
                except:
                    Tr = -1
                    dTr = 0
# print "analyse_data.fit:could not get average temperature for set number
# "+str(self.active_set)
                try:
                    #                    if correct_bkg:
                    #                        P=np.average(self.get_subset_data('PRESSURE'))-self.bkg_val['PRESSURE']
                    #                    else:
                    P = np.average(self.get_subset_data('PRESSURE'))
                    dP = np.std(self.get_subset_data('PRESSURE'))
                except:
                    P = -1
                    dP = 0
#                    print "analyse_data.fit:could not get average pressure for set number " + str(self.active_set)

                Q = Yfit
                dQ = np.sqrt(cov[0, 0])
                self.data_subsets[self.active_set].physparam = [str(round(Q, 13)), str(round(P, 4)), str(round(Tr, 3)), str(
                    round(T, 5)), str(round(dQ, 13)), str(round(dP, 4)), str(round(dTr, 3)), str(round(dT, 5))]

            elif fit_func.func_name == "exp_decay2":
                #                print paramX,x_bounds
                # print "analyse_data.fit : active set :",self.active_set
                X = self.get_subset_data(paramX)
                Y = self.get_subset_data(paramY)
    #            print X,Y
                try:
                    guess_param = self.data_subsets[
                        self.active_set - 1].fitparam
                    guess_param = [(Y[len(Y) - 1] - Y[0]), guess_param[1]]
#                    print guess_param
                except:
                    guess_param = [(Y[len(Y) - 1] - Y[0]),
                                   (np.max(X) - np.min(X))]
    #            print "analyse_data.fit: guess parame ",guess_param
                [deltaY, tau], cov = fit_nonlinear(
                    X - X[0], Y - Y[0], fit_func, guess_param)
#                print "analyse_data.fit: variables ", deltaY, tau
#                print "analyse_data.fit: covariant ", cov
                self.data_subsets[self.active_set].fitparam = [
                    deltaY, tau, Y[0], X[0], cov[0, 0]]
                Yfit = Y[0] + deltaY

                try:
                    T = np.average(self.get_subset_data('D(T)'))
                    dT = np.std(self.get_subset_data('D(T)'))
                except:
                    T = np.average(self.get_subset_data('D'))
                    dT = np.std(self.get_subset_data('D'))

                try:
                    Tr = np.average(self.get_subset_data('TEMPERATURE'))
                    dTr = np.std(self.get_subset_data('TEMPERATURE'))
                except:
                    Tr = -1
                    dTr = 0
# print "analyse_data.fit:could not get average temperature for set number
# "+str(self.active_set)
                try:
                    #                    if correct_bkg:
                    #                        P=np.average(self.get_subset_data('PRESSURE'))-self.bkg_val['PRESSURE']
                    #                    else:
                    P = np.average(self.get_subset_data('PRESSURE'))
                    dP = np.std(self.get_subset_data('PRESSURE'))
                except:
                    P = -1
                    dP = 0
#                    print "analyse_data.fit:could not get average pressure for set number " + str(self.active_set)

                Q = Yfit
                dQ = np.sqrt(cov[0, 0])
                self.data_subsets[self.active_set].physparam = [str(round(Q, 13)), str(round(P, 4)), str(round(Tr, 3)), str(
                    round(T, 5)), str(round(dQ, 13)), str(round(dP, 4)), str(round(dTr, 3)), str(round(dT, 5))]

            elif fit_func.func_name == "integrate":
                pass
            elif fit_func.func_name == "linear":
                X = self.get_subset_data(paramX)
                Y = self.get_subset_data(paramY)
                [m, h], cov = fit_nonlinear(X, Y, fit_func)
#                print "analyse_data.fit: variables ", m, h
#                print "analyse_data.fit: covariant ", cov
                self.data_subsets[self.active_set].fitparam = [m, h, cov[0, 0]]
                self.data_subsets[self.active_set].physparam = [m]
            elif fit_func.func_name == "vcrit":
                X = self.get_subset_data(paramX)
                Y = self.get_subset_data(paramY)
                X = X[Y > 0]
                Y = Y[Y > 0]
                guess_param = [Y[-1], 0.66]
                P = self.get_subset_data("P")
                T_l = T_lambda(np.average(P))

                def vcrit(T, vc0, nu):
                    Tc = T_l
                    return vc0 * np.power((1 - T / Tc), nu)
                [vc0, nu], cov = fit_nonlinear(X, Y, vcrit, guess_param)
#                print "analyse_data.fit: variables ", vc0, nu
#                print "analyse_data.fit: covariant ", cov
                self.data_subsets[self.active_set].fitparam = [
                    vc0, nu, cov[0, 0]]
                self.data_subsets[self.active_set].physparam = [vc0, nu]
            else:
#                print "*" * 20
#                print "You need to define a procedure in analyse_data.py for the function %s" % (fit_func.func_name)
#                print "*" * 20
                self.data_subsets[self.active_set].limparam = [
                self.data_subsets[self.active_set].bounds, X[0], X[-1]]

    def get_active_physparams(self):
        if self.active_set == -1:
            return []
        else:
            return self.data_subsets[self.active_set].physparam
#

    def get_active_fit_params(self):
        if self.active_set == -1:
            return []
        else:
            return self.data_subsets[self.active_set].fitparam

    def get_active_lim_params(self):
        if self.active_set == -1:
            return []
        else:
            return self.data_subsets[self.active_set].limparam
#    def correct_bkg(self,param=None,val=0):
#        self.has_bkg=True
#        if not param:
#            print "you should specifiy a parameter in the list"
#            print self.params
#        else:
#            if param in self.params:
#                self.bkg_val[param]=val
#            else:
#                print "you should specifiy a parameter in the list"
#                print self.params

    def savefile(self, of, physp):
#        print "saving"
#
#        physp=self.params
        of.write("#P ")
        for p in physp:
            of.write(p + "\t")
        of.write("and respective uncertaines")
        of.write("\n")
        for s in self.data_subsets:
            try:
                for p in s.physparam:
                    of.write(str(p) + "\t")
                of.write("\n")
#                if save_subsets:
#                    of.write(str(s.bounds).strip('[]')+"\n")
            except:
                print("analyse_data.experiment.savefile : could not save the file")

    def saveset(self, of):
#        print "saving sets"
  # here I should define the different parameters and the fit parameters

        for i, s in enumerate(self.data_subsets):
            try:
                for p in s.limparam:
                    of.write(str(p) + "\t")
                of.write(":")
                for p in s.physparam:
                    of.write(str(p) + "\t")
                of.write(":")
#                print s.fitparam
                for p in s.fitparam:
                    of.write(str(p) + "\t")
                of.write("\n")

            except:
                print("analyse_data.experiment.saveset : could not save the set")

def test_fit_exponential():
    import random
    def dummy_exp(Yfinal = 2,tau = 15,t_off = 10):
        answer = np.array([])
        dt = np.array([])
        idx = 0
        for t in range(t_off):
            answer = np.append(answer,0.05 *(random.random() - 0.5))
            dt = np.append(dt,idx)
            idx += 1
        for t in range(3*tau):
            answer = np.append(answer,exp_decay(idx-t_off, Yfinal, tau, 0) * (1 + 0.05 *(random.random() - 0.5)))
            dt = np.append(dt,idx)
            idx += 1
            
        return dt,answer
        
    t,y = dummy_exp()

    data = np.loadtxt("C:\\Users\\pfduc\\Documents\\g2gui\\g2python\\161011_TEST_sample_name_010.dat")    
    t = data[:,2]
    y=data[:,1]
    
    idx_b = 14
    idx_s = 60

    fitp_val,cov = fit_nonlinear(t[idx_b:idx_s],y[idx_b:idx_s],exp_decay,guess_param = [y[idx_b],t[idx_s]-t[idx_b],t[idx_s]])
    print fitp_val
    plt.plot(t,y,'b',t[idx_b:idx_s],y[idx_b:idx_s],'or',exp_decay(t,*fitp_val),'--k')
    plt.show()
    
def test_fit_exponential_down():
    import random
    def dummy_exp(dY = 2,tau = 15,Y_inf = 1,t_off = 10):
        answer = np.array([])
        dt = np.array([])
        idx = 0
        for t in range(t_off):
            answer = np.append(answer,(dY+Y_inf)*(1 + 0.05 *(random.random() - 0.5)))
            dt = np.append(dt,idx)
            idx += 1
        for t in range(3*tau):
            answer = np.append(answer,exp_decay_down(idx-t_off,Y_inf,dY, tau, 0)*(1 + 0.05 *(random.random() - 0.5)))
            dt = np.append(dt,idx)
            idx += 1
            
        return dt,answer
        
    t,y = dummy_exp()
    idx_b = 13

    fitp_val,cov = fit_nonlinear(t[idx_b:],y[idx_b:],exp_decay_down)
    print fitp_val
    plt.plot(t,y,'b',t[idx_b:],y[idx_b:],'or',exp_decay_down (t,*fitp_val),'--k')
    plt.show()
   
    
if __name__ == "__main__":
    test_fit_exponential()
#    test_fit_exponential_down()
#    def fit_nonlinear(t, y, func_name=exp_decay, guess_param=None):
   