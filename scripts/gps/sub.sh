#!/bin/bash
print_help () {
  echo "Usage: gps/sub.sh <node_id>"
  exit
}

NODE_ID=$1
if [ -z "$NODE_ID" ]; then
    print_help
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
source $SCRIPT_DIR/base.sh

pdop_id=$(y r $NODE_ID uavcan.pub.gps.pdop.id)
point_id=$(y r $NODE_ID uavcan.pub.gps.point.id)
sats_id=$(y r $NODE_ID uavcan.pub.gps.sats.id)
status_id=$(y r $NODE_ID uavcan.pub.gps.status.id)
# yaw_id=$(y r $NODE_ID uavcan.pub.gps.yaw.id)

for i in {1..5000}; do
    y sub -N 1 $pdop_id:uavcan.primitive.scalar.Integer16
    y sub -N 1 $point_id:reg.udral.physics.kinematics.geodetic.PointStateVarTs
    y sub -N 1 $sats_id:uavcan.primitive.scalar.Integer16
    # y sub -N 1 $status_id:uavcan.primitive.scalar.Integer16
    # y sub -N 1 $yaw_id:uavcan.si.sample.angle.Scalar
done



