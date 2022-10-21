#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.vin
$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.5v
$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.temp

$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.vin
$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.5v
$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.temp

$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.vin
$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.5v
$SCRIPT_DIR/sub_once.sh uavcan.pub.crct.temp
