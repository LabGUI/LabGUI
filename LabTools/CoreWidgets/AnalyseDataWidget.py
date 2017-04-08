# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 11:11:45 2013

@author: pf
"""
#import matplotlib.pyplot as plt
import PyQt4.QtCore as QtCore
from PyQt4.QtCore import Qt
import PyQt4.QtGui as QtGui
#from PyQt4.QtGui import *
import sys
#from He4Properties import T_lambda
import logging
logging.basicConfig(level=logging.DEBUG)

from LabTools.Display.mplZoomWidget import ZOOM_MODE, PAN_MODE, SELECT_MODE

from collections import OrderedDict
from LabTools.Fitting import analyse_data as ad
#import matplotlib.pyplot as plt

import numpy as np
from LabTools.IO import IOTool as io

import logging.config
import os
#ABS_PATH=os.path.abspath("C:\Users\pfduc\Documents\g2gui\g2python")
#logging.config.fileConfig(os.path.join(ABS_PATH,"logging.conf"))

FONCTIONS_MODULE = "Functions"
FONCTIONS_PKG = "LabTools.Fitting"
VOID_NPARRAY = np.array([])
VOID_ARRAY = []

def clear_layout(layout):
    """
    This function loop over a layout objects and delete them properly
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        layout.removeWidget(widget)
        try:
            widget.setParent(None)
        except:
            pass
        if not widget == None:
            widget.close()

def toggle_layout(layout,state):
    """
    This function loop over a layout objects enable/disable their state
    """
    widgets = (layout.itemAt(i).widget() for i in range(layout.count())) 
    for w in widgets:
        if not w == None:
            w.setEnabled(state)



def fill_layout_textbox(layout, text,debug = False,alist = None):
    """
    This function loop over a layout objects set the texts for QLineEdit only
    """
    index = 0
    #loof through the widgets of a Layout
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        #check that the widget is a QLineEdit instance
        if isinstance(widget,QtGui.QLineEdit):
            
            #if a list of widget is provided, then check that the widget is in this list
            if alist !=None:
               
               if widget in alist:
                   widget.setText(str(text[index]))
                   index = index + 1

            else:
                widget.setText(str(text[index]))
                index = index + 1
                
            #if needbe to debug
            if debug:
                pass
            
#            except IndexError:
#                logging.info("The parameter %s had no value to update"%(widget.objectName()[3:]))

def isnparray(an_array):
    if not isinstance(an_array, np.ndarray):
        msg = "The argument passed as a numpy array is of type '%s'"%(
        type(an_array).__name__)
        return TypeError(msg)
    else:
        return True


