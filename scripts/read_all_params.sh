#!/bin/bash
NODE_ID=51
rl_raw=$(y rl $NODE_ID)
rl_clamped=${rl_raw:1:${#rl_raw}-2}
IFS=', ' read -r -a rl_parsed <<< "$rl_clamped"

for register_raw in "${rl_parsed[@]}"; do
    register=${register_raw:1:${#register_raw}-2}
    reg_value=$(y r $NODE_ID $register)
    echo $register : $reg_value
done
