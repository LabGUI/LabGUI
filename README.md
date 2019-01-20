LabGui
======

# Introduction #
Modular python data acquisition software and GUI.

LabGui has been written by grad students in experimental physics. It is intended to overcome the frustration that most
instruments come (came? times change) with their own dummy software with very poor or no integrability into a larger "meta" software coordinating the instruments.

## Laboratories using LabGUI ##

* http://gervaislab.mcgill.ca/home.php @ McGill University
* http://carbon.ece.mcgill.ca @ McGill University
* https://www.hybridquantumlab.com/ @ Michighan state University

## Peer-reviewed articles linked to the use of LabGUI ##


* Anomalous Attenuation of Piezoacoustic Surface Waves by Liquid Helium Thin Films, H. Byeon, K. Nasyedkin, J.R. Lane, L. Zhang, N.R. Beysengulov, R. Loloee and J. Pollanen, Journal of Low Temperature Physics (2018) https://doi.org/10.1007/s10909-018-02115-0 (online first).

* Flip-chip Gate-tunable Acoustoelectric Effect in Graphene, J.R. Lane, L. Zhang, M.A. Khasawneh, B.N. Zhou, E.A. Henriksen, and J. Pollanen, Journal of Applied Physics  124, 194302 (2018).

* Unconventional Field Effect Transistor Composed of Electrons Floating on Liquid Helium, K. Nasyedkin, H. Byeon, L. Zhang, N.R. Beysengulov, J. Milem, S. Hemmerle, R. Loloee and J. Pollanen, Journal of Physics: Condensed Matter  30, 465501 (2018).

*  Specific heat and entropy of fractional quantum Hall states in the second Landau level, B.A. Schmidt, K. Bennaceur, S. Gaucher, G. Gervais, L.N. Pfeiffer, K.W. West, Phys. Rev. B 95, 201306(R) (2017). 

*  Dual-Gate Velocity-Modulated Transistor Based on Black Phosphorus, V. Tayari, N. Hemsworth, O. Cyr-Choinière, W. Dickerson, G. Gervais and T. Szkopek, Phys. Rev. Applied 5, 064004 (2016).  

* Second Landau Level Fractional Quantum Hall Effects in the Corbino Geometry, B. A. Schmidt, K. Bennaceur, S. Bilodeau, G. Gervais, K. W. West, L. N. Pfeiffer, Solid State Communications 217, 1 (2015).

* Critical flow and dissipation in a quasi–one-dimensional superfluid, P-F Duc, M.Savard, M. Petrescu, B. Rosenow, A. Del Maestro, and G. Gervais, Science Advances 1, el1400222 (2015). 

# Installation #


For the time being this package is only supported in python 2.7 (but we are working to make it work in python 3)

## Using pip ##

Find the requirements.txt file and run 

```
#!python

pip install -r requirements.txt
```

The requirement file contains the following lines :
```
PyVISA==1.8
matplotlib==1.5.1
numpy==1.11.0
pyserial==3.0.1

```

Then the output of the command
```
#!python

pip freeze
```
should be 
```
PyVISA==1.8
cycler==0.10.0
enum34==1.1.3
matplotlib==1.5.1
numpy==1.11.0
pyparsing==2.1.1
pyserial==3.0.1
python-dateutil==2.5.3
pytz==2016.4
six==1.10.0
```
For python 2.7
and should be 
```
cycler==0.10.0
matplotlib==1.5.1
numpy==1.11.0
pyparsing==2.1.4
pyserial==3.0.1
python-dateutil==2.5.3
pytz==2016.4
PyVISA==1.8
six==1.10.0
```
for python 3.4

Unfortunately we use PyQt4 which cannot be easily installed by pip, you should look how to install PyQt4 on google or install Anaconda or PythonXY

If you don't know if you have PyQt4 open a python prompt and type

```
#!python

import PyQt4
```
It shouldn't generate error messages

### Anaconda ###