class FittingWidget(QtGui.QWidget):

    data_array = None
    fit_func = None
    
    #A dictionnary containing the function name, the limits, the parameters of the function (and their values), the covariance of the fit etc...
    fit_params = {}
    fit_func_variables = []
        
    physparam_list = [] 
    
    fit_data = ad.FittingData()
    
    # contains the x axis index, y axis index, the axis limits, the mode
    # (pan,zoom,selection)
    fit_selection_parameters = {"X_line_idx":0, "Fit_line_idx":1,"limits":[], "mode":1}

    fonctions_module = None
    
    fonctions_pkg = None
    
    state = True
    
    data_type = "Live"
    
    live_widgets = []
    past_widgets = []

    def __init__(self, parent=None, fonctions_module = FONCTIONS_MODULE, fonctions_pkg = FONCTIONS_PKG):
        super(FittingWidget, self).__init__(parent)
        
       
        
        if not parent == None:
            
            #this will be triggered whenever the user changes the plot limits 
            #or whenever the software changes increases the dataset
            self.connect(parent, QtCore.SIGNAL(
                "selections_limits(PyQt_PyObject,int,int,int,int)"), self.update_selection_limits)
                
            #this will call update_experiment whenever the dataset is updated
            self.connect(parent, QtCore.SIGNAL(
                "data_array_updated(PyQt_PyObject)"), self.update_data_and_fit)
            self.connect(parent, QtCore.SIGNAL(
                "instrument_hub_connected(PyQt_PyObject)"), self.update_instruments_information)
     
            self.connect(parent, QtCore.SIGNAL("removed_selection_box()"), self.selection_removed) 
     
            self.connect(parent, QtCore.SIGNAL("plotwindowtype_changed(PyQt_PyObject)"),self.data_type_changed)     
     
        #loads the lists of functions from a module
        self.fonctions_pkg = fonctions_pkg     
     
        if parent == None:
            self.fonctions_module = fonctions_module
         
            self.fit_funcs_names = io.list_module_func(self.fonctions_module)
        else:
            self.fonctions_module = ".%s"%(fonctions_module)
            self.fit_funcs_names = io.list_module_func(
                self.fonctions_module, package=self.fonctions_pkg)    
    

        # main layout of the form is the verticallayout
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        """
        here will be displayed the button to create subsets and choose between livefit or postfit, also the number of the subset is displayed
        """
        self.commandLayout = QtGui.QHBoxLayout()

        self.fitCombo = QtGui.QComboBox(self)
        self.fitCombo.setObjectName("fit_comboBox")
        self.fitCombo.addItems(self.fit_funcs_names)      
        self.save_fitButton = QtGui.QPushButton(self)
        self.save_fitButton.setText("Save single fit")
        self.save_setButton = QtGui.QPushButton(self)
        self.save_setButton.setText("Save set fit")      
        self.live_fitButton = QtGui.QPushButton(self)
        self.live_fitButton.setText("Enable Fit")  
        
    
        #initializes the fonction list in the ComboBox for the first time
        if parent == None:
            self.fit_func = io.import_module_func(
                self.fonctions_module, str(self.fitCombo.currentText()))
        else:
            self.fit_func = io.import_module_func(self.fonctions_module, str(
                self.fitCombo.currentText()), package=self.fonctions_pkg)
        
        #assigns the name of the fit fonction (python2 and python3)
        try:
            self.fit_params["fit_func"] = self.fit_func.func_name
        except:
            self.fit_params["fit_func"] = self.fit_func.__name__

      
        
        self.commandLayout.addWidget(self.fitCombo)
        self.commandLayout.addWidget(self.save_fitButton)
        self.commandLayout.addWidget(self.save_setButton)
        self.commandLayout.addWidget(self.live_fitButton)
        self.verticalLayout.addLayout(self.commandLayout)

        """
        here will be displayed the x-axis boundaries over which the plot is made
        """
        self.create_selection_layout()

        #if the user defined extra physical parameters needed once the fit
        #is performed, they will be defined in the dict PHYS_PARAMS
        if self.fit_params["fit_func"] in ad.PHYS_PARAMS:
            self.physparam_list = ad.PHYS_PARAMS[self.fit_params["fit_func"]]
        else:
             self.physparam_list = []
            
        self.create_fit_layout()
        self.create_phys_layout()
        
        self.setLayout(self.verticalLayout)

        self.connect(self.fitCombo, QtCore.SIGNAL(
            "currentIndexChanged(int)"), self.fit_func_changed)
        
        self.connect(self.live_fitButton, QtCore.SIGNAL(
            'clicked()'), self.on_live_fitButton_clicked)    
            
        #this helps to toggle all the button according to the state False
        #it starts in True)
        self.on_live_fitButton_clicked()
            
        self.connect(self.save_fitButton, QtCore.SIGNAL(
            'clicked()'), self.on_save_fitButton_clicked)
            
        self.connect(self.save_setButton, QtCore.SIGNAL(
            'clicked()'), self.on_save_setButton_clicked)

    def update_instruments_information(self, information):
        self.parameters = information
