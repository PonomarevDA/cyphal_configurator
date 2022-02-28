#!/usr/bin/env python3.7
import sys
import logging
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
import reg.udral.service.actuator.common.Status_0_1
import reg.udral.physics.electricity.PowerTs_0_1

import uavcan.node.ExecuteCommand_1_0
import uavcan.register.Access_1_0
import uavcan.register.List_1_0


VALUE_TO_HEALTH_STRING = {
    0 : "NOMINAL",
    1 : "ADVISORY",
    2 : "CAUTION",
    3 : "WARNING"
}
VALUE_TO_MODE_STRING = {
    0 : "OPERATIONAL",
    1 : "INITIALIZATION",
    2 : "MAINTENANCE",
    3 : "SOFTWARE_UPDATE"
}


class BaseSubscriber:
    def __init__(self, node, data_type, name) -> None:
        self._node = node
        self._data_type = data_type
        self._name = name

    def init(self):
        self._sub = self._node.make_subscriber(self._data_type, self._name)
        self._sub.receive_in_background(self.callback)

    async def callback(self, msg, _):
        pass
        # print(msg)


class SetpointSubscriber(BaseSubscriber):
    def __init__(self, node, name="setpoint") -> None:
        super().__init__(node, reg.udral.service.actuator.common.sp.Vector4_0_1, name)
        self.value = [None, None, None, None]

    async def callback(self, msg, _) -> None:
        self.value = msg.value

class ReadinessSubscriber(BaseSubscriber):
    def __init__(self, node, name="readiness") -> None:
        super().__init__(node, reg.udral.service.common.Readiness_0_1, name)
        self.value = None

    async def callback(self, msg, _) -> None:
        self.value = msg.value


class EscHearbeatSubscriber(BaseSubscriber):
    def __init__(self, node, name="esc_heartbeat") -> None:
        super().__init__(node, reg.udral.service.common.Heartbeat_0_1, name)
        self.msg = None

    async def callback(self, msg, _) -> None:
        self.msg = msg

class DynamicsSubscriber(BaseSubscriber):
    def __init__(self, node, name="dynamics") -> None:
        super().__init__(node, reg.udral.physics.dynamics.rotation.PlanarTs_0_1, name)

class StatusSubscriber(BaseSubscriber):
    def __init__(self, node, name="status") -> None:
        super().__init__(node, reg.udral.service.actuator.common.Status_0_1, name)

class PortListSubscriber(BaseSubscriber):
    def __init__(self, node, name="port") -> None:
        super().__init__(node, uavcan.node.port.List_0_1, name)

    async def callback(self, msg, _) -> None:
        """
        Last time response was:
        - pub 7509:     uavcan.node.Heartbeat.1.0
        - pub 7510:     uavcan.node.port.List.0.1
        - server 384:   uavcan.register.Access.1.0
        - server 385:   uavcan.register.List.1.0
        - server 430:   uavcan.node.GetInfo.1.0
        - server 435:   uavcan.node.ExecuteCommand 1.0 or 1.1?
        """
        publishers = []
        subscribers = []
        cliens = []
        servers = []

        if msg.publishers.sparse_list is not None:
            for port in msg.publishers.sparse_list:
                publishers.append(port.value)
        if msg.subscribers.sparse_list is not None:
            for port in msg.subscribers.sparse_list:
                subscribers.append(port.value)
        for idx in (range(len(msg.clients.mask))):
            if msg.clients.mask[idx]:
                cliens.append(idx)
        for idx in (range(len(msg.servers.mask))):
            if msg.servers.mask[idx]:
                servers.append(idx)
        print("sub: Port.List: {}, {}, {}, {}".format(\
            "\n    - pub: {}".format(publishers),
            "\n    - sub on: {}".format(subscribers),
            "\n    - clients: {}".format(cliens),
            "\n    - servers: {}".format(servers)))


class HearbeatSubscriber(BaseSubscriber):
    def __init__(self, node, name="heartbeat") -> None:
        super().__init__(node, uavcan.node.Heartbeat_1_0, name)

    async def callback(self, msg, _) -> None:
        pass

class PowerSubscriber(BaseSubscriber):
    def __init__(self, node, name="power") -> None:
        super().__init__(node, reg.udral.physics.electricity.PowerTs_0_1, name)
        self.current = None
        self.voltage = None

    async def callback(self, msg, _):
        self.current = msg.value.current.ampere
        self.voltage = msg.value.voltage.volt


class FeedbackSubscriber(BaseSubscriber):
    READINESS_TO_STR = {
        0   : "SLEEP",
        1   : "INVALID",
        2   : "STANDBY",
        3   : "ENGAGED",
    }
    HEALTH_TO_STR = {
        0   : "NOMINAL",
        1   : "ADVISORY",
        2   : "CAUTION",
        3   : "WARNING",
    }
    def __init__(self, node, name="feedback") -> None:
        super().__init__(node, reg.udral.service.actuator.common.Feedback_0_1, name)
        self.readiness = "-"
        self.health = "-"
        self.demand_factor_pct = None


    async def callback(self, msg, _):
        if msg.heartbeat.readiness.value in FeedbackSubscriber.READINESS_TO_STR:
            self.readiness = FeedbackSubscriber.READINESS_TO_STR[msg.heartbeat.readiness.value]
        else:
            self.readiness = "-"

        if msg.heartbeat.health.value in FeedbackSubscriber.HEALTH_TO_STR:
            self.health = FeedbackSubscriber.HEALTH_TO_STR[msg.heartbeat.health.value]
        else:
            self.health = "-"

        self.demand_factor_pct = msg.demand_factor_pct
