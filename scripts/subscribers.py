#!/usr/bin/env python3.7
import sys
import pathlib
import time

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
        self._msg = data_type()

        self.msg_counter = 0
        self.recv_timestamp_ms = 0
        self.time_between_msgs = 0
        self.max_time_between_msgs = 0

    def init(self):
        self._sub = self._node.make_subscriber(self._data_type, self._name)
        self._sub.receive_in_background(self.callback)

    def register_callback(self, callback):
        sub = self._node.make_subscriber(self._data_type, self._name)
        sub.receive_in_background(callback)

    def get_value(self):
        return self._msg.value

    def get_number_of_rx_msgs(self):
        return self.msg_counter

    def update_max_time_between_msgs(self):
        max_time_between_msgs = self.max_time_between_msgs
        self.max_time_between_msgs = 0
        return max_time_between_msgs

    async def callback(self, msg, _):
        self._msg = msg
        self.msg_counter += 1
        self.time_between_msgs = time.time() - self.recv_timestamp_ms
        self.recv_timestamp_ms = time.time()
        if self.time_between_msgs > self.max_time_between_msgs:
            self.max_time_between_msgs = self.time_between_msgs


class SetpointSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="setpoint") -> None:
        super().__init__(node, reg.udral.service.actuator.common.sp.Vector4_0_1, reg_name)


class ReadinessSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="readiness") -> None:
        super().__init__(node, reg.udral.service.common.Readiness_0_1, reg_name)


class EscHeartbeatSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="esc_heartbeat") -> None:
        super().__init__(node, reg.udral.service.common.Heartbeat_0_1, reg_name)


class DynamicsSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="dynamics") -> None:
        super().__init__(node, reg.udral.physics.dynamics.rotation.PlanarTs_0_1, reg_name)


class StatusSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="status") -> None:
        super().__init__(node, reg.udral.service.actuator.common.Status_0_1, reg_name)


class PowerSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="power") -> None:
        super().__init__(node, reg.udral.physics.electricity.PowerTs_0_1, reg_name)
    def get_voltage(self):
        return self._msg.value.voltage.volt
    def get_current(self):
        return self._msg.value.current.ampere


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
    def __init__(self, node, reg_name="feedback") -> None:
        super().__init__(node, reg.udral.service.actuator.common.Feedback_0_1, reg_name)
        self.readiness = "-"
        self.health = "-"
        self.demand_factor_pct = None


    async def callback(self, msg, _):
        self._msg = msg
        if msg.heartbeat.readiness.value in FeedbackSubscriber.READINESS_TO_STR:
            self.readiness = FeedbackSubscriber.READINESS_TO_STR[msg.heartbeat.readiness.value]
        else:
            self.readiness = "-"

        if msg.heartbeat.health.value in FeedbackSubscriber.HEALTH_TO_STR:
            self.health = FeedbackSubscriber.HEALTH_TO_STR[msg.heartbeat.health.value]
        else:
            self.health = "-"

        self.demand_factor_pct = msg.demand_factor_pct

class PortListSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="port") -> None:
        super().__init__(node, uavcan.node.port.List_0_1, reg_name)

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
        self._msg = msg
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


class HeartbeatSubscriber(BaseSubscriber):
    def __init__(self, node, reg_name="heartbeat") -> None:
        super().__init__(node, uavcan.node.Heartbeat_1_0, reg_name)
        self.nodes_avaliable = set()

    async def callback(self, msg, transfer_info) -> None:
        self._msg = msg
        self.nodes_avaliable.add(transfer_info.source_node_id)

    async def get_avaliable_nodes(self) -> None:
        return self.nodes_avaliable


class CyphalSubscriberCreator:
    SUB_TYPE_BY_NAME = {
        "setpoint"          : SetpointSubscriber,
        "readiness"         : ReadinessSubscriber,
        "esc_heartbeat"     : EscHeartbeatSubscriber,
        "dynamics"          : DynamicsSubscriber,
        "status"            : StatusSubscriber,
        "power"             : PowerSubscriber,
        "feedback"          : FeedbackSubscriber,
        "port_list"         : PortListSubscriber,
        "heartbeat"         : HeartbeatSubscriber
    }
    def __init__(self, node) -> None:
        self.node = node

    def create(self, pub_name, reg_name=None, params=None):
        node = None
        if reg_name is None:
            reg_name = pub_name
        if pub_name in CyphalSubscriberCreator.SUB_TYPE_BY_NAME:
            node = CyphalSubscriberCreator.SUB_TYPE_BY_NAME[pub_name](self.node, reg_name)

        return node
