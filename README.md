LabGui
======

# Introduction #
Modular python data acquisition software and GUI.

LabGUI has been written by grad students in experimental condensed matter physics. It is intended to overcome the frustration that most of the time measuring-instruments come with their own dummy software with very poor or no integrability into a larger "meta" software coordinating the instruments. It was developped with the philosophy to share the maximum of the code to interface with the instruments while still allowing to run different types of experiments. Being two main developpers on the projects with our own specific experimental needs, helped us to make this software modular.

## Laboratories using LabGUI ##

* http://gervaislab.mcgill.ca/home.php @ McGill University
* http://carbon.ece.mcgill.ca @ McGill University
* https://www.hybridquantumlab.com/ @ Michighan state University

## Publications which used LabGUI to acquire their data ##

* Anomalous Attenuation of Piezoacoustic Surface Waves by Liquid Helium Thin Films, H. Byeon, K. Nasyedkin, J.R. Lane, L. Zhang, N.R. Beysengulov, R. Loloee and J. Pollanen, Journal of Low Temperature Physics (2018) https://doi.org/10.1007/s10909-018-02115-0 (online first).

* Flip-chip Gate-tunable Acoustoelectric Effect in Graphene, J.R. Lane, L. Zhang, M.A. Khasawneh, B.N. Zhou, E.A. Henriksen, and J. Pollanen, Journal of Applied Physics  124, 194302 (2018).

* Unconventional Field Effect Transistor Composed of Electrons Floating on Liquid Helium, K. Nasyedkin, H. Byeon, L. Zhang, N.R. Beysengulov, J. Milem, S. Hemmerle, R. Loloee and J. Pollanen, Journal of Physics: Condensed Matter  30, 465501 (2018).

*  Specific heat and entropy of fractional quantum Hall states in the second Landau level, B.A. Schmidt, K. Bennaceur, S. Gaucher, G. Gervais, L.N. Pfeiffer, K.W. West, Phys. Rev. B 95, 201306(R) (2017). 

*  Dual-Gate Velocity-Modulated Transistor Based on Black Phosphorus, V. Tayari, N. Hemsworth, O. Cyr-Choinière, W. Dickerson, G. Gervais and T. Szkopek, Phys. Rev. Applied 5, 064004 (2016).  

* Second Landau Level Fractional Quantum Hall Effects in the Corbino Geometry, B. A. Schmidt, K. Bennaceur, S. Bilodeau, G. Gervais, K. W. West, L. N. Pfeiffer, Solid State Communications 217, 1 (2015).

* Critical flow and dissipation in a quasi–one-dimensional superfluid, P-F Duc, M.Savard, M. Petrescu, B. Rosenow, A. Del Maestro, and G. Gervais, Science Advances 1, el1400222 (2015). 


## Scope and limitations ##

The present software was not designed and is certainly not suited for high speed data acquisition (like CCD camera or oscilloscope). For an example of CCD python wrapper see https://bitbucket.org/abracadabri/princetoninstrument/src/master/.
We designed it to acquire data from multiple instruments over timescales of the order of seconds (we run long experiments). The fastest one can go using our software depends mainly on the interface used to connect to the instrument. If you want to monitor the temperature, the pressure, have a PID loop over one of these values, set a magnetic field and sweep over different voltage ranges for each different values of magnetic field, or anything similar, then this software is suited for you as it is very unlikely that many different instruments will have a common interface from which you can control them.

# Installation #

For the time being this package is only supported in python 2.7 (but we are working to make it work in python 3)

## Using pip ##

Open a terminal and run 

```
#!python

pip install -r requirements.txt
```

The requirement file contains the following lines :
```
PyVISA
matplotlib
numpy
pyserial

```

## Using Anaconda ##

