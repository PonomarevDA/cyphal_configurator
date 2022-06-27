#!/usr/bin/env python3.7
import os
import sys
import asyncio
import logging
from time import sleep
import pyuavcan
import pathlib
from subscribers import EscHeartbeatSubscriber, DynamicsSubscriber, PortListSubscriber, \
                        HeartbeatSubscriber, StatusSubscriber, PowerSubscriber, FeedbackSubscriber
from publishers import NoteResponsePublisher, SetpointPublisher, ReadinessPublisher

from rpc_clients import RpcClientRegisterList, RpcClientRegisterAccess, RpcClientExecuteCommand
from color_log import log_warn

compiled_dsdl_dir = pathlib.Path(__file__).resolve().parent / "compile_output"
sys.path.insert(0, str(compiled_dsdl_dir))

try:
    import pyuavcan.application
    import uavcan.node
    import uavcan.node.port.List_0_1

    import uavcan.primitive.scalar
    import uavcan.primitive.scalar.Bit_1_0
    import uavcan.node.ExecuteCommand_1_0
    import uavcan.register.Access_1_0
    import uavcan.register.List_1_0
except (ImportError, AttributeError):
    logging.warning("There is no compiled DSDL in {}.".format(compiled_dsdl_dir))
    exit()


COMMAND_STORE_PERSISTENT_STATES = 65530
COMMAND_RESTART = 65535

DEST_NODE_ID = 123
REGISTER_FILE = "allocation_table.db"

COMMON_KOTLETA_REGISTERS_VALUES = {
    "uavcan.sub.note_response.id"       : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__SUB__NOTE_RESPONSE__ID']),
    "uavcan.sub.setpoint.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__SUB__SETPOINT__ID']),
    "uavcan.sub.readiness.id"           : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__SUB__READINESS__ID']),
    "ttl_milliseconds"                  : uavcan.primitive.array.Integer64_1_0(100),
    "control_mode_rpm"                  : uavcan.primitive.array.Bit_1_0(False)
}

ESC_REGISTER_VALUES_1 = {
    **COMMON_KOTLETA_REGISTERS_VALUES,
    "id_in_esc_group"                   : uavcan.primitive.array.Natural16_1_0(0),
    "ctl_dir"                           : uavcan.primitive.array.Integer64_1_0(0),

    "uavcan.pub.esc_heartbeat.id"       : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__ESC_HEARTBEAT_1__ID']),
    "uavcan.pub.feedback.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__FEEDBACK_1__ID']),
    "uavcan.pub.power.id"               : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__POWER_1__ID']),
    "uavcan.pub.status.id"              : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__STATUS_1__ID']),
    "uavcan.pub.dynamics.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__DYNAMICS_1__ID']),
}

ESC_REGISTER_VALUES_2 = {
    **COMMON_KOTLETA_REGISTERS_VALUES,
    "id_in_esc_group"                   : uavcan.primitive.array.Natural16_1_0(1),
    "ctl_dir"                           : uavcan.primitive.array.Integer64_1_0(1),      # wrong connection?

    "uavcan.pub.esc_heartbeat.id"       : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__ESC_HEARTBEAT_2__ID']),
    "uavcan.pub.feedback.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__FEEDBACK_2__ID']),
    "uavcan.pub.power.id"               : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__POWER_2__ID']),
    "uavcan.pub.status.id"              : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__STATUS_2__ID']),
    "uavcan.pub.dynamics.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__DYNAMICS_2__ID']),
}

ESC_REGISTER_VALUES_3 = {
    **COMMON_KOTLETA_REGISTERS_VALUES,
    "id_in_esc_group"                   : uavcan.primitive.array.Natural16_1_0(2),
    "ctl_dir"                           : uavcan.primitive.array.Integer64_1_0(1),

    "uavcan.pub.esc_heartbeat.id"       : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__ESC_HEARTBEAT_3__ID']),
    "uavcan.pub.feedback.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__FEEDBACK_3__ID']),
    "uavcan.pub.power.id"               : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__POWER_3__ID']),
    "uavcan.pub.status.id"              : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__STATUS_3__ID']),
    "uavcan.pub.dynamics.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__DYNAMICS_3__ID']),
}

