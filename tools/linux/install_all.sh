#!/bin/bash

# installer for LabGUI for linux, which includes 
#	- building python3.7 from source
#	- installing all required libraries
#	- running `python3.7 setup.py install`
#	- building linux-gpib from source, 
#		including kernel patch and python wrapper
#
#
# NOTE: Currently untested, TODO: create fresh debian/ubuntu install and try


root_warning () {
	echo "You must run this as root!"
	exit 6
}
apt-get update -y || root_warning

SCRIPT_PATH=`dirname $(readlink -f $0)`
echo $SCRIPT_PATH
exit 0
SCRIPT_PATH_BACKUP="$SCRIPT_PATH"
cd_to_script_dir() {
	cd "$SCRIPT_PATH"
}

cd_to_labgui_dir() {
	# this is a bit ugly but it does the job
	cd "$SCRIPT_PATH"
	cd ../../
}

error_inst () {
	case "$1" in
		1)
			echo "Error installing python3.7"
			exit 1
			;;
		2)
			echo "Error running setup.py"
			exit 2
			;;
		3)
			echo "Error installing linux-gpib"
			exit 3
			;;
		*)
			echo "Unknown error"
			exit 255
			;;
	esac
}

# BUILD PYTHON3.7 FROM SOURCE

cd_to_script_dir

bash ./install_python3.7.sh || error_inst 1

# INSTALL ALL REQUIRED LIBRARIES

apt-get install python3-pip -y

reqs=($(cat ../../requirements.txt))

for i in "${reqs[@]}"; do
	apt-get install "python3-$i" -y
done

# RUN python3.7 setup.py install


cd_to_labgui_dir

python3.7 setup.py install || error_inst 2


# build linux-gpib from source, and specify python directory

cd_to_labgui_dir

# note, that the script reached this point, StartLabGui.sh exists

start_script=($(cat StartLabGui.sh))

PYEXC=""
for i in "${start_script[@]}"; do
	if [[ "$i" == *python* ]]; then
		vers=`$i --version`
		if [[ "$vers" == "Python 3.7.3" ]]; then
			PYEXC="$i"
		fi
	fi
done

ARGS=('--quiet')

if [[ ! -z "$PYEXC" ]]; then
	ARGS+=("PYTHON=$PYEXC")
fi

cd_to_script_dir

# get rid of any source, so that the kernel package can be installed for sure

bash install_linux-gpib.sh --clean

bash install_linux-gpib.sh "${ARGS[@]}" || error_inst 3


echo "Installation complete :)"
