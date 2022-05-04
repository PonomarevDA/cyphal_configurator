#!/bin/bash

print_help() {
   echo "Wrapper under yakut.
It automatically configurate required registers.

https://https://github.com/PonomarevDA/kotleta_tools

Usage: run.sh <command>

Commands:
accomodate      Call yakut accomodate
compile         Call yakut compile
server          Scans network to check online nodes, perform reading and
                writing to their registers and save and reboot device if
                write operation is successfull
gui_esc_panel   The same as server + gui
mock_vehicle    Mock vehicle that has 4 esc nodes
help            Print this message and exit"
}

configurate() {
    source config.sh
    if [[ ! $(ifconfig | grep slcan0) ]]; then
        ./create_slcan_from_serial.sh
    fi
}

accomodate() {
    configurate
    export UAVCAN__NODE__ID=$(yakut accommodate)
}

compile() {
    configurate
    yakut compile $REG_DATA_TYPE_PATH -O $YAKUT_COMPILE_OUTPUT
}

pnp() {
    configurate
    yakut file-server --plug-and-play=$ALLOCATION_TABLE_PATH
}

gui_esc_panel() {
    configurate
    python3.7 gui_esc_panel.py
}

mock_vehicle() {
    configurate
    python3.7 mock_vehicle.py
}

server() {
    configurate
    python3.7 server.py
}

cd "$(dirname "$0")"/scripts
set -e

if [ "$1" = "accomodate" ]; then
    accomodate
elif [ "$1" = "compile" ]; then
    compile
elif [ "$1" = "server" ]; then
    server
elif [ "$1" = "gui_esc_panel" ]; then
    gui_esc_panel
elif [ "$1" = "mock_vehicle" ]; then
    mock_vehicle
else
    print_help
fi
