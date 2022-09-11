#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$SCRIPT_DIR/setup_base.sh

CONFIG_LOCAL_PATH="config/ardupilot_and_esc_registers.yaml"
cat $SCRIPT_DIR/../$CONFIG_LOCAL_PATH | y rb

y cmd 42 restart -e
y cmd 116 restart -e
y cmd 123-125 restart -e
