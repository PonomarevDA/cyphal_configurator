#!/bin/bash
print_help () {
  echo "Usage: servo/readiness_pub.sh <node_id>"
  exit
}

NODE_ID=$1
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/../setup_base.sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
${SCRIPT_DIR}/readiness_pub.sh $NODE_ID &
sleep 2
${SCRIPT_DIR}/feedback_sub.sh $NODE_ID &
sleep 2
${SCRIPT_DIR}/setpoint_pub.sh $NODE_ID