#        print self.parameters

    def fit_func_changed(self):
        """
        when a new fit fonction is choosen, the fit parameters are 
        automatically adjusted
        """
        
        new_func_name =  str(self.fitCombo.currentText())        
        
        self.fit_func = io.import_module_func(
            self.fonctions_module,new_func_name,package = self.fonctions_pkg)

        self.fit_params["fit_func"] = new_func_name

        #if the user defined extra physical parameters needed once the fit
        #is performed, they will be defined in the dict PHYS_PARAMS
        if new_func_name in ad.PHYS_PARAMS:
            self.physparam_list = ad.PHYS_PARAMS[new_func_name]
        else:
             self.physparam_list = []

        #update the layout according to the parameters
        self.remove_phys_layout()
        self.remove_fit_layout()
        
        self.create_fit_layout()
        self.create_phys_layout()


    def data_type_changed(self,data_type = None):
        """
        recieve a string that identifies the type of data which is being
        displayed on the current widget, it could be live data or past data.
        the way the GUI looks when past or live data is selected will be 
        different
        """
        
        logging.debug(data_type)
        if data_type == None:
            if self.data_type == "Live":
                self.data_type = "Past"
            elif self.data_type == "Past":
                self.data_type = "Live"
        else:
            if self.data_type in ['Live','Past']:
                self.data_type = data_type
            else:
                logging.error("The data type passed in argument is not of the right format")

        self.toggle_selection_layout(self.data_type)
#        self.create_selection_layout(self.data_type)

    def selection_removed(self):
        """
        this function is triggered by a signal
        it allows the change of limits when zooming in and out
        """
        print("prout pan mode")
        self.fit_selection_parameters["mode"] = PAN_MODE
        

    def update_selection_limits(self, limits, paramX, paramY, paramYfit, mode):
        """
        function changing the xaxis limits of the fit and which y axis variable is choosen to fit the function.
        this function is mainly called upon the signal "selections_limits(PyQt_PyObject,int,int,int,int)" usually emitted by emit_axis_lim
        in LabGui.
        """

        # update the fit selection parameters, we actually don't care about the
        # paramY, only the fit axis
        self.fit_selection_parameters["X_line_idx"] = paramX
        self.fit_selection_parameters["Fit_line_idx"] = paramYfit
        
        #this lock the change of the mode as long as the selection recangle
        #exists on the plot, when it is removed a signal will trigger the
        #change of the mode (see selection_removed method)
        if self.fit_selection_parameters["mode"] == SELECT_MODE:
            if mode == SELECT_MODE:
                self.fit_selection_parameters["limits"] = limits
        else:
            self.fit_selection_parameters["mode"] = mode
            self.fit_selection_parameters["limits"] = limits
        
        limits = self.fit_selection_parameters["limits"]
        # change the x axis limit information
        fill_layout_textbox(self.selectionLayout, ["%i" % (limits[0]), "%i" % (
            limits[1]), "%.2f" % (limits[2]), "%.2f" % (limits[3])],alist = self.live_widgets)
            
        logging.debug(self.fit_selection_parameters)

    def get_data_to_fit(self, whole = False):
        """
        if the dataset is bounded it returns only a bounded dataset
        if whole is set to True it returns the whole dataset
        the x-axis and y-axis are predetermined by the values in
        the dict self.fit_selection_parameters
        """

        #if the array is empty we return None,None
        if np.size(self.data_array)>0:
            #this contains the limits, the first two values are the indexes
            xlims = self.fit_selection_parameters["limits"]
            #this is a number between 0 and the number of row in the data set
            paramX = self.fit_selection_parameters["X_line_idx"]
            #this is a number between 0 and the number of row in the data set
            paramY = self.fit_selection_parameters["Fit_line_idx"]
            
            
            if not xlims == [] and whole ==False:
                
                start = int(xlims[0])
                end = int(xlims[1])
                
                if start == 0 and end == 1:
                    
                    X = self.data_array[:,paramX]
                    Y = self.data_array[:,paramY]
                    
                else:
                    
                    X = self.data_array[start:end,paramX]
                    Y = self.data_array[start:end,paramY]
                    
            else:
                
                X = self.data_array[:,paramX]
                Y = self.data_array[:,paramY]
                
            return np.squeeze(X),np.squeeze(Y)
            
        else:
            
            return VOID_NPARRAY,VOID_NPARRAY

    def on_live_fitButton_clicked(self):
        """toggle the state between enabled od disabled"""
        
        if self.state:
            self.live_fitButton.setText("Enable Fit")
            self.state = not self.state 
        else:
            self.live_fitButton.setText("Disable Fit")
            self.state = not self.state 

        #enable/disable the widget in the layout
        toggle_layout(self.fitLayout,self.state)
        toggle_layout(self.fit_paramLayout,self.state)
        toggle_layout(self.fit_param_labelLayout,self.state)
        
        toggle_layout(self.physLayout,self.state)
        toggle_layout(self.phys_paramLayout,self.state)
        toggle_layout(self.phys_param_labelLayout,self.state)

        toggle_layout(self.selectionLayout,self.state)
        
        self.indexValue.setEnabled(self.state)
        self.save_fitButton.setEnabled(self.state)
        self.save_setButton.setEnabled(self.state)
                

    def on_save_fitButton_clicked(self):

       self.update_data_and_fit()
       
       self.fit_data.create_subset(self.fit_params,self.physparam_list)
        
        
    def on_save_setButton_clicked(self):
        self.data_type_changed()
