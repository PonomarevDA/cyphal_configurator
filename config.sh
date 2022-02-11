#!/bin/bash

cd "$(dirname "$0")"

# specify your pathes here:
export YAKUT_COMPILE_OUTPUT=compile_output
REG_DATA_TYPE_PATH_UAVCAN=public_regulated_data_types/uavcan
REG_DATA_TYPE_PATH_REG=public_regulated_data_types/reg

export YAKUT_PATH="$YAKUT_COMPILE_OUTPUT"
export REG_DATA_TYPE_PATH="$REG_DATA_TYPE_PATH_UAVCAN $REG_DATA_TYPE_PATH_REG"

export UAVCAN__CAN__IFACE='socketcan:slcan0'
export UAVCAN__CAN__MTU=8
export UAVCAN__NODE__ID=127

export ALLOCATION_TABLE_PATH=allocation_table.db

# Todo: identifiers should be defined dynamicly in future
export UAVCAN__PUB__NOTE_RESPONSE__ID=2341
export UAVCAN__PUB__SETPOINT__ID=2342
export UAVCAN__PUB__READINESS__ID=2343
export UAVCAN__SUB__ESC_HEARTBEAT__ID=2344
export UAVCAN__SUB__FEEDBACK__ID=2345
export UAVCAN__SUB__POWER__ID=2346
export UAVCAN__SUB__STATUS__ID=2347
export UAVCAN__SUB__DYNAMICS__ID=2348
