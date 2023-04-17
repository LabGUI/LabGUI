#!/bin/bash

# cd into proper directory and do stuff
if [[ -d /python-build-stuff-zac ]]; then
	rm /python-build-stuff-labgui -R
fi
mkdir /python-build-stuff-labgui
cd /python-build-stuff-labgui

# install required build stuff

sudo apt-get update -y
sudo apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget -y

# now to download/extract python stuff

wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz

tar -xJf Python-3.7.3.tar.xz

# Curl/GNU Tar code (not full support)
#curl -O https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
#
#tar -xf Python-3.7.3.tar.xz

cd Python-3.7.3

# configure and make

./configure --enable-optimizations

make -j $(nproc)

# this will build it as python3.7

make altinstall

# this will build it as python3
#make install

python3.7 --version

apt-get install python3-pip -y

pip3 install --upgrade pip

cd /

rm /python-build-stuff-labgui -R

echo "Installation complete :)"