ESC_REGISTER_VALUES_4 = {
    **COMMON_KOTLETA_REGISTERS_VALUES,
    "id_in_esc_group"                   : uavcan.primitive.array.Natural16_1_0(3),
    "ctl_dir"                           : uavcan.primitive.array.Integer64_1_0(1),

    "uavcan.pub.esc_heartbeat.id"       : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__ESC_HEARTBEAT_4__ID']),
    "uavcan.pub.feedback.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__FEEDBACK_4__ID']),
    "uavcan.pub.power.id"               : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__POWER_4__ID']),
    "uavcan.pub.status.id"              : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__STATUS_4__ID']),
    "uavcan.pub.dynamics.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__DYNAMICS_4__ID']),
}

AUTOPILOT_REGISTER_VALUES = {
    "uavcan.node.id"                    : uavcan.primitive.array.Natural16_1_0(42),
    "uavcan.pub.note_response.id"       : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__NOTE_RESPONSE__ID']),
    "uavcan.pub.setpoint.id"            : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__SETPOINT__ID']),
    "uavcan.pub.readiness.id"           : uavcan.primitive.array.Natural16_1_0(os.environ['UAVCAN__PUB__READINESS__ID']),

    "uavcan.sub.esc_heartbeat.0.id"     : ESC_REGISTER_VALUES_1["uavcan.pub.esc_heartbeat.id"],
    "uavcan.sub.feedback.0.id"          : ESC_REGISTER_VALUES_1["uavcan.pub.feedback.id"],
    "uavcan.sub.power.0.id"             : ESC_REGISTER_VALUES_1["uavcan.pub.power.id"],
    "uavcan.sub.status.0.id"            : ESC_REGISTER_VALUES_1["uavcan.pub.status.id"],
    "uavcan.sub.dynamics.0.id"          : ESC_REGISTER_VALUES_1["uavcan.pub.dynamics.id"],

    "uavcan.sub.esc_heartbeat.1.id"     : ESC_REGISTER_VALUES_2["uavcan.pub.esc_heartbeat.id"],
    "uavcan.sub.feedback.1.id"          : ESC_REGISTER_VALUES_2["uavcan.pub.feedback.id"],
    "uavcan.sub.power.1.id"             : ESC_REGISTER_VALUES_2["uavcan.pub.power.id"],
    "uavcan.sub.status.1.id"            : ESC_REGISTER_VALUES_2["uavcan.pub.status.id"],
    "uavcan.sub.dynamics.1.id"          : ESC_REGISTER_VALUES_2["uavcan.pub.dynamics.id"],

    "uavcan.sub.esc_heartbeat.2.id"     : ESC_REGISTER_VALUES_3["uavcan.pub.esc_heartbeat.id"],
    "uavcan.sub.feedback.2.id"          : ESC_REGISTER_VALUES_3["uavcan.pub.feedback.id"],
    "uavcan.sub.power.2.id"             : ESC_REGISTER_VALUES_3["uavcan.pub.power.id"],
    "uavcan.sub.status.2.id"            : ESC_REGISTER_VALUES_3["uavcan.pub.status.id"],
    "uavcan.sub.dynamics.2.id"          : ESC_REGISTER_VALUES_3["uavcan.pub.dynamics.id"],

    "uavcan.sub.esc_heartbeat.3.id"     : ESC_REGISTER_VALUES_4["uavcan.pub.esc_heartbeat.id"],
    "uavcan.sub.feedback.3.id"          : ESC_REGISTER_VALUES_4["uavcan.pub.feedback.id"],
    "uavcan.sub.power.3.id"             : ESC_REGISTER_VALUES_4["uavcan.pub.power.id"],
    "uavcan.sub.status.3.id"            : ESC_REGISTER_VALUES_4["uavcan.pub.status.id"],
    "uavcan.sub.dynamics.3.id"          : ESC_REGISTER_VALUES_4["uavcan.pub.dynamics.id"],
}


SPECIFIC_REGISTER_VALUES = {
    # 123 :   ESC_REGISTER_VALUES_1,      # front right, CCW
    # 116 :   ESC_REGISTER_VALUES_2,      # rear left, CCW
    # 124 :   ESC_REGISTER_VALUES_3,      # front left, CW
    # 125 :   ESC_REGISTER_VALUES_4,      # rear right, CW
    42:     AUTOPILOT_REGISTER_VALUES,
}