#        if not self.fname:
#            fname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save output file as',
#                                                          './' + self.fname + '.aset'))
#        else:
#            fname = self.fname + '.aset'
#
##        fname = str(QFileDialog.getOpenFileName(self, 'Load load from', './'))
#        print(fname)
##        if fname:
##            of = open(fname, 'a')
##            self.experiment.saveset(of)
##            of.close()

    def checkbox_handler(self):
        """
        it fixes the value of the QLineEdit object with the same parameter
        so for the fits
        """
        #get the sender identity
        sdr = self.sender()
        
        #get the sender status (Checked(True) or not Checked(False))
        is_checked = sdr.isChecked()  
        
        #get the sender name
        id_label = str(sdr.objectName())
        
        #the first 3 characters are identifiers for QLineEdit or QCheckBox
        #the rest is the name of the fit parameter
        id_label = id_label[3:]
            
        #change the status of the fit parameter in the fixed parameters
        self.fit_params["fix_param"][id_label]=is_checked
        
        #call the method that will update the fit fonction
        self.manage_fix_value_fit_params()

    
    def lineedit_handler(self):
        """
        this is called whenever a QLineEdit of the fit Layout is edited
        it checks that the value is a number
        """
         #get the sender identity
        sdr = self.sender()
        
        #get the sender status (Checked(True) or not Checked(False))
        id_label = str(sdr.objectName())
        
        #the first 3 characters are identifiers for QLineEdit or QCheckBox
        #the rest is the name of the fit parameter
        id_label = id_label[3:]
        
        #We expect that the value is a number
        try:
            fit_param = float(str(sdr.text()))
        except ValueError:
            fit_param = np.nan
            sdr.setText(str(fit_param))
        
        #call the method that will update the fit fonction
        self.manage_fix_value_fit_params()
        
        

    def manage_fix_value_fit_params(self):
        """
        this methods goes through the list of parameters and see whether
        they are fixed or not, then generate a fonction with only the 
        non fixed parameters that can be varied by the fitting procedure
        """
        at_least_one_param_fixed = False
        
        #prepare the list of argument of ad.restrict_function_parameters
        fit_func_var = []
        for fp in self.fit_params["fix_param"]:
            
            #if the fit param is set to fixed == True
            if self.fit_params["fix_param"][fp]:
                
                at_least_one_param_fixed = True
                
                #retrieve the value of the text_box with that parameter name
                fitp_fixed_value = self.get_lineedit_value(fp)
                
                #modify the value list to create a fonction with this
                #parameter fixed
                fit_func_var.append(fitp_fixed_value)
                
                #assigns the value to the fixed fit param
                self.fit_params["fit_func_params"][fp] = fitp_fixed_value
                
            else:
                
                #prepare the value list to create a fonction with this
                #parameter value to be varied to find the best fit
                fit_func_var.append(None)
 
        original_func = io.import_module_func(
            self.fonctions_module, str(self.fit_params["fit_func"]),
            package = self.fonctions_pkg) 
            
        if at_least_one_param_fixed :
            #modifing the fit function by fixing some of its variables
            self.fit_func = ad.restrict_function_parameters(original_func, 
                                                            fit_func_var)
            
        else:
            
            self.fit_func = original_func       
                

    def update_data_and_fit(self, data = None):
        """
        change the dataset over which the fit is performed and reperform the 
        fit, actualize the fit curve and send it through a signal
        """

        if not data == None:
            if not isnparray(data) == True:
                raise isnparray(data) 
                
