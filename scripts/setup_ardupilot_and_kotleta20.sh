#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/init.sh

CONFIG_LOCAL_PATH="config/ardupilot_and_kotleta20.yaml"
cat $SCRIPT_DIR/../$CONFIG_LOCAL_PATH | y rb

y cmd 42 restart -e
y cmd 50-53 65530 -e
y cmd 50-53 restart -e
