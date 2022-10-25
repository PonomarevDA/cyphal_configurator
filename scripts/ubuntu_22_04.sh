#!/bin/bash

apt-get install -y can-utils socat net-tools udev iproute2
apt-get install -y python3 python3-pip python3-dev jq python3-scipy

python3 -m pip install --upgrade pip
python3 -m pip install cython pyuavcan yakut pyqt5