#            print "replacing", np.shape(self.data_array), "by", np.shape(data)
            self.data_array = data        
        
        #go into the fitting process only if the state is True
        if self.state:        
    
            #get the data over which to fit the fonction
            X,Y = self.get_data_to_fit()   
            
            if not ( X == VOID_NPARRAY and Y == VOID_NPARRAY):
                
                if self.fit_params["fit_func"] == "exp_raise":
                    #rough estimate of the parameters
                    #Y_inf     Y[-1]
                    #tau       X[-1]-X[0]
                    #t_offset  X[0]
                    guess_param = [Y[-1],X[-1]-X[0],X[0]]
                    
                elif self.fit_params["fit_func"] == "exp_decay":
                    #rough estimate of the parameters
                    #Y_inf     -Y[-1] (needs to be negative)
                    #dY        Y[0]-Y[-1] 
                    #tau       X[-1]-X[0]
                    #t_offset  X[0]
                    # Y_inf ,dY ,tau ,t_offset
                    guess_param = [Y[-1],Y[0]-Y[-1],X[-1]-X[0],X[0]]
                    
                else:
                    guess_param = None
                
                #performs the fit
                fitp_val, cov = ad.fit_nonlinear(X, Y, self.fit_func,guess_param)
                    
                logging.debug("analyse_data.fit: fitter params ")
                logging.debug(fitp_val)
                logging.debug("analyse_data.fit: covariance ")
                logging.debug(cov)
        
                #stores the parameters value in an ordered dict
                fitp = OrderedDict()
                index = 0
                
                for fp in self.fit_func_variables:
                    
                    #if the fit param is set to fixed == True
                    if self.fit_params["fix_param"][fp]:
                        #we copy the value stored
                        fitp[fp] = self.fit_params["fit_func_params"][fp]
                    else:
                        #otherwise we use the freshly fitted parameter
                        fitp[fp]=fitp_val[index]
                        index = index + 1
                    
                # Store for display and save later
                self.fit_params.update(self.fit_selection_parameters)
                self.fit_params["fit_func_params"] = fitp
                self.fit_params["cov"] = cov                
        
                #write the values of the fitting parameters in the boxes
                fill_layout_textbox(self.fit_paramLayout, list(fitp.values()))            
                
                #prepare the parameters needed to plot the fit
                passover_fitp = {}
                passover_fitp["limits"] = self.fit_params["limits"]
                passover_fitp["fit_func"] = self.fit_func
                passover_fitp["fitp_val"] = fitp_val

                self.emit(QtCore.SIGNAL("update_fit(PyQt_PyObject)"),
                          passover_fitp)


    def get_lineedit_value(self,id_label):
        """this will return the value of a QLineEdit in fitLayout"""
        widget = self.findChildren(QtGui.QLineEdit,"le_%s"%(id_label))
        if np.size(widget) == 1:
            try:
                answer = float(str(widget[0].text()))
            except ValueError:
                answer = np.nan
        else:
            msg = "There is more than one LineEdit named %s for the fonction %s"%(id_label,self.fit_func.func_name)
            raise(ValueError,msg)
        return answer
        
    def get_checkbox_state(self,id_label):
        """this will return the state of a QCheckBox in fitLayout"""
        widget = self.findChildren(QtGui.QCheckbox,"ch_%s"%(id_label))
        if np.size(widget) == 1:
            answer = widget[0].isChecked()
        else:
            msg = "There is more than one checkbox named %s for the fonction %s"%(id_label,self.fit_func.func_name)
            raise(ValueError,msg)
        return answer
          
    def create_selection_layout(self, data_type = "Live"):
        
        self.selectionLayout = QtGui.QHBoxLayout()
        self.selectionLayout.setObjectName("selectionLayout")
        
        alabel = QtGui.QLabel(self)
        alabel.setText("Index of the fit :")
        self.past_widgets.append(alabel)        
        self.selectionLayout.addWidget(alabel)
        
        self.indexValue = QtGui.QLineEdit(self)
        self.past_widgets.append(self.indexValue)
        self.selectionLayout.addWidget(self.indexValue)    
        
        self.previousButton = QtGui.QPushButton(self)
        self.previousButton.setText("<==")
        self.selectionLayout.addWidget(self.previousButton)
        self.past_widgets.append(self.previousButton)        
        
        self.nextButton = QtGui.QPushButton(self)
        self.nextButton.setText("==>")
        self.selectionLayout.addWidget(self.nextButton)
        self.past_widgets.append(self.nextButton)
        

        
