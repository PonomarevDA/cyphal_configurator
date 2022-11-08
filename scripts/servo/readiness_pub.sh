#!/bin/bash
print_help () {
  echo "Usage: servo/readiness_pub.sh <node_id>"
  exit
}

NODE_ID=$1
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
source $SCRIPT_DIR/setup_base.sh

READINESS_REGISTER_BASE=uavcan.sub.readiness
READINESS_PORT_ID=$(y r $NODE_ID $READINESS_REGISTER_BASE.id)
READINESS_DATA_TYPE=$(y r $NODE_ID $READINESS_REGISTER_BASE.type | tr -d '"')

echo Readiness Port id: $READINESS_PORT_ID
echo Readiness Data type: $READINESS_DATA_TYPE
if ((READINESS_PORT_ID < 1 || READINESS_PORT_ID > 6143)); then
    exit -1
fi

y pub -T 0.1 $READINESS_PORT_ID:$READINESS_DATA_TYPE 3