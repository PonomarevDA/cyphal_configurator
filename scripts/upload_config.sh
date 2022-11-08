#!/bin/bash
print_help () {
  echo "Usage: upload_config.sh <node_id> <config_dir>"
  exit
}

NODE_ID=$1
CONFIG_DIR=$2

if [ -z "$CONFIG_DIR" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/base.sh

cat $CONFIG_DIR | y rb

y cmd $NODE_ID 65530 -e
y cmd $NODE_ID restart -e