#        alabel = QtGui.QLabel(self)
#        self.live_widgets.append(alabel)
        
        self.XminIndex = QtGui.QLineEdit(self)
        self.live_widgets.append(self.XminIndex)
        self.XmaxIndex = QtGui.QLineEdit(self)
        self.Xmin = QtGui.QLineEdit(self)
        self.Xmax = QtGui.QLineEdit(self)
        alabel = QtGui.QLabel(self)
        alabel.setText("Imin :")
        self.live_widgets.append(alabel)
                
        self.selectionLayout.addWidget(alabel)
        self.selectionLayout.addWidget(self.XminIndex)
        alabel = QtGui.QLabel(self)
        alabel.setText("Imax :")
        self.live_widgets.append(alabel)
        
        self.live_widgets.append(self.XmaxIndex)
        self.selectionLayout.addWidget(alabel)
        self.selectionLayout.addWidget(self.XmaxIndex)
        alabel = QtGui.QLabel(self)
        alabel.setText("Xmin :")
        self.live_widgets.append(alabel)
        self.live_widgets.append(self.Xmin)        
        
        self.selectionLayout.addWidget(alabel)
        self.selectionLayout.addWidget(self.Xmin)
        alabel = QtGui.QLabel(self)
        alabel.setText("Xmax :")
        self.live_widgets.append(alabel)

        self.live_widgets.append(self.Xmax)            
            
        self.selectionLayout.addWidget(alabel)
        self.selectionLayout.addWidget(self.Xmax)
        fill_layout_textbox(self.selectionLayout, ["", "",  "",  ""],alist = self.live_widgets)


        self.verticalLayout.addLayout(self.selectionLayout)
        self.setLayout(self.verticalLayout)

    def toggle_selection_layout(self,data_type = None):
        """call a fonction to delete the object of the layout properly"""
        if data_type == "Live" :
            for widget in self.past_widgets:
                widget.hide()
            for widget in self.live_widgets:
                widget.show()
        else:
            for widget in self.live_widgets:
                widget.hide()
            for widget in self.past_widgets:
                widget.show()