For Windows/Mac/Linux you can install [anaconda](https://www.anaconda.com/download/)

and then from the anaconda console you can type 
```
conda install --yes --file requirements.txt
```

## Install PyQt4/5 ##
We use PyQt4/5 for the GUI and handling signals. If one of the version (i.e. 4 or 5 is not already installed you have to do it).

If you operate under python 3 you should be able to install PyQt5 simply by typing

```
#!python
pip install pyqt5

```

If you have PyQt4 installed it should work as well (not 100% garanteed). We would not recommand installing PyQt4 and rather using PyQt5. However, if you really want to install PyQt4, here are some instructions on how to do so : http://pyqt.sourceforge.net/Docs/PyQt4/installation.html. Can also refer to the possibily outdated instructions.

### Installing SIP (prerequisite to PyQt4) ###
* for python 3.5 (windows 10) simply  "c:\python35\python -m pip install sip"
* for python 3.4 (linux), download https://www.riverbankcomputing.com/software/sip/download follow their instructions
* for python 3.4 (windows 10), download https://www.riverbankcomputing.com/software/sip/download follow their instructions

### Installing PyQt4 ###
* for python 3.4 (windows 10), download https://www.riverbankcomputing.com/software/pyqt/download
* for python 3.4 linux, download https://www.riverbankcomputing.com/software/pyqt/download and follow their instructions

### About our use of PyQt4/5 ###

An interesting feature of PyQt4/5 is the signals and slot, they allow different threads to communicate with each other. Learn more about those ![here](https://www.tutorialspoint.com/pyqt/pyqt_signals_and_slots.htm) for PyQt4 and ![here](https://pythonspot.com/pyqt5-signals-and-slots/) for PyQt5.

## Additional drivers ##

Depending on how you connect your instruments to your computer, you might have to download drivers for the communication hub, pyvisa has some requirements which you can find by googling pyvisa. This topic is covered later in the readme.

# Useful commands #

To run the coverage tests

https://coverage.readthedocs.io/en/coverage-4.5.1/

```
#!bash

coverage run

```

To see the report do

```
#!bash

coverage report

```
or

```
#!bash

coverage html

```

# Structure #

You need to add LabGui folder to your PYHTON PATH (look for ways to do so) before starting.

# Getting started #

What you can do is call the program from a python console by typing 
```
#!python

run(path_to_the_folder/LabGui.py)
```

in a terminal by typing
```
#!bash

python path_to_the_folder/LabGui.py

```
or you can open the file LabGui.py in Spyder/PyCharm and run it.

It should prompt a window similar to this one :

![Example_LabGui.png](https://bitbucket.org/repo/8gbrjn/images/400678764-Example_LabGui.png)


## File menu ##

* Load Instrument Settings: prompt a dialogue to select a file which contains details about instruments connections and parameters to measure.
* Save Instrument Settings: prompt a dialogue to save the current instruments connections and parameters to measure to a file.
* Load Previous Data: prompt a dialogue to select an output file and display its data on a plot window for data analysis.
* Save Figure: save the current plot window into an image file.
* Save current configuration: save the configuration details as their are into the "config.txt" file.


## Plot menu ##
Most of the choices here are a duplicate of the options of the taskbar. They are quite intuitive so we won't describe their use here.

* Clear All Plot: remove all lines on on all plot windows.
* Remove fit: remove the line corresponding to a fit from all plot windows.

## Meas/Connect menu ##

* Start DDT: start the Data Taker Thread, i.e execute the code defined in the script file provided by the user. This code can be a loop only stopped by user interaction or passing across threshold values for a given instrument's parameter. It could also be a sweep of a given instrument's parameter.
* Read: call the `measure` method of all instruments connected to the instrument hub (in the `Instrument Setup` widget) with the corresponding parameter.
* Connect instruments: initiate the connection between the computer and the instruments in the instrument hub.
* Refresh port list: refresh the available ports to connect instruments in the comboboxes under the `Port` label in the `Instrument Setup` widget.

## Window menu ##
This menu shows you what are the widget currently displayed (they have a tick on the left of their name. If you click on one it will hide/display it on a toggle mode.

* Add a Plot
* Instrument Setup
* Live Calculations
* Limits
* Output file and header text
* Load previous data file
* Fitting
* Output Console
* Simple instrument console

## Options menu ##
* Change debug mode


## Output/input files ## 

* config file
This file should be in the same directory as the `LabGui.py` file, we named it `config.txt` (this can be changed).
If you don't have one, it will be generated for you with basic settings. 
This file contains the path of the script file, data folder, setting file, and the debug mode.
It is possible to add more variable you might want to save there, you can use the functions get_config_setting() and set_config_setting() of the `IOTool.py` module to read and write them from/into the file.

* the setting file
contains the details of the instrument hub (each line corresponds to an instrument with its name, the port it is using and the parameter it is measuring).
You can save your current instrument hub setting using "file -> save setting".
You can load a previously saved instrument hub setting using "file -> load setting".
You can have a setting file loading automatically by adding the line "SETTINGS=path_to_your_setting_file"

* script file
As what one want their instrument(s) to do is probably different than what another person would want, this part is described into a separated script.
It has the namespace of the DataTaker class in the DataManagement module and is executed whenever the method of the class DataTaker run() is called (which is whenever someone press the button play or start in the GUI)
It was designed in a way so there is no need to restart the whole GUI when changing something in the script file to have those changes being effective.

* data file
This file contains the data in the format the user defined (depends on each experiments), the default format is that each line correspond to a different measurement, each row is a different parameter of an instrument.
The first 3 lines are headers with the information about the instruments and their connections.

## Debug Mode ##

The debug mode is accessible through the menu option file. This is used to test functionalities of the GUI when not in the lab or not having an actual connection to the instruments. It is a property that all or drivers have in their class Instrument, and also most of the widgets.

The module LabGui contains the main function, which is an instance of QMainWindow. It acts as mediator pattern and connect different services together:

- instrument connection settings
- running an experiment
- collection of the data
- management of the collected data
	- plotting
	- writing to a file
	- fitting
The communication between the different services and the server is done using QtCore.SIGNAL, this way we can set up various listeners to the same signal which will all take different actions.



# How to include your own instrument into LabGUI #
## Instrument Driver ##

The class called "MeasInstr" in the module "Tool" is a basic instance from which all instrument driver inherits, it manages the actual connection (visa, serial, etc...)
and overloads the functions read, write and ask.

An instrument driver is a module named after the instrument, it needs to have the following properties:

-a variable called "param" which is a dictionary
-a variable called INTERFACE which specifies which interface, amongst the ones available, will be used to connect to the instrument
-a class called "Instrument" inheriting from "Tool.MeasInstr"
-it needs to be within the folder/package `LabDrivers` to be accessible from LabGui

When acquiring a new instrument, the first thing to find out is a file called "communication protocol". 
This will help you identify which port to connect to and what interface your instrument uses (visa, serial, raw, TCP/IP, etc...)

There are different steps between this stage and the stage when you collect data and interact with your instrument using LabGui:
 -establish a physical connection between your computer and your instrument.
 -communicate with your instrument with its own vocabulary and grammar.
 -figure out which commands you need.
 -write a driver file with python methods that send the command using the instrument vocabulary
 -write what you want to ask your instrument in a script using these python methods
 

## Physical connections to your instrument ##

Ways to connect physically to the instrument through a port:

- PROLOGIX GPIB to USB
- National Instruments GPIB to USB
- Agilent GPIB to USB

RS232 (RS232 to USB adapters are available from various vendors and should all work with LabGUI)


# Organisation scheme #

The class `LabGuiMain` inherits of `QtGui.QMainWindow` (referred to as main window), it will contain instances of :
- an instrument hub (`Tool.InstrumentHub`) which manages the connection to the physical and virtual measure instruments 
- a datataker (DataManagement.DataTaker) responsible to run, pause and stop the script describing the experiment as well as to share the acquired data with the main window (which itself dispatches them according to the mediator pattern)
- a list of `QtGui.QWidgets` used for user interaction with instruments, data acquisition, vizualisation or fitting and parameters input.

The widgets are separated into the "Core" widgets, the minimal set of widgets needed to operate LabGUI, and the "User" widgets, a collection of user defined extra widgets which can be included or not into LabGUI. The user widgets have usually specific uses and are not automatically included in the available widgets to ease the user experience.

An analogy of PyQt signal would be to picture "talkers" and "listeners", the talkers send signals which are catched by listeners. This connection has to be defined somewhere and the listeners only listen to the talkers they have been assigned. One talker can have many listeners or none.

The widgets communicate with each other through the main window, i.e. two distinct widgets should not be able communicate directly (because that would require to set a talker-listener connection between them and thus require that both widgets are presents in the main window, which might not necessarily be the case). Instead the design should be that each widget is connected to the main window and communicate data/information with it. The main window can then send signals depending on the data/information which can be listened by many widgets, while maintaining the widgets independent of each others (see next section for more details).

## Creating custom widgets for LabGUI ##

It is possible to add custom widgets to LabGUI (for example if you need a specific interface for one of your instrument). To do this you have to create a file in the `LabTools/UserWidgets` package. In this file you need to define your widget (it needs to inherit from PyQt's `QWidget`) and a function called `add_widget_into_main(parent)` which defines the signals this widget should exchange with the `QMainWindow` and potential methods to handle those signals. (The idea is that all the code which concerns your widget should be embedded into this file, LabGUI should be able to run with or without the addition of your widget. In the initialisation of LabGUI, the widget files listed in the `config.txt` file under `USER_WIDGETS` and separated by a semicolumn will be added to the interface. 
Example of line in the `config.txt file`:
```
USER_WIDGETS=ConnectTerminalWidget;ServerWidget
```

Use the file `TemplateUserWidget.py` for more practical information and to start your own widgets!


