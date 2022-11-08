#!/bin/bash
print_help () {
  echo "Usage: servo/feedback_sub.sh <node_id>"
  exit
}

NODE_ID=$1
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
$SCRIPT_DIR/sub.sh $NODE_ID uavcan.pub.feedback1
