#!/bin/bash

# User config
REPOSITORY_PATH="/catkin_ws/src/cyphal_tools"
REG_DATA_TYPE_PATH="$REPOSITORY_PATH/public_regulated_data_types/uavcan $REPOSITORY_PATH/public_regulated_data_types/reg/"
CONFIG_LOCAL_PATH="config/ardupilot_and_esc_registers.yaml"

# Common config
export YAKUT_COMPILE_OUTPUT="$REPOSITORY_PATH/compile_output"
export YAKUT_PATH="$YAKUT_COMPILE_OUTPUT"
export UAVCAN__CAN__IFACE='socketcan:slcan0'
export UAVCAN__CAN__MTU=8
export UAVCAN__NODE__ID=127


# Configure
yakut compile $REG_DATA_TYPE_PATH -O $YAKUT_COMPILE_OUTPUT
/catkin_ws/src/cyphal_tools/scripts/create_slcan_from_serial.sh $CYPHAL_DEV_PATH_SYMLINK
cat $REPOSITORY_PATH/$CONFIG_LOCAL_PATH | y rb
y cmd 42 restart -e
y cmd 116 restart -e
y cmd 123-125 restart -e
