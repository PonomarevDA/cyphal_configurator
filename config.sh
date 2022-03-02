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

# Server node port id. Common for all ESC:
export UAVCAN__PUB__NOTE_RESPONSE__ID=2341
export UAVCAN__PUB__SETPOINT__ID=2342
export UAVCAN__PUB__READINESS__ID=2343

# Server node port id. ESC #1:
export UAVCAN__SUB__ESC_HEARTBEAT_1__ID=2374
export UAVCAN__SUB__FEEDBACK_1__ID=2375
export UAVCAN__SUB__POWER_1__ID=2376
export UAVCAN__SUB__STATUS_1__ID=2377
export UAVCAN__SUB__DYNAMICS_1__ID=2378

# Server node port id. ESC #2:
export UAVCAN__SUB__ESC_HEARTBEAT_2__ID=2354
export UAVCAN__SUB__FEEDBACK_2__ID=2355
export UAVCAN__SUB__POWER_2__ID=2356
export UAVCAN__SUB__STATUS_2__ID=2357
export UAVCAN__SUB__DYNAMICS_2__ID=2358

# Server node port id. ESC #3:
export UAVCAN__SUB__ESC_HEARTBEAT_3__ID=2364
export UAVCAN__SUB__FEEDBACK_3__ID=2365
export UAVCAN__SUB__POWER_3__ID=2366
export UAVCAN__SUB__STATUS_3__ID=2367
export UAVCAN__SUB__DYNAMICS_3__ID=2368

# Server node port id. ESC #4:
export UAVCAN__SUB__ESC_HEARTBEAT_4__ID=2344
export UAVCAN__SUB__FEEDBACK_4__ID=2345
export UAVCAN__SUB__POWER_4__ID=2346
export UAVCAN__SUB__STATUS_4__ID=2347
export UAVCAN__SUB__DYNAMICS_4__ID=2348

# Kotleta mock port id:
export UAVCAN__SUB__NOTE_RESPONSE__ID=2341
export UAVCAN__SUB__SETPOINT__ID=2342
export UAVCAN__SUB__READINESS__ID=2343
export UAVCAN__PUB__ESC_HEARTBEAT__ID=2344
export UAVCAN__PUB__FEEDBACK__ID=2345
export UAVCAN__PUB__POWER__ID=2346
export UAVCAN__PUB__STATUS__ID=2347
export UAVCAN__PUB__DYNAMICS__ID=2348
