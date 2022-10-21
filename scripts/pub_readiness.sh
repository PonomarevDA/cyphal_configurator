#!/bin/bash
NODE_ID=51
REGISTER_BASE=uavcan.sub.readiness
PORT_ID=$(y r $NODE_ID $REGISTER_BASE.id)
DATA_TYPE=$(y r $NODE_ID $REGISTER_BASE.type | tr -d '"')

echo Port id: $PORT_ID
echo Data type: $DATA_TYPE

y pub -T 0.1 $PORT_ID:$DATA_TYPE 3