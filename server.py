#!/usr/bin/env python3.7
import os
import sys
import asyncio
import logging
import pyuavcan
import pathlib
from subscribers import EscHearbeatSubscriber, DynamicsSubscriber, PortListSubscriber, \
                        HearbeatSubscriber, StatusSubscriber, PowerSubscriber, FeedbackSubscriber
from publishers import NoteResponsePublisher, SetpointPublisher, ReadinessPublisher

from rpc_clients import RpcClientRegisterList, RpcClientRegisterAccess, RpcClientExecuteCommand


compiled_dsdl_dir = pathlib.Path(__file__).resolve().parent / "compile_output"
sys.path.insert(0, str(compiled_dsdl_dir))

try:
    import pyuavcan.application
    import uavcan.node
    import uavcan.node.port.List_0_1

    import uavcan.node.ExecuteCommand_1_0
    import uavcan.register.Access_1_0
    import uavcan.register.List_1_0
except (ImportError, AttributeError):
    logging.warning("There is no compiled DSDL in {}.".format(compiled_dsdl_dir))
    exit()


DEST_NODE_ID = 42 #116
REGISTER_FILE = "allocation_table.db"

REGISTERS_VALUES = {
    # "id_in_esc_group"                   : 1,
    # "uavcan.sub.note_response.id"       : 2341,
    # "uavcan.sub.setpoint.id"            : 2342,
    # "uavcan.sub.readiness.id"           : 2343,
    # "uavcan.sub.esc_heartbeat.id"       : 2344,
    # "uavcan.pub.feedback.id"            : 2345,
    # "uavcan.pub.power.id"               : 2346,
    # "uavcan.pub.status.id"              : 2447,
    # "uavcan.pub.dynamics.id"            : 2448,
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

    def get_voltage(self):
        if "power" in self.subs:
            return self.subs["power"].voltage
        return None

    def get_current(self):
        if "power" in self.subs:
            return self.subs["power"].current
        return None

    def get_readiness(self):
        if "feedback" in self.subs:
            return self.subs["feedback"].readiness
        return None

    def get_health(self):
        if "feedback" in self.subs:
            return self.subs["feedback"].health
        return None

    def get_demand_factor_pct(self):
        if "feedback" in self.subs:
            return self.subs["feedback"].demand_factor_pct
        return None

    def set_setpoint(self, value):
        if "setpoint" in self.pubs:
            return self.pubs["setpoint"].set_value(value)

    async def _main(self) -> None:
        try:
            await self._init()
            await self._run()
        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    async def _init(self) -> None:
        node_info = uavcan.node.GetInfo_1_0.Response(
            software_version=uavcan.node.Version_1_0(major=1, minor=0),
            name="server_app",
        )
        self._node = pyuavcan.application.make_node(node_info, REGISTER_FILE)
        self._node.heartbeat_publisher.mode = uavcan.node.Mode_1_0.OPERATIONAL
        self._node.heartbeat_publisher.vendor_specific_status_code = os.getpid() % 100
        self._node.start()
        self.register_table = dict()

        self._rpc_client_register_list = RpcClientRegisterList(self._node, DEST_NODE_ID)
        self._rpc_client_register_access = RpcClientRegisterAccess(self._node, DEST_NODE_ID)
        self._rpc_client_execute_command = RpcClientExecuteCommand(self._node, DEST_NODE_ID)


    async def _run(self) -> None:
        """
        The main method that runs the business logic.
        """

        await self._get_registers()

        # COMMAND_STORE_PERSISTENT_STATES = 65530
        # await self._rpc_client_execute_command._call(COMMAND_STORE_PERSISTENT_STATES)
        # COMMAND_RESTART = 65535
        # await self._rpc_client_execute_command._call(COMMAND_RESTART)

        await self._start_pub_and_sub()

        while True:
            await asyncio.sleep(10)

    async def _get_registers(self):
        """
        Discover the names of all registers available on the server.
        """
        MAX_NUMBER_OF_REGISTERS = 100

        for index in range(MAX_NUMBER_OF_REGISTERS):
            register_name = await self._rpc_client_register_list._call(index)
            if len(register_name) == 0:
                break

            new_value = REGISTERS_VALUES[register_name] if register_name in REGISTERS_VALUES else None
            read_value, data_type = await self._rpc_client_register_access._call(register_name, new_value)
            if read_value is None:
                print("ERR: RegisterAccess has been failed")
                break

            self.register_table[register_name] = RegisterTableCell(index, data_type, read_value)

            print("{:<3} {:<30} {:<10} {:<5}".format("{}.".format(index),
                                                     register_name,
                                                     data_type,
                                                     read_value))

    async def _start_pub_and_sub(self):
        """
        Initialize all subscribers and publishers which are avaliable on the destination node.
        """
        self.subs = {
            "heartbeat"     : HearbeatSubscriber(self._node),       # 7509
            "port_list"     : PortListSubscriber(self._node),       # 7510
            "esc_heartbeat" : EscHearbeatSubscriber(self._node),    # 2344  empty on kotleta
            "feedback"      : FeedbackSubscriber(self._node),       # 2345
            "power"         : PowerSubscriber(self._node),          # 2346
            "status"        : StatusSubscriber(self._node),         # 2347
            "dynamics"      : DynamicsSubscriber(self._node),       # 2348
        }

        self.pubs = {
            "note_response": NoteResponsePublisher(self._node),     # 2341
            "setpoint"     : SetpointPublisher(self._node),         # 2342
            "readiness"    : ReadinessPublisher(self._node),        # 2343
        }

    def close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    server_node = ServerNode()
    server_node.run_async()
