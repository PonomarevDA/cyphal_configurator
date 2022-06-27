# Tools for configuration Ardupilot & kotleta20

Here we have few scripts to configure [kotleta20 esc](http://www.holybro.com/product/kotleta20/) and [Ardupilot](https://ardupilot.org/) autopilot via [Cyphal protocol](https://opencyphal.org/).

These scripts allow to automatically set registers values of autopilot and ESCs.

## Content
  - [1. Configuration](#1-configuration)
    - [1.1. Common interface](#11-common-interface)
    - [1.2. Kotleta20 specific interface](#12-kotleta20-specific-interface)
    - [1.3. Ardupilot specific interface](#13-ardupilot-specific-interface)
  - [2. Before start](#2-before-start)
  - [3. Usage](#3-usage)
    - [3.1. Configurator](#31-configurator)
    - [3.2. Esc panel](#32-esc-panel)

### 1.1. Common interface

Below you can see the table with basic any node must-have interface.

| № | Type                 |Port ID| Register name | Data type                  |
| - | -------------------- |:-----:|:-------------:|:--------------------------:|
| 1 | publisher            | 7509  | -             | [uavcan.node.Heartbeat.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/7509.Heartbeat.1.0.uavcan)  |
| 2 | publisher            | 7510  | -             | [uavcan.node.port.List.0.1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/port/7510.List.0.1.uavcan)  |
| 3 | RPC-service provider | 384   | -             | [uavcan.register.Access.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/register/384.Access.1.0.uavcan) |
| 4 | RPC-service provider | 385   | -             | [uavcan.register.List.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/register/385.List.1.0.uavcan)   |
| 5 | RPC-service provider | 430   | -             | [uavcan.node.GetInfo.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/430.GetInfo.1.0.uavcan)    |
| 6 | RPC-service provider | 435   | -             | [uavcan.node.ExecuteCommand](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/435.ExecuteCommand.1.0.uavcan) |

> These subjects doesn't require to have a specific register because their port id is fixed.

### 1.2. Kotleta20 specific interface

Kotleta20 has several registers. Here is the table with registers which describe the esc's interface.

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

> All port id in the table above are not fixed. The shown values are the default values from `config.sh` script.

### 1.3. Ardupilot specific interface

Ardupilot has several registers. Here is the table with registers which describe the Ardupilot's interface.

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

> All port id in the table above are not fixed. The shown values are the default values from `config.sh` script.


## 2. Before start

1. Connect CAN-sniffer (for example [this one](https://github.com/InnopolisAero/inno_uavcan_node_binaries/blob/master/doc/programmer_sniffer/README.md)) with autopilot & ESCs CAN bus network.
2. Configure environment variables by running `source config.sh`
3. Create SLCAN by running `./create_slcan_from_serial.sh`

After these steps you will be able to perform configuration.

## 3. Usage

### 3.1. Configurator

Algorithm of work:

1. Listen network for 3 seconds and collect all available nodes.
2. Subsequently set all nodes registers to the desired values using Register.List and Register.Access.
3. Send ExecuteCommand requests with load and reboot commands.

The script output when an Ardupilot autopilot is connected might be as in the picture below.

![configurator_autopilot](img/configurator_autopilot.png?raw=true "configurator_autopilot")

The script output when an kotleta20 esc is connected might be as in the picture below.

![configurator_kotleta20](img/configurator_kotleta20.png?raw=true "configurator_kotleta20")

### 3.2. Esc panel

The second one runs `Esc panel` with sliders which allow you to send a setpoint to ESCs to test them.

An example of the `Esc panel` is shown on the picture below.

![esc_panel](img/esc_panel.png?raw=true "esc_panel")