#        clear_layout(self.selectionLayout)


    def create_phys_layout(self, physparam_list=None):
        """
           The parameters that will be displayed depend on the function to fit, one has to describe the list here.
           This function creates a layout for the physically relevant parameter extracted from fit
        """
        logging.debug("Just called phys Layout")
        
        self.physLayout = QtGui.QVBoxLayout()
        self.physLayout.setObjectName("physLayout")
        self.phys_paramLayout = QtGui.QHBoxLayout()
        self.phys_param_labelLayout = QtGui.QHBoxLayout()
        
        #if there is no physical parameters we don't display them
        if np.size(self.physparam_list) == 0:
            pass
        else:
            #browse through the list of physical parameters
            for physparam in self.physparam_list:
                aLabel = QtGui.QLabel(self)
                aLabel.setText(physparam)
                self.aValue = QtGui.QLineEdit(self)
                self.phys_param_labelLayout.addWidget(
                    aLabel, alignment=Qt.AlignCenter)
                self.phys_paramLayout.addWidget(self.aValue)
                
                
            aLabel = QtGui.QLabel(self)
            aLabel.setText("Physical Parameters")
            self.physLayout.addWidget(aLabel,alignment=Qt.AlignCenter)
            
        self.physLayout.addLayout(self.phys_param_labelLayout)
        self.physLayout.addLayout(self.phys_paramLayout)

        self.verticalLayout.addLayout(self.physLayout)
        self.setLayout(self.verticalLayout)
        
        toggle_layout(self.physLayout,self.state)
        toggle_layout(self.phys_paramLayout,self.state)
        toggle_layout(self.phys_param_labelLayout,self.state)

    def remove_phys_layout(self):
        """call a fonction to delete the object of the layout properly"""
        
        clear_layout(self.phys_paramLayout)
        clear_layout(self.phys_param_labelLayout)
        clear_layout(self.physLayout)
        

    def create_fit_layout(self, fparam_list=None):
        """
           The parameters that will be displayed depend on the function to fit, they are automatically extracted from the functions described in the module Fitting
        """
        self.state
        logging.debug("Just called fit Layout")        
        
        if fparam_list == None:
            fparam_list = io.get_func_variables(self.fit_func)
            # the first variable is the x axis coordinate, is it not a fit
            # parameter
            fparam_list = fparam_list[1:]
        
        #store them for later use
        self.fit_func_variables = fparam_list
        
        #This is to choose whether one wants to pass the fit parameter
        #as a guess parameter or to fix one or more fit parameters
        fit_func_params = OrderedDict()
        fit_func_guess = OrderedDict()
        fit_func_fix_param = OrderedDict()
        
        for fp in self.fit_func_variables:
            
            #this should store the value of the fit param after the fit
            fit_func_params[fp] = None
            #if None, it will not be passed as a guess argument
            fit_func_guess[fp] = None
            #if False it is not fixed, if True it is fixed
            fit_func_fix_param[fp] = False
            
        #store this information for later use
        self.fit_params["fit_func_params"] = fit_func_params
        self.fit_params["guess"] = fit_func_guess
        self.fit_params["fix_param"] = fit_func_fix_param
        
        self.fitLayout = QtGui.QVBoxLayout()
        self.fitLayout.setObjectName("fitLayout")
        self.fit_param_labelLayout = QtGui.QHBoxLayout()
        self.fit_paramLayout = QtGui.QHBoxLayout()

        for fparam in fparam_list:
            aLabel = QtGui.QLabel(self)
            aLabel.setText(fparam)
            self.fit_param_labelLayout.addWidget(
                aLabel, alignment=Qt.AlignCenter)
                
            self.aCheckBox = QtGui.QCheckBox(self)       
            self.aCheckBox.setObjectName("ch_%s"%(fparam))
            self.connect(self.aCheckBox,QtCore.SIGNAL(
            'clicked()'), self.checkbox_handler)
            self.fit_paramLayout.addWidget(self.aCheckBox)
            
            self.aValue = QtGui.QLineEdit(self)
            self.aValue.setObjectName("le_%s"%(fparam))
            self.connect(self.aValue,QtCore.SIGNAL("editingFinished()"),self.lineedit_handler)            
            
            self.fit_paramLayout.addWidget(self.aValue)
