#!/bin/bash

sudo apt-get install -y can-utils socat net-tools udev iproute2
sudo apt-get install -y python3 python3-dev

python3 -m pip install --upgrade pip
python3 -m pip install cython scipy pyuavcan yakut pyqt5

