#!/bin/bash
print_help () {
  echo "Usage: baro/pub.sh <port_id>"
  exit
}

function kill_all_process() {
  for process_pid in "${child_processes_pids[@]}"; do
    kill $process_pid
  done
}

function yakut_pub_in_bg() {
  echo "y pub $PORT_ID:$DATA_TYPE $VALUE"
  yakut pub $PORT_ID:$DATA_TYPE "$VALUE" &
  process_pid=$!
  child_processes_pids+=($process_pid)
}


child_processes_pids=()
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
source $SCRIPT_DIR/init.sh
trap kill_all_process INT


BASE_PORT_ID=$1
if [ -z "$BASE_PORT_ID" ]; then
  print_help
fi


# 1. pressure
DATA_TYPE=uavcan.si.sample.pressure.Scalar.1.0
PORT_ID=$(( $BASE_PORT_ID + 0))
VALUE="{pascal: 101234.4321}"
yakut_pub_in_bg

# 2. temperature
DATA_TYPE=uavcan.si.sample.temperature.Scalar.1.0
PORT_ID=$(( $BASE_PORT_ID + 1))
VALUE="{kelvin: 300.0}"
yakut_pub_in_bg

sleep infinity
