#!/usr/bin/env python3.7
import sys
import asyncio
import pathlib

compiled_dsdl_dir = pathlib.Path(__file__).resolve().parent / "compile_output"
sys.path.insert(0, str(compiled_dsdl_dir))

import uavcan.node
import uavcan.node.port.List_0_1

import reg.udral.service.actuator.common.Status_0_1
import reg.udral.service.actuator.common.Feedback_0_1
import reg.udral.service.actuator.common.sp.Scalar_0_1
import reg.udral.service.actuator.common.sp.Vector2_0_1
import reg.udral.service.actuator.common.sp.Vector4_0_1
import reg.udral.service.common.Readiness_0_1
import reg.udral.service.common.Heartbeat_0_1
import reg.udral.physics.acoustics.Note_0_1
import reg.udral.physics.dynamics.rotation.PlanarTs_0_1
import reg.udral.physics.electricity.PowerTs_0_1

import uavcan.node.ExecuteCommand_1_0
import uavcan.register.Access_1_0
import uavcan.register.List_1_0



class BasePublisher:
    def __init__(self, node, data_type, name, enable_by_default=True) -> None:
        self._pub = node.make_publisher(data_type, name)
        if enable_by_default:
            self._pub_task = asyncio.create_task(self.pub_task())
        else:
            self._pub_task = None
        self.data_type = data_type

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.5)

    async def enable(self):
        if self._pub_task is None or self._pub_task.cancelled():
            self._pub_task = asyncio.create_task(self.pub_task())

    async def disable(self):
        if self._pub_task is not None and not self._pub_task.cancelled():
            self.pub_task.cancel()

class NoteResponsePublisher(BasePublisher):
    def __init__(self, node, name="note_response", enable_by_default=True) -> None:
        super().__init__(node, reg.udral.physics.acoustics.Note_0_1, name, enable_by_default)

    async def pub_task(self):
        while True:
            await asyncio.sleep(1)
            msg = reg.udral.physics.acoustics.Note_0_1()
            msg.frequency.hertz = 1000
            msg.duration.second = 0.01
            msg.acoustic_power.watt = 0.0005
            await self._pub.publish(msg)

class SetpointPublisher(BasePublisher):
    def __init__(self, node, name="setpoint", enable_by_default=True) -> None:
        super().__init__(node, reg.udral.service.actuator.common.sp.Vector4_0_1, name, enable_by_default)
        self.value = [0, 0, 0, 0]

    def set_value(self, new_value, esc_idx=0):
        self.value[esc_idx] = new_value

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.003)
            await self._pub.publish(self.data_type(self.value))


class ReadinessPublisher(BasePublisher):
    def __init__(self, node, name="readiness", enable_by_default=True) -> None:
        super().__init__(node, reg.udral.service.common.Readiness_0_1, name, enable_by_default)

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.5)
            SLEEP = 0
            STANDBY = 2
            ENGAGED = 3
            await self._pub.publish(self.data_type(ENGAGED))


class DynamicsPublisher(BasePublisher):
    def __init__(self, node, name="dynamics", enable_by_default=True) -> None:
        self.msg = reg.udral.physics.dynamics.rotation.PlanarTs_0_1()
        super().__init__(node, reg.udral.physics.dynamics.rotation.PlanarTs_0_1, name, enable_by_default)
        self.msg.value.kinematics.angular_position.radian = 0.0
        self.msg.value.kinematics.angular_velocity.radian_per_second = 0.0
        self.msg.value.kinematics.angular_acceleration.radian_per_second_per_second = 0.0

    def set_value(self, radian_per_second):
        self.msg.value.kinematics.angular_velocity.radian_per_second = radian_per_second

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.1)
            self.msg.timestamp.microsecond += 100000

            self.msg.value.torque.newton_meter=0.0
            await self._pub.publish(self.msg)

class PowerPublisher(BasePublisher):
    def __init__(self, node, name="power", enable_by_default=True) -> None:
        self.msg = reg.udral.physics.electricity.PowerTs_0_1()
        self.msg.value.current.ampere = 0.005
        self.msg.value.voltage.volt = 12.0
        super().__init__(node, reg.udral.physics.electricity.PowerTs_0_1, name, enable_by_default)

    def set_value(self, current, voltage):
        self.msg.value.current.ampere = current
        self.msg.value.voltage.volt = voltage

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.1)
            self.msg.timestamp.microsecond += 100000
            await self._pub.publish(self.msg)

class FeedbackPublisher(BasePublisher):
    """
    reg.udral.service.actuator.common.Feedback_0_1
    https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Feedback.0.1.uavcan
    """
    def __init__(self, node, name="feedback", enable_by_default=True) -> None:
        self.msg = reg.udral.service.actuator.common.Feedback_0_1()
        self.msg.demand_factor_pct = 0
        super().__init__(node, reg.udral.service.actuator.common.Feedback_0_1, name, enable_by_default)

    def set_value(self, demand_factor_pct):
        self.msg.demand_factor_pct = demand_factor_pct

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.1)
            await self._pub.publish(self.msg)

class StatusPublisher(BasePublisher):
    """
    reg.udral.service.actuator.common.Status_0_1
    https://github.com/UAVCAN/public_regulated_data_types/blob/master/reg/udral/service/actuator/common/Status.0.1.uavcan
    """
    def __init__(self, node, name="status", enable_by_default=True) -> None:
        self.msg = reg.udral.service.actuator.common.Status_0_1()
        self.msg.motor_temperature.kelvin = 300
        self.msg.controller_temperature.kelvin = 301
        super().__init__(node, reg.udral.service.actuator.common.Status_0_1, name, enable_by_default)

    def set_motor_temperature(self, temperature_kelvin):
        self.msg.motor_temperature.kelvin = temperature_kelvin
        pass

    async def pub_task(self):
        while True:
            await asyncio.sleep(0.1)
            await self._pub.publish(self.msg)
