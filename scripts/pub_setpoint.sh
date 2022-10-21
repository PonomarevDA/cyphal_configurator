#!/bin/bash

NODE_ID=51
REGISTER_BASE=uavcan.sub.setpoint
PORT_ID=$(y r $NODE_ID $REGISTER_BASE.id)
DATA_TYPE=$(y r $NODE_ID $REGISTER_BASE.type | tr -d '"')

echo Port id: $PORT_ID
echo Data type: $DATA_TYPE

for repeat in 1 2 3 4 5 6 7 8 9 10; do
    for setpoint in {10..98..2}; do
        echo $setpoint
        y pub -N 1 -T 0.05 $PORT_ID:$DATA_TYPE "[0.$setpoint, 0.$setpoint, 0.$setpoint, 0.$setpoint]"
    done
    for setpoint in {98..10..-2}; do
        echo $setpoint
        y pub -N 1 -T 0.05 $PORT_ID:$DATA_TYPE "[0.$setpoint, 0.$setpoint, 0.$setpoint, 0.$setpoint]"
    done
done

# y pub -N 2 -T 0.1 $PORT_ID:$DATA_TYPE "[0.0, 0.0, 0.0, 0.0]"
# y pub -N 2 -T 0.1 $PORT_ID:$DATA_TYPE "[0.1, 0.0, 0.0, 0.0]"
# y pub -N 2 -T 0.1 $PORT_ID:$DATA_TYPE "[0.2, 0.0, 0.0, 0.0]"
# y pub -N 2 -T 0.1 $PORT_ID:$DATA_TYPE "[0.3, 0.0, 0.0, 0.0]"

# y pub -N 30 -T 0.1 $PORT_ID:$DATA_TYPE "[0.1, 0.0, 0.0, 0.0]"
# y pub -N 30 -T 0.1 $PORT_ID:$DATA_TYPE "[0.0, 0.1, 0.0, 0.0]"
# y pub -N 30 -T 0.1 $PORT_ID:$DATA_TYPE "[0.0, 0.0, 0.1, 0.0]"
# y pub -N 30 -T 0.1 $PORT_ID:$DATA_TYPE "[0.0, 0.0, 0.0, 0.1]"