class RegisterTableCell:
    def __init__(self, idx, value_type, value):
        self.idx = idx
        self.value_type = value_type
        self.value = value


class ServerNode:
    def __init__(self) -> None:
        self.subs = {}
        self.pubs = {}

    def run_async(self) -> None:
        asyncio.run(self._main())

    async def _main(self) -> None:
        try:
            await self._init()
            await self._run()
        except KeyboardInterrupt:
            pass
        finally:
            self._close()

    async def _init(self) -> None:
        node_info = uavcan.node.GetInfo_1_0.Response(
            software_version=uavcan.node.Version_1_0(major=1, minor=0),
            name="server_app",
        )
        self._node = pyuavcan.application.make_node(node_info, REGISTER_FILE)
        self._node.heartbeat_publisher.mode = uavcan.node.Mode_1_0.OPERATIONAL
        self._node.heartbeat_publisher.vendor_specific_status_code = 10
        self._node.start()
        self.register_table = dict()

        self._rpc_client_register_list = RpcClientRegisterList(self._node, 0)
        self._rpc_client_register_access = RpcClientRegisterAccess(self._node, 0)
        self._rpc_client_execute_command = RpcClientExecuteCommand(self._node, 0)


    async def _run(self) -> None:
        """
        The main method that runs the business logic.
        """

        await self._start_pub_and_sub()

        avaliable_nodes = await self._scan_network()

        for avaliable_node in avaliable_nodes:

            if avaliable_node in SPECIFIC_REGISTER_VALUES:
                print("Node={}. Writing to registers is in process...".format(avaliable_node))
                write_registers_values = SPECIFIC_REGISTER_VALUES[avaliable_node]
                await self._read_and_write_registers(write_registers_values, avaliable_node)

                if len(COMMON_KOTLETA_REGISTERS_VALUES) != 0:
                    await self._rpc_client_execute_command.init_with_specific_node_id(avaliable_node)
                    await self._rpc_client_execute_command._call(COMMAND_STORE_PERSISTENT_STATES)
                    await self._rpc_client_execute_command._call(COMMAND_RESTART)

            else:
                print("Node={}. Reading of registers is in process...".format(avaliable_node))
                write_registers_values = {}
                await self._read_and_write_registers(write_registers_values, avaliable_node)

        print("Configuration is done.")

        while True:
            await asyncio.sleep(10)

    async def _scan_network(self, scanning_time_sec=2):
        nodes_avaliable = set()
        print("Listening the network...")
        for sec_remaining in range(scanning_time_sec, 0, -1):
            nodes_avaliable = await self.subs["heartbeat"].get_avaliable_nodes()
            print("{}... Avaliable nodes: {}".format(sec_remaining, nodes_avaliable))
            await asyncio.sleep(1)
        print("")
        return nodes_avaliable

    async def _read_and_write_registers(self, registers_values, destination_node_id):
        """
        Discover the names of all registers available on the server.
        """
        MAX_NUMBER_OF_REGISTERS = 100

        await self._rpc_client_register_list.init_with_specific_node_id(destination_node_id)
        await self._rpc_client_register_access.init_with_specific_node_id(destination_node_id)

        for index in range(MAX_NUMBER_OF_REGISTERS):
            # Try until get empty register name that means previous register was the last one
            await asyncio.sleep(0.1)
            register_name = await self._rpc_client_register_list._call(index)
            if len(register_name) == 0:
                break

            # Read or write register value by his name
            set_value = registers_values[register_name] if register_name in registers_values else None
            await asyncio.sleep(0.1)
            read_value, data_type = await self._rpc_client_register_access._call(register_name, set_value)
            if read_value is None:
                print("ERR: RegisterAccess has been failed")
                break

            # Store register value
            self.register_table[register_name] = RegisterTableCell(index, data_type, read_value)

            log_func = print if set_value is None else log_warn
            log_func("{:<3} {:<30} {:<10} {:<5}".format("{}.".format(index),
                                                        register_name,
                                                        data_type,
                                                        str(read_value)))

    async def _start_pub_and_sub(self):
        """
        Initialize all subscribers and publishers which are avaliable on the destination node.
        """
        self.subs = {
            "heartbeat"         : HeartbeatSubscriber(self._node),                           # 7509  fixed
            "port_list"         : PortListSubscriber(self._node),                           # 7510  fixed

            "esc_heartbeat_1"   : EscHeartbeatSubscriber(self._node, "esc_heartbeat_1"),     # empty on kotleta
            "feedback_1"        : FeedbackSubscriber(self._node, "feedback_1"),             # specific for node
            "power_1"           : PowerSubscriber(self._node, "power_1"),                   # specific for node
            "status_1"          : StatusSubscriber(self._node, "status_1"),                 # specific for node
            "dynamics_1"        : DynamicsSubscriber(self._node, "dynamics_1"),             # specific for node

            "esc_heartbeat_2"   : EscHeartbeatSubscriber(self._node, "esc_heartbeat_2"),     # empty on kotleta
            "feedback_2"        : FeedbackSubscriber(self._node, "feedback_2"),             # specific for node
            "power_2"           : PowerSubscriber(self._node, "power_2"),                   # specific for node
            "status_2"          : StatusSubscriber(self._node, "status_2"),                 # specific for node
            "dynamics_2"        : DynamicsSubscriber(self._node, "dynamics_2"),             # specific for node

            "esc_heartbeat_3"   : EscHeartbeatSubscriber(self._node, "esc_heartbeat_3"),     # empty on kotleta
            "feedback_3"        : FeedbackSubscriber(self._node, "feedback_3"),             # specific for node
            "power_3"           : PowerSubscriber(self._node, "power_3"),                   # specific for node
            "status_3"          : StatusSubscriber(self._node, "status_3"),                 # specific for node
            "dynamics_3"        : DynamicsSubscriber(self._node, "dynamics_3"),             # specific for node

            "esc_heartbeat_4"   : EscHeartbeatSubscriber(self._node, "esc_heartbeat_4"),     # empty on kotleta
            "feedback_4"        : FeedbackSubscriber(self._node, "feedback_4"),             # specific for node
            "power_4"           : PowerSubscriber(self._node, "power_4"),                   # specific for node
            "status_4"          : StatusSubscriber(self._node, "status_4"),                 # specific for node
            "dynamics_4"        : DynamicsSubscriber(self._node, "dynamics_4"),             # specific for node
        }
        for sub in self.subs:
            self.subs[sub].init()

        self.pubs = {
            # "note_response": NoteResponsePublisher(self._node, enable_by_default=True),        # 2341  dynamic
            # "setpoint"     : SetpointPublisher(self._node, enable_by_default=True),            # 2342  dynamic
            # "readiness"    : ReadinessPublisher(self._node, enable_by_default=True),           # 2343  dynamic
        }

    def _close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


