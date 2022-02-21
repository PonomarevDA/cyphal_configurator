# Tools for playing with kotleta

![kotleta_registers](img/kotleta_registers.png?raw=true "kotleta_registers")

**Basic any node must-have interface**

| № | Type                 |Port ID| Register name | Data type                  |
| - | -------------------- |:-----:|:-------------:|:--------------------------:|
| 1 | publisher            | 7509  | -             | uavcan.node.Heartbeat.1.0  |
| 2 | publisher            | 7510  | -             | uavcan.node.port.List.0.1  |
| 3 | RPC-service provider | 384   | -             | uavcan.register.Access.1.0 |
| 4 | RPC-service provider | 385   | -             | uavcan.register.List.1.0   |
| 5 | RPC-service provider | 430   | -             | uavcan.node.GetInfo.1.0    |
| 6 | RPC-service provider | 435   | -             | uavcan.node.ExecuteCommand |

**Kotleta's specific interface**

| № | Type                 |Port ID| Register name | Data type                                        |
| - | -------------------- |:-----:|:-------------:|:------------------------------------------------:|
| 1 | subscriber           | 2341  | note_response | reg.udral.physics.acoustics.Note_0_1             |
| 2 | subscriber           | 2342  | setpoint      | reg.udral.service.actuator.common.sp.Scalar_0_1  |
| 3 | subscriber           | 2343  | readiness     | reg.udral.service.common.Readiness_0_1           |
| 4 | publisher            | -     | esc_heartbeat | reg.udral.service.common.Heartbeat_0_1           |
| 5 | publisher            | 2345  | feedback      | reg.udral.service.actuator.common.Feedback_0_1   |
| 6 | publisher            | 2346  | power         | reg.udral.physics.electricity.PowerTs_0_1        |
| 7 | publisher            | 2347  | status        | reg.udral.service.actuator.common.Status_0_1     |
| 8 | publisher            | 2348  | dynamics      | reg.udral.physics.dynamics.rotation.PlanarTs_0_1 |

**Autopilot's specific interface**
| № | Type                 |Port ID| Register name | Data type                                        |
| - | -------------------- |:-----:|:-------------:|:------------------------------------------------:|
| 1 | publisher            | 2341  | note_response | reg.udral.physics.acoustics.Note_0_1             |
| 2 | publisher            | 2342  | setpoint      | reg.udral.service.actuator.common.sp.Scalar_0_1  |
| 3 | publisher            | 2343  | readiness     | reg.udral.service.common.Readiness_0_1           |
| 4 | subscriber           | -     | esc_heartbeat | reg.udral.service.common.Heartbeat_0_1           |
| 5 | subscriber           | 2345  | feedback      | reg.udral.service.actuator.common.Feedback_0_1   |
| 6 | subscriber           | 2346  | power         | reg.udral.physics.electricity.PowerTs_0_1        |
| 7 | subscriber           | 2347  | status        | reg.udral.service.actuator.common.Status_0_1     |
| 8 | subscriber           | 2348  | dynamics      | reg.udral.physics.dynamics.rotation.PlanarTs_0_1 |