For Windows/Mac/Linux you can install [anaconda](https://www.continuum.io/downloads)


### Python XY ###

On windows only you can install [Python XY](https://python-xy.github.io/downloads.htm)


## Without pip ##

The minimal requirements is the following list of packages

```
PyVISA==1.8
matplotlib==1.5.1
numpy==1.11.0
pyserial==3.0.1

```

You should be able to get numpy and matplotlib if you installed Anaconda or Python XY. An easy way to check if you have the two others is to type 


```
import visa
``` 

and

```
import serial
```
if you get no error messages you should be good to go.

## Install PyQt4 manually ##
###Installing SIP (prerequisite to PyQt4)###
for python 3.5 (windows 10) simply  "c:\python35\python -m pip install sip"
for python 3.4 (linux), download https://www.riverbankcomputing.com/software/sip/download follow their instructions
for python 3.4 (windows 10), download https://www.riverbankcomputing.com/software/sip/download follow their instructions


###Installing PyQt4###
for python 3.4 (windows 10), download https://www.riverbankcomputing.com/software/pyqt/download
for python 3.4 linux, download https://www.riverbankcomputing.com/software/pyqt/download and follow their instructions



## Additional drivers ##

Depending on how you connect your computer to your instruments you might have to download drivers for the communication hub, pyvisa has some requirements which you can find by googling pyvisa. This topic is covered latter in the readme.

# Structure #

You need to add LabGui folder to your PYHTON PATH (look for ways to do so) before starting.

#Getting started#

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


##File menu##

* Load Instrument Settings
* Save Instrument Settings
* Load Previous Data
* Save Figure
* Save current configuration


##Plot menu##
Most of the choices here are a duplicate of the options of the taskbar. They are quite intuitive so we won't describe their use here.

* Clear Plot
* Remove fit

##Meas/Connect menu##

* Start DDT
* Read
* Connect instruments
* Refresh port list

##Window menu##
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

##Options menu##
* Change debug mode


##Output/input files## 

* config file
This file should be in the same directory as the LabGui.py, we named it config.txt (this can be changed).
If you don't have one, it will be generated for you with basic settings. 
This file contains the path of the script file, data folder, setting file, and the debug mode.
It is possible to add more variable you might want to save there, you can use the functions get_config_setting() and set_config_setting() of the IOTool.py module to read and write them from/into the file.

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
This file contains the data in the format the user defined (depends on each experiments), the format by default is each line correspond to a different measurement, each row is a different parameter of an instrument.
The first 3 lines are headers with the information about the instruments and their connections.

##Debug Mode##

The debug mode is accessible through the menu option file. This is used to test functionalities of the GUI when not in the lab or not having an actual connection 
to the instruments. It is a property that all or drivers have in their class Instrument, and most of the widgets also.

The module LabGui contains the main function, which is an instance of QMainWindow. It acts as a server and connect different services together:

- instrument connection settings
- collection of the data
- management of the collected data
- plotting

The talk between the different services and the server is done using QtCore.SIGNAL, this way we can set up various listeners to the same signal which will all take different actions.


#Scope and limitations#

The present software was not designed and is certainly not suited for high speed data acquisition (like CCD camera or oscilloscope). For an example of CCD python wrapper see (projet Hélène).
We designed it to acquire data from multiple instruments over timescales of the order of seconds (we run long experiments). The fastest one can go using our software depends mainly on the interface used
to connect to the instrument. If you want to monitor the temperature, the pressure, have a PID loop over one of these values, set a magnetic field and sweep over different voltage ranges for each different values of magnetic field, or anything similar,
then this software is suited for you as it is very unlikely that many different instruments will have a common interface from which you can control them.

#How to include your instrument#
##Instrument Driver##

The class called "MeasInstr" in the module "Tool" is a basic instance from which all instrument driver inherits, it manages the actual connection (visa,serial,etc...)
and overloads the functions read, write and ask.

An instrument driver is a module named after the instrument, it needs to have the following properties:

-a variable called "param" which is a dictionary
-a variable called INTERFACE which specifies which interface, amongst the ones available, will be used to connect to the instrument
-a class called "Instrument" inheriting from "Tool.MeasInstr"
-it needs to be within the folder/package LabDrivers to be accessible from LabGui

When acquiring a new instrument, the first thing to find out is a file called "communication protocol". 
This will help you identify which port to connect to and what interface your instrument uses (visa, serial, raw, TCP/IP, etc...)

There are different steps between this stage and the stage when you collect data and interact with your instrument using LabGui:
 -establish a physical connection between your computer and your instrument.
 -communicate with your instrument with its own vocabulary and grammar.
 -figure out which commands you need
 -write a driver file with python methods that send the command in the instrument vocabulary
 -write what you want to ask your instrument in a script using the python functions
 

##Physical connections to your instrument##

Ways to connect physically to the instrument through a port:

PROLOGIX GPIB to USB
National Instruments GPIB to USB
Agilent GPIB to USB

RS232 (RS232 to USB adapters are available from various vendors and should all work with LabGUI)