class ServerNodeFrontend(ServerNode):
    def __init__(self) -> None:
        super().__init__()

    def get_voltage(self, esc_idx=0):
        sub_name = "power_{}".format(esc_idx + 1)
        return self.subs[sub_name].get_voltage() if sub_name in self.subs else None

    def get_current(self, esc_idx=0):
        sub_name = "power_{}".format(esc_idx + 1)
        return self.subs[sub_name].get_current() if sub_name in self.subs else None

    def get_readiness(self, esc_idx=0):
        sub_name = "feedback_{}".format(esc_idx + 1)
        return self.subs[sub_name].readiness if sub_name in self.subs else None

    def get_health(self, esc_idx=0):
        sub_name = "feedback_{}".format(esc_idx + 1)
        return self.subs[sub_name].health if sub_name in self.subs else None

    def get_demand_factor_pct(self, esc_idx=0):
        sub_name = "feedback_{}".format(esc_idx + 1)
        return self.subs[sub_name].demand_factor_pct if sub_name in self.subs else None

    def set_setpoint(self, value, esc_idx=0):
        sub_name = "setpoint"
        if sub_name in self.pubs:
            self.pubs[sub_name].set_value(value, esc_idx=esc_idx)


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    server_node = ServerNode()
    server_node.run_async()
