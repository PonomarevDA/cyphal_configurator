#!/usr/bin/env python3.7
import sys
import asyncio
import pathlib

compiled_dsdl_dir = pathlib.Path(__file__).resolve().parent / "compile_output"
sys.path.insert(0, str(compiled_dsdl_dir))

import uavcan.node
import uavcan.node.port.List_0_1

import reg.udral.service.actuator.common.Feedback_0_1
import reg.udral.service.actuator.common.sp.Scalar_0_1
import reg.udral.service.common.Readiness_0_1
import reg.udral.service.common.Heartbeat_0_1
import reg.udral.physics.acoustics.Note_0_1
import reg.udral.physics.dynamics.rotation.PlanarTs_0_1
import reg.udral.physics.electricity.PowerTs_0_1

import uavcan.node.ExecuteCommand_1_0
import uavcan.register.Access_1_0
import uavcan.register.List_1_0



class BasePublisher:
    def __init__(self, node, data_type, name) -> None:
        self._pub = node.make_publisher(data_type, name)
        self._pub_task = asyncio.create_task(self.pub_task())
        self.data_type = data_type

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.5)


class NoteResponsePublisher(BasePublisher):
    def __init__(self, node, name="note_response") -> None:
        super().__init__(node, reg.udral.physics.acoustics.Note_0_1, name)


class SetpointPublisher(BasePublisher):
    def __init__(self, node, name="setpoint") -> None:
        super().__init__(node, reg.udral.service.actuator.common.sp.Scalar_0_1, name)
        self.value = 0

    def set_value(self, new_value):
        self.value = new_value

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.005)
            await self._pub.publish(self.data_type(self.value))


class ReadinessPublisher(BasePublisher):
    def __init__(self, node, name="readiness") -> None:
        super().__init__(node, reg.udral.service.common.Readiness_0_1, name)

    async def pub_task(self):
        while True:
            await asyncio.sleep(1)
            SLEEP = 0
            STANDBY = 2
            ENGAGED = 3
            await self._pub.publish(self.data_type(ENGAGED))
            print("pub: ENGAGED")
