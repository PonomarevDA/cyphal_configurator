#!/bin/bash
print_help () {
  echo "Usage: circuit_status/sub.sh <node_id>"
  exit
}

NODE_ID=$1
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
source $SCRIPT_DIR/setup_base.sh

crcr_vin_id=$(y r $NODE_ID uavcan.pub.crct.vin.id)
crcr_5v_id=$(y r $NODE_ID uavcan.pub.crct.5v.id)
crcr_temp_id=$(y r $NODE_ID uavcan.pub.crct.temp.id)

echo uavcan.pub.crct.vin.id = $crcr_vin_id
echo uavcan.pub.crct.5v.id = $crcr_5v_id
echo uavcan.pub.crct.temp.id = $crcr_temp_id

for i in {1..5000}; do
  if ((crcr_vin_id >= 1 && crcr_vin_id <= 6143)); then
    res=$(timeout 1 y sub -N 1 $crcr_vin_id:uavcan.si.sample.voltage.Scalar.1.0)
    echo Vin: $res | grep volt
  fi

  if ((crcr_5v_id >= 1 && crcr_5v_id <= 6143)); then
    res=$(timeout 1 y sub -N 1 $crcr_5v_id:uavcan.si.sample.voltage.Scalar.1.0)
    echo 5V: $res | grep volt
  fi

  if ((crcr_temp_id >= 1 && crcr_temp_id <= 6143)); then
    res=$(timeout 1 y sub -N 1 $crcr_temp_id:uavcan.si.sample.temperature.Scalar.1.0)
    echo Temperature: $res | grep kelvin
  fi
done
