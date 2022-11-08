#!/bin/bash
NODE_ID=71
CONFIG_NAME="config/gps_mag_baro_registers.yaml"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..

$SCRIPT_DIR/upload_config.sh $NODE_ID $CONFIG_NAME
