#!/bin/bash

print_help () {
  echo "Usage: sub.sh <node_id> <register_base>"
  exit
}

NODE_ID=$1
REGISTER_BASE=$2

if [ -z "$REGISTER_BASE" ]; then
    print_help
fi

PORT_ID=$(y r $NODE_ID $REGISTER_BASE.id)
DATA_TYPE=$(y r $NODE_ID $REGISTER_BASE.type | tr -d '"')
y sub $PORT_ID:$DATA_TYPE