#!/bin/bash

sudo apt-get install python3.7 python3.7-dev

python3.7 -m pip install --upgrade pip

# necessary for main libraries
python3.7 -m pip install cython scipy

# main libraries
python3.7 -m pip install pyuavcan yakut

# esc_panel
python3.7 -m pip install pyqt5

