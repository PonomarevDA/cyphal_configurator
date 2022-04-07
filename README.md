# Tools for playing with kotleta

Here we have few scripts to interract with [kotleta20 esc](http://www.holybro.com/product/kotleta20/) and Ardupilot autopilot via UAVCAN v1 protocol (as kotleta20 mocks).

These scripts allow to automatically set registers values of autopilot and ESCs.

## Before start

It is expected that you are using CAN-sniffer device such as [UAVCAN sniffer and programmer](https://github.com/InnopolisAero/inno_uavcan_node_binaries/blob/master/doc/programmer_sniffer/README.md). You need to connect it to your PC.

After connection, you should create SLCAN and configure environment variables using following scripts:

```bash
./create_slcan_from_serial.sh
source config.sh
```


## Interracting with ESCs

Here we have 2 scripts.

You may eirher run `server.py` script or `gui_esc_panel.py`.

The first script scans network to check online nodes, perform reading and writing to their registers and save and reboot device if write operation is successfull.

Tipically, the output is following:

![kotleta_registers](img/kotleta_registers.png?raw=true "kotleta_registers")


The second one do the same, but additionally run `Esc panel` with sliders which allow you to send a setpoint to ESCs to test them.

An example of the `Esc panel` is shown on the picture below.

![esc_panel](img/esc_panel.png?raw=true "esc_panel")

## Mocks

...


## Registers values

**Basic any node must-have interface**

| № | Type                 |Port ID| Register name | Data type                  |
| - | -------------------- |:-----:|:-------------:|:--------------------------:|
| 1 | publisher            | 7509  | -             | [uavcan.node.Heartbeat.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/7509.Heartbeat.1.0.uavcan)  |
| 2 | publisher            | 7510  | -             | [uavcan.node.port.List.0.1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/port/7510.List.0.1.uavcan)  |
| 3 | RPC-service provider | 384   | -             | [uavcan.register.Access.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/register/384.Access.1.0.uavcan) |
| 4 | RPC-service provider | 385   | -             | [uavcan.register.List.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/register/385.List.1.0.uavcan)   |
| 5 | RPC-service provider | 430   | -             | [uavcan.node.GetInfo.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/430.GetInfo.1.0.uavcan)    |
| 6 | RPC-service provider | 435   | -             | [uavcan.node.ExecuteCommand](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/435.ExecuteCommand.1.0.uavcan) |

**Kotleta's specific interface**

| № | Type                 |Port ID| Register name | Data type                                        |
| - | -------------------- |:-----:|:-------------:|:------------------------------------------------:|
| 1 | subscriber           | 2341  | note_response | [reg.udral.physics.acoustics.Note_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/physics/acoustics/Note.0.1.uavcan)             |
| 2 | subscriber           | 2342  | setpoint      | [reg.udral.service.actuator.common.sp.Scalar_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/sp/Vector4.0.1.uavcan)  |
| 3 | subscriber           | 2343  | readiness     | [reg.udral.service.common.Readiness_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/common/Readiness.0.1.uavcan)           |
| 4 | publisher            | -     | esc_heartbeat | [reg.udral.service.common.Heartbeat_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/common/Heartbeat.0.1.uavcan)           |
| 5 | publisher            | 2345  | feedback      | [reg.udral.service.actuator.common.Feedback_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Feedback.0.1.uavcan)   |
| 6 | publisher            | 2346  | power         | [reg.udral.physics.electricity.PowerTs_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/physics/electricity/PowerTs.0.1.uavcan)        |
| 7 | publisher            | 2347  | status        | [reg.udral.service.actuator.common.Status_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Status.0.1.uavcan)     |
| 8 | publisher            | 2348  | dynamics      | [reg.udral.physics.dynamics.rotation.PlanarTs_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/physics/dynamics/rotation/PlanarTs.0.1.uavcan) |

**Autopilot's specific interface**

The node id is 42.

| № | Type                 |Port ID| Register name | Data type                                        |
| - | -------------------- |:-----:|:-------------:|:------------------------------------------------:|
| 1 | publisher            | 2341  | note_response | [reg.udral.physics.acoustics.Note_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/physics/acoustics/Note.0.1.uavcan)             |
| 2 | publisher            | 2342  | setpoint      | [reg.udral.service.actuator.common.sp.Scalar_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/sp/Vector4.0.1.uavcan)  |
| 3 | publisher            | 2343  | readiness     | [reg.udral.service.common.Readiness_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/common/Readiness.0.1.uavcan)           |
| 4 | subscriber           | -     | esc_heartbeat | [reg.udral.service.common.Heartbeat_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/common/Heartbeat.0.1.uavcan)           |
| 5 | subscriber           | [2345, 2355, 2365, 2375] | feedback      | [reg.udral.service.actuator.common.Feedback_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Feedback.0.1.uavcan)   |
| 6 | subscriber           | [2346, 2356, 2366, 2376]  | power         | [reg.udral.physics.electricity.PowerTs_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/physics/electricity/PowerTs.0.1.uavcan)        |
| 7 | subscriber           | [2347, 2357, 2367, 2377]  | status        | [reg.udral.service.actuator.common.Status_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Status.0.1.uavcan)     |
| 8 | subscriber           | [2348, 2358, 2368, 2378]  | dynamics      | [reg.udral.physics.dynamics.rotation.PlanarTs_0_1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/physics/dynamics/rotation/PlanarTs.0.1.uavcan) |
