#!/bin/bash
print_help () {
  echo "Usage: gps/sub.sh <port_id>"
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


# 1. point
LAT="0.69833590432"   # 40.0117° N
LON="-1.56814691699"  # -89.8482° W
ALT=0.5
DEG_TO_RAD=0.017453292519943295

DATA_TYPE=reg.udral.physics.kinematics.geodetic.PointStateVarTs.0.1
PORT_ID=$(( $BASE_PORT_ID + 0))
VALUE="{value: {position: {value: {latitude: $LAT, longitude: $LON, altitude: {meter: $ALT}}}}}"
yakut_pub_in_bg

# 2. sats
DATA_TYPE=uavcan.primitive.scalar.Integer16
PORT_ID=$(( $BASE_PORT_ID + 1))
VALUE="{value: !$ \"15-3*cos(t * pi * 0.08)\"}"
yakut_pub_in_bg

# 3. status (3D Fix)
DATA_TYPE=uavcan.primitive.scalar.Integer16
PORT_ID=$(( $BASE_PORT_ID + 2))
VALUE="{value: 3}"
yakut_pub_in_bg

# 4. pdop
DATA_TYPE=uavcan.primitive.scalar.Integer16
PORT_ID=$(( $BASE_PORT_ID + 3))
VALUE="{value: !$ \"3+2*cos(t * pi * 0.08)\"}"
yakut_pub_in_bg

sleep infinity
