#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/setup_base.sh

CONFIG_LOCAL_PATH="config/ardupilot_hitl_registers.yaml"
cat $SCRIPT_DIR/../$CONFIG_LOCAL_PATH | y rb

y cmd 42 restart -e
