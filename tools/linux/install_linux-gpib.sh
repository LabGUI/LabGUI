#!/bin/bash

# MUST BE RUN IN ROOT!
root_warning () {
	echo "You must run this as root!"
	exit 6
}
apt-get update -y || root_warning
apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget python3-dev python3-pyvisa-py python3-serial python3-usb python3-tk -y || exit 7


remove_args () {
	NARGS=()
	for var in $GARGS; do
		[[ "$var" != "$1" ]] && NARGS+=("$var")
		echo $var
	done
	GARGS="${NARGS[@]}"
}
# script actually starts

SCRIPT_PATH=`dirname $(readlink -f $0)`
cd_to_script_dir () {
	cd "$SCRIPT_PATH"
}

cd_to_script_dir


if [[ "$@" == *--clean* ]]; then
	rm linux-gpib.tar.gz
	rm linux-gpib*/ -R
	exit 0
fi


QUIET=false
GARGS="$@"
if [[ "$GARGS" == *--quiet* ]]; then
	QUIET=true
	remove_args "--quiet"
fi

if [[ $QUIET == true ]]; then
	read () {
		return 0
	}
fi

DEBUG=false
pause () {
	if [[ $QUIET == true ]]; then
		return 1
	fi
	read -p "Press any key to continue..."
	return 0
}



error_kernel () {
	cd ../../
	rm linux-gpib.tar.gz
	rm linux-gpib/ -R
	exit $1
}

error_user () {
	case "$1" in
		1)
			echo "Error configuring package"
			exit 1
			;;
		2)
			echo "Error running make"
			exit 2
			;;
		3)
			echo "Error running make install"
			exit 3
			;;
		*)
			echo "Unknown error"
			exit 255
			;;
	esac
}

error_pypath () {
	echo "Unable to check python version"
	exit 5
}

if [[ "$GARGS" != *PYTHON* ]]; then
	PYTH=$(which python3)
	if [[ $PYTH == "" ]]; then
		#echo "Unable to find python3 installation. Please specify with command-line argument: PYTHON=/path/to/python3/executable"
		#exit 255
		$PYEXC=""
		read -p "Unable to find python3 installation. Please specify the absolute path of the python3 executable: " PYEXC
		if [[ -z "$PYEXC" ]]; then
			echo "Invalid path"
			exit 254
		elif [[ ! -x "$PYEXC" ]]; then
			echo "Invalid file"
			exit 255
		else
			PYTH="$PYEXC"
			$PYTH --version || error_pypath
			ARGS=($GARGS)
			ARGS+=("PYTHON=$PYTH")
			GARGS="${ARGS[@]}"
		fi
	else
		PYEXC=""
		read -p "Select python3 installation to install to [$PYTH]: " PYEXC
		echo "$PYEXC"
		pause
		if [[ -z "$PYEXC" ]]; then
			PYEXC="$PYTH"
		elif [[ ! -x "$PYEXC" ]]; then
			echo "Invalid file"
			exit 255
		fi
		PYTH="$PYEXC"
		$PYTH --version || error_pypath
		ARGS=($GARGS)
		ARGS+=("PYTHON=$PYTH")
		GARGS="${ARGS[@]}"
	fi
else
	PYTH=""
	for var in $GARGS; do
		if [[ "$var" == PYTHON=* ]]; then
			PYTH="${var:7}"
		fi
	done
	echo $GARGS
	if [[ -z "$PYTH" ]]; then
		echo "Invalid path"
		exit 254
	elif [[ ! -x "$PYTH" ]]; then
		echo "Invalid file"
		exit 255
	fi
	$PYTH --version || error_pypath
	ARGS=($GARGS)
fi


# arguments passable are PYTHON=/path/to/python

if [[ ! -f ./linux-gpib.tar.gz || ! -d $(echo ./linux-gpib*/)  ]]; then

	echo "Installing linux-gpib Kernel stuff"
	pause

	wget sourceforge.net/projects/linux-gpib/files/latest/download -O linux-gpib.tar.gz
	
	if [[ "$@" == *--download* ]]; then
		exit 0
	fi


	tar -xzf linux-gpib.tar.gz
	

	cd linux-gpib*/

	# DO KERNEL STUFF HERE
	kernels=( $(ls /lib/modules) )
	echo "Installing linux kernel headers"
	for i in "${kernels[@]}"; do
		apt-get install "linux-headers-$i" -y
	done
	
	tar -xzf linux-gpib-kernel*.tar.gz

	cd linux-gpib-kernel*/

	echo "Configuring kernel packages"
	
	$DEBUG || ./configure || error_kernel 1

	$DEBUG || make || error_kernel 2

	$DEBUG || make install || error_kernel 3

	echo "Installed Kernel Drivers"

	cd_to_script_dir
else

	cd_to_script_dir
fi

# At this point, in script directory, so cd to linux-gpib

cd linux-gpib*/

# DO USER STUFF

tar -xzf linux-gpib-user*.tar.gz

cd linux-gpib-user*/

# configure
echo "Python executable is $PYTH"
echo "Configuring with parameters --sysconfdir=/etc $GARGS"
pause

$DEBUG || ./configure --sysconfdir=/etc "$GARGS" || error_user 1

$DEBUG || make || error_user 2

$DEBUG || make install || error_user 3

## since it is extremely likely that make messed up setup.py installation for non-standard lib, the following will fix it
cd language/python
$PYTH setup.py install && echo "Install complete" || echo "Error installing python module"

cd_to_script_dir

echo "Finished installing linux-gpib. Make sure to modprobe the correct driver and modify /etc/gpib.conf"

echo "Example gpib.conf for ni-devices called gpib_ni_example.conf"

pause && more ./gpib_ni_example.conf

resp=y
read -p "Copy gpib_ni_example.conf to /etc/gpib.conf? [yN]:" resp

if [[ "$resp" == "y" ]]; then
	if [[ -f /etc/gpib.conf ]]; then
		backup=/etc/gpib.conf.orig
		i=0
		while [[ -f "$backup.$i" ]]; do
			i=$[$i+1]
		done
		back_file="$backup.$i"
		echo "backing up /etc/gpib.conf to $back_file"
		mv /etc/gpib.conf $back_file
	fi

	cp ./gpib_ni_example.conf /etc/gpib.conf

	echo "Refreshing gpib configuration"
	gpib_config
fi

echo "Installation complete :)"


