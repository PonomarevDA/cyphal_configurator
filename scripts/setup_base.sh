#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPOSITORY_PATH="$SCRIPT_DIR/.."
REG_DATA_TYPE_PATH="$REPOSITORY_PATH/public_regulated_data_types/uavcan $REPOSITORY_PATH/public_regulated_data_types/reg/"
export YAKUT_COMPILE_OUTPUT="$REPOSITORY_PATH/compile_output"
export YAKUT_PATH="$YAKUT_COMPILE_OUTPUT"
export UAVCAN__CAN__IFACE='socketcan:slcan0'
export UAVCAN__CAN__MTU=8
export UAVCAN__NODE__ID=127
yakut compile $REG_DATA_TYPE_PATH -O $YAKUT_COMPILE_OUTPUT
$SCRIPT_DIR/create_slcan_from_serial.sh $CYPHAL_DEV_PATH_SYMLINK
