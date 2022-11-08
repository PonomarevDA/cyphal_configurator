#!/bin/bash

print_help () {
  echo "Usage: save_params.sh <node_id> <out_file>"
}

NODE_ID=$1
OUT_YAML_FILE=$2
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/base.sh

y rl $NODE_ID | y rb $NODE_ID > config.json | jq

if [ -z "$OUT_YAML_FILE" ]; then
    $SCRIPT_DIR/json_to_yaml.sh config.json
else
    $SCRIPT_DIR/json_to_yaml.sh config.json > $OUT_YAML_FILE
fi

rm config.json