#
        aLabel = QtGui.QLabel(self)
        aLabel.setText(u"Fit Parameters for %s"%(self.fit_func.__doc__))

        self.fitLayout.addWidget(aLabel,alignment=Qt.AlignCenter)
        self.fitLayout.addLayout(self.fit_param_labelLayout)
        self.fitLayout.addLayout(self.fit_paramLayout)

        self.verticalLayout.addLayout(self.fitLayout)
        self.setLayout(self.verticalLayout)
        
        
        #enable/disable the widget in the layout
        toggle_layout(self.fitLayout,self.state)
        toggle_layout(self.fit_paramLayout,self.state)
        toggle_layout(self.fit_param_labelLayout,self.state)
        


    def remove_fit_layout(self):
        clear_layout(self.fit_paramLayout)
        clear_layout(self.fit_param_labelLayout)
        clear_layout(self.fitLayout)

    def load_file_name(self):
        return self.loadFileLineEdit.text()


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain
    
    create a QDock widget and store a reference to the widget
    """    
    mywidget = FittingWidget(parent = parent)
    
    
     #create a QDockWidget
    analyseDataDockWidget = QtGui.QDockWidget("Fitting", parent)
    analyseDataDockWidget.setObjectName("analyseDataWidget")
    analyseDataDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
    analyseDataDockWidget.setWidget(mywidget)
    
    #fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['AnalyseDataWidget'] = mywidget        
    
    parent.addDockWidget(Qt.RightDockWidgetArea, analyseDataDockWidget)

    #Enable the toggle view action
    parent.windowMenu.addAction(analyseDataDockWidget.toggleViewAction())

    analyseDataDockWidget.hide()

def test_data_fitting():
    x = np.arange(0,10,1)
    y = np.array([0,-1,2,3,4,5,6,7,8,9])
   
    data = np.transpose(np.vstack((x,y)))
    
    app = QtGui.QApplication(sys.argv)
    ex = FittingWidget()
    ex.state = True
    ex.data_type_changed("Live")
    
    ex.update_data_and_fit(data)
    ex.update_data_and_fit()
    ex.show()
    sys.exit(app.exec_())

def test_limit_updates():
    """
    test the fitting
    """
    x = np.arange(0,10,1)
    y = np.array([0,-1,2,3,4,5,6,7,8,9])
   
    data = np.transpose(np.vstack((x,y)))
    
    app = QtGui.QApplication(sys.argv)
    ex = FittingWidget()
    ex.state = True
    ex.data_type_changed("Live")
    
    ex.update_selection_limits([0,1,3,9],0, 1, 1, 1)
    ex.show()
    sys.exit(app.exec_())

def test_data_type_switching():

    app = QtGui.QApplication(sys.argv)
    ex = FittingWidget()
    ex.state = True
    ex.data_type_changed("Live")
    ex.show()
    sys.exit(app.exec_())
    
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
            answer = np.append(answer,ad.exp_decay(idx-t_off, Yfinal, tau, 0) * (1 + 0.05 *(random.random() - 0.5)))
            dt = np.append(dt,idx)
            idx += 1
            
        return dt,answer
        
    t,y = dummy_exp()
    data = np.transpose(np.vstack((t,y)))
    
    app = QtGui.QApplication(sys.argv)
    ex = FittingWidget()
    ex.state = True
    ex.data_type_changed("Live")
    
    ex.update_data_and_fit(data)
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
#    test_data_fitting()
#    test_limit_updates()
#    test_fit_exponential()
    test_data_type_switching()

