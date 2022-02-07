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
        self._sub = node.make_subscriber(data_type, name)
        self._sub.receive_in_background(self.callback)
    async def callback(self, msg, _):
        print(msg)

class EscHearbeatSubscriber(BaseSubscriber):
    def __init__(self, node, name="esc_heartbeat") -> None:
        super().__init__(node, reg.udral.service.common.Heartbeat_0_1, name)

class DynamicsSubscriber(BaseSubscriber):
    def __init__(self, node, name="dynamics") -> None:
        super().__init__(node, reg.udral.physics.dynamics.rotation.PlanarTs_0_1, name)

class PortListSubscriber(BaseSubscriber):
    def __init__(self, node, name="port") -> None:
        super().__init__(node=node, data_type=uavcan.node.port.List_0_1, name=name)
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
            print("sub: (Heartbeat: {}, {}, {}, {})".format(\
                msg.uptime,
                VALUE_TO_HEALTH_STRING[msg.health.value],
                VALUE_TO_MODE_STRING[msg.mode.value],
                msg.vendor_specific_status_code))

class PowerSubscriber(BaseSubscriber):
    def __init__(self, node, name="power") -> None:
        super().__init__(node, reg.udral.physics.electricity.PowerTs_0_1, name)
    async def callback(self, msg, _):
        print("sub: Power (current={}, voltage={})".format(\
            msg.value.current.ampere,
            msg.value.voltage.volt))

class FeedbackSubscriber(BaseSubscriber):
    def __init__(self, node, name="feedback") -> None:
        super().__init__(node, reg.udral.service.actuator.common.Feedback_0_1, name)
    async def callback(self, msg, _):
        print("sub: Feedback (readiness={}, health={}, vdemand_factor_pct={})".format(\
            msg.heartbeat.readiness.value,
            msg.heartbeat.health.value,
            msg.demand_factor_pct))
