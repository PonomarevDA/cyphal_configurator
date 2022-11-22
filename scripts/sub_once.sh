#!/bin/bash
print_help () {
  echo "Usage: sub_once.sh <node_id> <register_base>"
  exit
}

NODE_ID=$1
REGISTER_BASE=$2

if [ -z "$REGISTER_BASE" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/init.sh

PORT_ID=$(y r $NODE_ID $REGISTER_BASE.id)
DATA_TYPE=$(y r $NODE_ID $REGISTER_BASE.type | tr -d '"')

y sub -N 1 $PORT_ID:$DATA_TYPE