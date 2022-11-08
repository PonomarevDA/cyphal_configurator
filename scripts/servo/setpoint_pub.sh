#!/bin/bash
print_help () {
  echo "Usage: servo/setpoint_pub.sh <node_id>"
  exit
}

NODE_ID=$1
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
source $SCRIPT_DIR/setup_base.sh

SETPOINT_REGISTER_BASE=uavcan.sub.setpoint
SETPOINT_PORT_ID=$(y r $NODE_ID $SETPOINT_REGISTER_BASE.id)
SETPOINT_DATA_TYPE=$(y r $NODE_ID $SETPOINT_REGISTER_BASE.type | tr -d '"')

echo Setpoint Port id: $SETPOINT_PORT_ID
echo Setpoint Data type: $SETPOINT_DATA_TYPE
if ((SETPOINT_PORT_ID < 1 || SETPOINT_PORT_ID > 6143)); then
    exit -1
fi

y pub -T 0.05 $SETPOINT_PORT_ID:$SETPOINT_DATA_TYPE '[!$ "0.5-0.5*cos(t * pi * 0.3)", !$ "0.5-0.5*cos(t * pi * 0.3)", !$ "0.5-0.5*cos(t * pi * 0.3)", !$ "0.5-0.5*cos(t * pi * 0.3)"]'
