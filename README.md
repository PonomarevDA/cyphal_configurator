# Ardupilot & kotleta20 configuration

Here we have few scripts to configure [kotleta20 esc](http://www.holybro.com/product/kotleta20/) and [Ardupilot](https://ardupilot.org/) autopilot via [Cyphal protocol](https://opencyphal.org/).

These scripts allow to automatically set registers values of autopilot and ESCs.

## Content
  - [1. Interface description](#1-interface-description)
    - [1.1. Common interface](#11-common-interface)
    - [1.2. Kotleta20 specific interface](#12-kotleta20-specific-interface)
    - [1.3. Ardupilot specific interface](#13-ardupilot-specific-interface)
  - [2. Before start](#2-before-start)
  - [3. Usage](#3-usage)
    - [3.1. Manual usage](#31-manual-usage)
    - [3.2. Docker usage](#32-docker-usage)

## 1. Interface description

The goal of configuration is to set the desired registers values of autopilot and ESCs. This process is defined by the device interfaces. Let's study them below.

> This section is just a reminder page. Read it only if you are going to develop your own configuration.

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

> All port id in the table above are not fixed. The shown values are the default values from [registers.yaml](config/registers.yaml) file. If you want to customize the configuration, edit this yaml file.

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

> All port id in the table above are not fixed. The shown values are the default values from [registers.yaml](config/registers.yaml) script. If you want to customize the configuration, edit this yaml file.


## 2. Before start

You need to connect CAN-sniffer (for example [this one](https://github.com/InnopolisAero/inno_uavcan_node_binaries/blob/master/doc/programmer_sniffer/README.md)) with autopilot & ESCs CAN bus network.

An example of connection is shown below.

> It is expected that your ESC has an external power supply.

> It's not recommended to perform configuration when your motors are equipped with propellers.

![connection](img/connection.png?raw=true "connection")


## 3. Usage

There are 2 options. You can either configure from docker or install everything on your environment and run it.

### 3.1. Manual usage

Run following commands to start the configuration:

```bash
git clone https://github.com/PonomarevDA/kotleta_tools --recursive
git submodule update --init --recursive
cd kotleta_tools
./scripts/install.sh
./scripts/setup.sh
```

The `setup.sh` script:

1. Configure all required environment variables
2. Compile DSDL
3. Create SLCAN
4. Configure devices registers
5. Reboot devices

### 3.2. Docker usage

Run following commands to start the configuration:

```bash
git clone https://github.com/PonomarevDA/kotleta_tools --recursive
git submodule update --init --recursive
cd kotleta_tools
./scripts/docker.sh build
./scripts/docker.sh interactive
./scripts/setup.sh
```

All the same, but everything is already installed in the docker.
