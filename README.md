# Cyphal configurator

This repository is just a collection of config files and scripts based on [yakut](https://github.com/OpenCyphal/yakut) to configure the following [Cyphal](https://opencyphal.org/) applications:

- Quadcopter based on [Cyphal Ardupilot](https://github.com/PonomarevDA/ardupilot) with [4 Cyphal kotleta20 esc](http://www.holybro.com/product/kotleta20/),
- Quadcopter based on [Cyphal Ardupilot](https://github.com/PonomarevDA/ardupilot) with [2 Cyphal micro nodes](https://raccoonlabdev.github.io/docs/guide/can_pwm/),
- Quadcopter based on [Cyphal Ardupilot](https://github.com/PonomarevDA/ardupilot) with [Mini v2 node](https://raccoonlabdev.github.io/docs/guide/can_pwm/) and [Cyphal GPS](https://raccoonlabdev.github.io/docs/guide/gps_mag_baro/),
- Quadcopter [Cyphal HITL simulation](https://github.com/InnopolisAero/innopolis_vtol_dynamics) based on [Cyphal HITL Ardupilot](https://github.com/PonomarevDA/ardupilot/tree/pr-uavcan-v1-hitl).

But it might be also used as an example/template of configuration for other applications.

It automatically:
1. Configure all required environment variables
2. Compile DSDL based on public regulated data types
3. Create SLCAN based on CAN sniffer
4. Configure devices registers
5. Reboot devices (if they support this feature)

## 1. Before start

You need to connect CAN-sniffer (for example [this one](https://innopolisaero.github.io/inno_uavcan_node_binaries/guide/programmer_sniffer.html#uavcan-sniffer-and-programmer)) with CAN bus network.

An example of connection is shown below.

![connection](img/connection.png?raw=true "connection")


## 2. Usage

> It is expected that all your nodes already have allocated node-ID. If they are not, run a plug-and-play node-ID allocator  before continuing. Check `yakut` documentation. 

There are 2 options. You can either configure from docker or install everything on your environment and run it.

**2.1. Manual usage**

Run the following commands to start the configuration:

```bash
git clone https://github.com/PonomarevDA/cyphal_configurator --recursive
git submodule update --init --recursive
cd cyphal_configurator
./scripts/ubuntu_22_04.sh
source scripts/init.sh
```

**2.2. Docker usage**

Run the following commands to start the configuration:

```bash
git clone https://github.com/PonomarevDA/cyphal_configurator --recursive
git submodule update --init --recursive
cd cyphal_configurator
./docker/docker.sh b
./docker/docker.sh i
source scripts/init.sh
```

All the same, but everything is already installed in the docker.


## 3. Configurable registers

Configurable registers are listed in the [config](config/) directory.

<details>
  <summary>(Cheat sheet) Click here to expand the devices interface.</summary>

**3.1. Common interface**

Below you can see the table with basic any node must-have interface.

| № | Type                 |Port ID| Register name | Data type                  |
| - | -------------------- |:-----:|:-------------:|:--------------------------:|
| 1 | publisher            | 7509  | -             | [uavcan.node.Heartbeat.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/7509.Heartbeat.1.0.dsdl)  |
| 2 | publisher            | 7510  | -             | [uavcan.node.port.List.0.1](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/port/7510.List.0.1.dsdl)  |
| 3 | RPC-service provider | 384   | -             | [uavcan.register.Access.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/register/384.Access.1.0.dsdl) |
| 4 | RPC-service provider | 385   | -             | [uavcan.register.List.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/register/385.List.1.0.dsdl)   |
| 5 | RPC-service provider | 430   | -             | [uavcan.node.GetInfo.1.0](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/430.GetInfo.1.0.dsdl)    |
| 6 | RPC-service provider | 435   | -             | [uavcan.node.ExecuteCommand](https://github.com/UAVCAN/public_regulated_data_types/blob/master/uavcan/node/435.ExecuteCommand.1.0.dsdl) |

> These subjects doesn't require to have a specific register because their port id is fixed.

**3.2. Ardupilot specific interface**

Ardupilot has several registers. Here is the table with registers which describe the Ardupilot's interface.

| № | Type                 |Port ID| Register name | Data type                                        |
| - | -------------------- |:-----:|:-------------:|:------------------------------------------------:|
| 1 | publisher            | 2341  | note_response | [reg.udral.physics.acoustics.Note_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/acoustics/Note.0.1.dsdl)             |
| 2 | publisher            | 2342  | setpoint      | [reg.udral.service.actuator.common.sp.Scalar_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/sp/Vector4.0.1.dsdl)  |
| 3 | publisher            | 2343  | readiness     | [reg.udral.service.common.Readiness_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/common/Readiness.0.1.dsdl)           |
| 4 | subscriber           | -     | esc_heartbeat | [reg.udral.service.common.Heartbeat_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/common/Heartbeat.0.1.dsdl)           |
| 5 | subscriber           | [2345, 2355, 2365, 2375] | feedback      | [reg.udral.service.actuator.common.Feedback_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Feedback.0.1.dsdl)   |
| 6 | subscriber           | [2346, 2356, 2366, 2376]  | power         | [reg.udral.physics.electricity.PowerTs_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/electricity/PowerTs.0.1.dsdl)        |
| 7 | subscriber           | [2347, 2357, 2367, 2377]  | status        | [reg.udral.service.actuator.common.Status_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Status.0.1.dsdl)     |
| 8 | subscriber           | [2348, 2358, 2368, 2378]  | dynamics      | [reg.udral.physics.dynamics.rotation.PlanarTs_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/dynamics/rotation/PlanarTs.0.1.dsdl) |
| 9 | subscriber            | 2400  | accel | [uavcan.si.sample.acceleration.Vector3.1.0](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/uavcan/si/sample/acceleration/Vector3.1.0.dsdl)             |
| 10 | subscriber            | 2401  | gyro | [uavcan.si.sample.angular_velocity.Vector3.1.0](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/uavcan/si/sample/angular_velocity/Vector3.1.0.dsdl)             |
| 11 | subscriber            | 2402  | mag | [uavcan.si.sample.magnetic_field_strength.Vector3.1.0](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/uavcan/si/sample/magnetic_field_strength/Vector3.1.0.dsdl)             |
| 12 | subscriber            | 2403  | baro.temp | [uavcan.si.sample.temperature.Scalar.1.0](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/uavcan/si/sample/angle/Scalar.1.0.dsdl)             |
| 13 | subscriber            | 2404  | baro.pres | [uavcan.si.sample.pressure.Scalar.1.0](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/uavcan/si/sample/angle/Scalar.1.0.dsdl)             |
| 14 | subscriber            | 2405  | gps.yaw | [uavcan.si.sample.angle.Scalar](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/uavcan/si/sample/angle/Scalar.1.0.dsdl)             |
| 15 | subscriber            | 2406  | gps.point | [reg.udral.physics.kinematics.geodetic.PointStateVarTs.0.1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/kinematics/geodetic/PointStateVarTs.0.1.dsdl)             |


> All port id in the table above are not fixed. The shown values are the default values from [config](config/) directory. If you want to customize the configuration, edit this yaml file.

**3.3. Kotleta20 specific interface**

Kotleta20 has several registers. Here is the table with registers which describe the esc's interface.

| № | Type                 |Port ID| Register name | Data type                                        |
| - | -------------------- |:-----:|:-------------:|:------------------------------------------------:|
| 1 | subscriber           | 2341  | note_response | [reg.udral.physics.acoustics.Note_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/acoustics/Note.0.1.dsdl)             |
| 2 | subscriber           | 2342  | setpoint      | [reg.udral.service.actuator.common.sp.Scalar_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/sp/Vector4.0.1.dsdl)  |
| 3 | subscriber           | 2343  | readiness     | [reg.udral.service.common.Readiness_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/common/Readiness.0.1.dsdl)           |
| 4 | publisher            | -     | esc_heartbeat | [reg.udral.service.common.Heartbeat_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/common/Heartbeat.0.1.dsdl)           |
| 5 | publisher            | 2345  | feedback      | [reg.udral.service.actuator.common.Feedback_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Feedback.0.1.dsdl)   |
| 6 | publisher            | 2346  | power         | [reg.udral.physics.electricity.PowerTs_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/electricity/PowerTs.0.1.dsdl)        |
| 7 | publisher            | 2347  | status        | [reg.udral.service.actuator.common.Status_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Status.0.1.dsdl)     |
| 8 | publisher            | 2348  | dynamics      | [reg.udral.physics.dynamics.rotation.PlanarTs_0_1](https://github.com/OpenCyphal/public_regulated_data_types/blob/master/reg/udral/physics/dynamics/rotation/PlanarTs.0.1.dsdl) |

> All port id in the table above are not fixed. The shown values are the default values from [config](config/) directory. If you want to customize the configuration, edit this yaml file.

</details>

## 4. Flight examples

Few flight example videos are listed below:
- https://youtu.be/7vLIsBtI9Hs
- https://youtu.be/FE_kxwhicWM
