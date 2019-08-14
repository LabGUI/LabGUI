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

This package is designed to work with Python 3. Fresh installations require Python >= 3.6

## Using the setup script

For a fresh install of LabGUI with Python3 and git in the directory where you wish to install, type the following into your favorite shell:
```
git clone https://github.com/LabGUI/LabGUI.git
cd LabGUI
python setup.py install
```
This will clone LabGUI to the current directory using git, set up a virtual environment, install all required packages, and create a configuration file via `setup_new.py` script, and will add LabGUI to the path.

By cloning the repository, you can easily use git to update LabGUI by calling
```
git stash
git pull
git stash apply
```
Using git also has the added benefit of allowing you to create your own branches, to fully customize LabGUI to suit your needs, while still allowing you to fetch/merge new features/hotfixes/updates.
## Using pip ##

Setup a [virtual environement](https://virtualenv.pypa.io/en/latest/)

For powershell in windows 10:
```
pip install virtualenv
```
```
virtualenv my_venv
```
```
<path to my_venv>\my_venv\Scripts\activate
```

Then run 

```
pip install -r requirements.txt
```

## Using Anaconda ##

For Windows/Mac/Linux you can install [anaconda](https://www.anaconda.com/download/)

and then from the anaconda console you can type 
```
conda install --yes --file requirements.txt
```
## Using Linux ##

Under some distributions of Linux, Python >= 3.6 may not be easily available through regular repositories. 
To simplify installation under Linux, there are several scripts useful scripts under `tools/linux/`

####Complete install script ####
Built under Debian9, `install_all.sh`, which must be run as root, will install Python3.7, LabGUI, and Linux-GPIB. If you wish to install these components separately, please see the following:
####Installing Python 3.7 ####
The script `install_python3.7.sh` downloads the Python-3.7.3 tarball, and builds it from source. By default, this script assumes that there already exists an earlier version of Python 3, and therefore installs it as `python3.7`


To overwrite your current version of Python 3, in `install_python3.7.sh`, comment out
`make altinstall` and uncomment `make install`. You will need to run this with root privileges.

If you would rather use an install package other than `apt-get`, simply replace all 3 occurences of it in this script.

#### Installing USB-GPIB interface ####

For certain distributions, you can download the proprietary NI visa drivers [here](https://www.ni.com/en-us/support/downloads/drivers/download.ni-linux-device-drivers.html).
If you are unable or do not wish to install the NI visa drivers, you can instead install the open-source linux-gpib drivers. If this package is not easily available through regular repositories, you can either build linux-gpib from source, or install it using the `install_linux-gpib.sh` script. Note that this script MUST be run as root, and you must specify which Python3 installation to use.

You can allow the script to copy the example `gpib.conf`, or make your own modifications to `/etc/gpib.conf` as you see fit.

Afterwards, you simply need to add the following to config.txt

```buildoutcfg
VISA_BACKEND=py
```

Or change the PyVISA backend via the GUI configuration manager built into LabGUI.

NOTE: If you do not allow for the devices under `/dev/gpib[0-9]` to be read/written by any user, you must launch LabGUI as root


## Install PyQt5 ##
We use PyQt5 for the GUI and handling signals.
```
pip install pyqt5
```

If you have PyQt4 installed it should work as well (however, there is no guarantee). We would recommend using PyQt5 rather than PyQt4. However, if you really want to install PyQt4, here are some instructions on how to do so : http://pyqt.sourceforge.net/Docs/PyQt4/installation.html. You can also install an out-dated version of LabGUI

### Installing SIP (prerequisite to PyQt4) ###
* for newer version of python, simply run any of the following
    * `python[3] -m pip install sip`
    * `pip[3] install sip`
* for python 3.5 (windows 10) simply  "c:\python35\python -m pip install sip"
* for python 3.4 (linux), download https://www.riverbankcomputing.com/software/sip/download follow their instructions
* for python 3.4 (windows 10), download https://www.riverbankcomputing.com/software/sip/download follow their instructions

### About our use of PyQt5 ###

An interesting feature of PyQt5 is the signals and slot, they allow different widgets to communicate with each other. Learn more about this ![here](https://pythonspot.com/pyqt5-signals-and-slots/)

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

Alternatively, if you added LabGUI to the path via setup.py, it can be launched in your favorite shell as follows:
```
LabGUI
```


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

## Tools menu ##
* Configurations Manager
* User-Widget Manager
* Restart LabGUI

## Options menu ##
* Set logger level
* Change debug mode
* Change GPIB interface
* Run the GPIB command line


## Output/input files ## 

* Configuration File

This file should be in the same directory as the `LabGui.py` file, we named it `config.txt` (this can be changed).
If you don't have one, it will be generated for you with basic settings.

Alternatively, you can run
```buildoutcfg
python config_generate.py
```
And follow the user prompts.

This file contains the path of the script file, data folder, setting file, and the debug mode.
It is possible to add more variable you might want to save there, you can use the functions get_config_setting() and set_config_setting() of the `IOTool.py` module to read and write them from/into the file.

This file also defines where data is saved, what widgets are to be loaded, what GPIB and VISA interfaces to use, and the default script to run.

* Settings File

This contains the details of the instrument hub (each line corresponds to an instrument with its name, the port it is using and the parameter it is measuring).
You can save your current instrument hub setting using "file -> save setting".
You can load a previously saved instrument hub setting using "file -> load setting".
You can have a setting file saved to and loaded from automatically on start/exit by adding the following line to your configuration file: `SETTINGS=path_to_your_setting_file`

* Script File

As what one wants their instrument(s) to do is probably different than from person to person, LabGUI allows for custom scripts to be run.

User scripts are in the namespace of the DataTaker class, in the DataManagement module, and is executed whenever the method of the class DataTaker run() is called (which is whenever someone press the button play or start in the GUI)

It was designed to allow modifications in the script to be made between runs without having to restart LabGUI.


* Data File

This file contains the data in the format the user defined (depends on each experiments), the default format is that each line correspond to a different measurement, each row is a different parameter of an instrument.

The first 3 lines are headers with the information about the instruments and their connections.

Other commented lines correspond to user-variables or notes taken in the OutputFile and UserData widgets.

## Debug Mode ##

The debug mode is accessible through the menu option file. This is used to test functionalities of the GUI when not in the lab or not having an actual connection to the instruments. It is a property that all or drivers have in their class Instrument, and also most of the widgets.

## Main Module ##
The module LabGui contains the main function, which is an instance of QMainWindow. It acts as mediator pattern and connect different services together:

- instrument connection settings
- running an experiment
- collection of the data
- management of the collected data
	- plotting
	- writing to a file
	- fitting
- running specific user-scripts/widgets

The communication between the different services and the server is done using QtCore.SIGNAL, this way we can set up various listeners to the same signal which will all take different actions.

# GPIB Command-Line #

The GPIB Command-Line is accessible through the option menu. The module `CommandWidget` contains all functions relating to the command line. It is designed to ease the debugging process of both driver and device. It has features that enable custom write/sweep functions to be run, and sweep data to be plotted. It can be used to access multiple connected devices concurrently

It is designed to be a custom shell for the LabGUI program, with its own built-in functions and syntax. Generally, the first word corresponds to the command, where all subsequent words are parameters fed to the command. It uses Shlex syntax processing. Fully equipped with environment variables, adding a new command is as easy as adding if statement to the `execute_command` function


Specifically, it offers the following features:

### read ###
This command reads data in the specified device's buffer, and prints it into the console.

### write \<GPIB command\> ###
This command writes any GPIB command to the specified device.

### ask/query \<GPIB command\> ###
This command queries any GPIB command to the specified device, printing the response to the console.

### methods ###
This command returns all callable functions available from the device's driver.

### run \<function\> \<parameters\> ###
This command will execute any callable function (viewable via the `methods` command), with the specified parameters separated by spaces, and print the return data to the console.

### plot \<function\> \<parameters\> ###
This command plots the return data of any callable function. If the return data is not plottable, it is printed to the console. This function uses MatPlotLib, with axis labelling available via the `numbers` environment variable.

The return value of the function must be a list of plottable points of any dimension `n`. By default, the `plot` command will plot all possible unordered combinations of values, with the smallest index of two values as the x-axis.

This will produce `n-1` separate windows containing subgraphs, with `C(n,2)` graphs in total.

### set \<variable\> \<parameters\> ###
This command relates to setting/retrieving environment variables. It has the following possible uses

`set`  returns all environment variables and their values.

`set <variable>` returns the value of `<variable>`

`set <variable> <parameters>` sets `<variable>` to have the value `<parameter>`.

Environment variables can be set to both single values and a list of values. To set a list, simply separate all values by a space.

`set <variable> value1 value2 value3` sets `<variable>` to `['value1', 'value2', 'value3']`

To change a specific value in a list, `<parameter>` must be of the form `position=value`

Using the example above, `set <variable> 0=changed_value` sets `<variable>` to `['changed_value', 'value2', 'value3']`

To access environment variables in other commands, you must use `$varname` in a parameter. If you want to access the value of an environment variable by index, use `$varname{index}`, where index is an integer. To test the output of your command, use `echo <parameter>`

You can use environment variables in a string by enclosing it in quotations. Variables <i>must</i> be separated by other words by a space. Example: `variable is $varname units` will replace `$varname` by its value iff it exists

The only limitation of this usage is that it cannot be used to change the size of the list

### unset ###

Usage: `unset <variable>` will remove environment variable by the name `<variable>`

### echo ###

Usage: `echo <parameter>` will process `<parameter>` like it would with any other function, and print the result to screen to ensure proper output.

If environment variable `INFO` is set to `True`, it will also print the data structure of the processed `<parameter>`
### clear ###
As the name suggests, `clear` clears the console window

### history \<number\> ###

This prints command history to the console. It has the following usage:

`history` prints the entire command history of the current session

`history <+integer>` prints the last `<positive integer>` commands to the console

`history <-integer>` prints all commands executed after the specified position to the console

### last/recall \<index\> ###

This command is designed to recall previously executed commands

`last` removes the last command executed from the history, and places it in the command line.

`last <+index>` recalls the last command at index without removing it from the history, and places it in the command line.

`last <-index>` recalls the first command at index from the session without removing it from the history, and places it in the command line.

Example: `last 1` recalls the last command executed, whereas `last -1` recalls the first command executed



# How to include your own instrument into LabGUI #
## Instrument Driver ##

The class called "MeasInstr" in the module "Tool" is a basic instance from which all instrument driver inherits, it manages the actual connection (visa, serial, etc...)
and overloads the functions read, write and ask.

An instrument driver is a module named after the instrument, it needs to have the following properties:

- a variable called `param` which is a dictionary
- a variable called <b>INTERFACE</b> which specifies which interface, amongst the ones available, will be used to connect to the instrument
- a class called "Instrument" inheriting from "Tool.MeasInstr"
- it needs to be within the folder/package `LabDrivers` to be accessible from LabGui

The following are optional properties that allow for more functionality:

- a variable called `properties` which is a special dictionary, allows you to write to the device through <b>PropertiesWidget</b>
    - the key represents the <b>channel</b>
    - the value is another dictionary, which specifies type, range, units, etc
    - The `get` and `set` methods allow for these values to be read and written.

Please see `driver_example_rw.py` for more detailed usage

- a variable called `functions` which is a special dictionary, allows you to execute custom commands to connected devices at any stage through <b>FunctionWidget</b>
    - the key represents the <b>function</b> (channel)
    - the value is an array of objects describing the possible variables and variable type, as well as units, range, type, and whether or not it is a required argument
    - the `run` method allows for these functions to be executed

For driver examples and templates, see
- driver_example[_rwx].py
- driver_template[_rwx].py

When acquiring a new instrument, the first thing to find out what is it's "communication protocol". 
This will help you identify which port to connect to and what interface your instrument uses (visa, serial, raw, TCP/IP, etc...)

There are different steps between this stage and the stage when you collect data and interact with your instrument using LabGui:

- establish a physical connection between your computer and your instrument.
- communicate with your instrument with its own vocabulary and grammar.
- figure out which commands you need.
- write a driver file with python methods that send the command using the instrument vocabulary
- write what you want to ask/tell your instrument in a script using these python methods
 

## Physical connections to your instrument ##

Ways to connect physically to the instrument through a GPIB port:

- PROLOGIX GPIB to USB ([driver here](http://prologix.biz/))
- National Instruments GPIB to USB (PyVISA)
- Agilent GPIB to USB (PyVisa)

Through serial:
- RS232 (RS232 to USB adapters are available from various vendors and should all work with LabGUI)

Through third-party software:
- Sockets to read data from a server
- Using third-party python libraries

To use a specific interface, the <b>INTERFACE</b> property of you driver must be set to any of the following:
- `INTF_GPIB` allows for any GPIB-type connection
    - `INTF_VISA` specifies PyVISA
    - `INTF_PROLOGIX` specifies prologix
- `INTF_SERIAL` specifies RS232 using PySerial
- `INTF_NONE` specifies the default connections are built in (IE third party)

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


## Using LabGUI Core Widgets ##

Built into LabGUI, there are a set of core widgets in which it bases it's operation.
Among these are several designed to help analyse/manipulate data and aid in seemless communication with devices.

These widgets can be enabled/disabled from the `Window` dropdown menu.

#### Remote Enable  Widget ####
This widget allows the user to bring any device into a specific REN state, as well as set the default state for all connected devices.

#### Instrument Widget ####
This widget allows the user to select which instruments to connect to, from a list of device drivers as well as connected ports. By default, the state of this widget is loaded on launch, and saved on exit.

#### Command Widget ####
This widget is the GPIB Command-Line Widget, described above.

#### Output File Widget ####
This widget allows to the user to specify where data is saved, as well as leave some notes as comments in that datafile. Notes left by the user is saved/loaded by default.

#### Script Widget ####
This widget allows the user to specify which script is to be run via DataTaker.

#### Properties Widget ####
This widget allows the user to select from a list of connected devices, and modify any properties that may be available within the devices' driver.

#### Function Widget ####
This widget allows the user to select from a list of connected devices, and run any functions that may be available within the devices' driver.

#### User Data Widget ####
This widget is an extension to the Output File Widget comment saver, 

#### Load Plot Widget ####
This widget allows the user to load and plot previously taken data, with functionality extending to `User Data Widget` and `Output File Widget`.

#### Console Widget ####
This widget intercepts all strings sent to the `Standard Output` and prints them within the window, acting as a read-only terminal window.