#!/usr/bin/env python3.7
import os
import sys
import asyncio
import logging
import pyuavcan
import pathlib
from subscribers import EscHearbeatSubscriber, DynamicsSubscriber, PortListSubscriber, \
                        HearbeatSubscriber, PowerSubscriber, FeedbackSubscriber

compiled_dsdl_dir = pathlib.Path(__file__).resolve().parent / "compile_output"
sys.path.insert(0, str(compiled_dsdl_dir))

try:
    import pyuavcan.application
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
except (ImportError, AttributeError):
    logging.warning("There is no compiled DSDL in {}.".format(compiled_dsdl_dir))
    exit()


DEST_NODE_ID = 116
REGISTER_FILE = "allocation_table.db"

REGISTERS_VALUES = {
    "id_in_esc_group"                   : 1,
    "uavcan.sub.note_response.id"       : 2341,
    "uavcan.sub.setpoint.id"            : 2342,
    "uavcan.sub.readiness.id"           : 2343,
    "uavcan.pub.esc_heartbeat.id"       : 2344,
    "uavcan.pub.feedback.id"            : 2345,
    "uavcan.pub.power.id"               : 2346,
    "uavcan.pub.status.id"              : 2447,
    "uavcan.pub.dynamics.id"            : 2448,
}
EXECUTE_COMMAND_STATUS_TO_STRING = {
    0 : "STATUS_SUCCESS",
    1 : "STATUS_FAILURE",
    2 : "STATUS_NOT_AUTHORIZED",
    3 : "STATUS_BAD_COMMAND",
    4 : "STATUS_BAD_PARAMETER",
    5 : "STATUS_BAD_STATE",
    6 : "STATUS_INTERNAL_ERROR",
}


class RegisterTableCell:
    def __init__(self, idx, value_type, value):
        self.idx = idx
        self.value_type = value_type
        self.value = value


class App:
    def __init__(self) -> None:
        node_info = uavcan.node.GetInfo_1_0.Response(
            software_version=uavcan.node.Version_1_0(major=1, minor=0),
            name="server_app",
        )
        self._node = pyuavcan.application.make_node(node_info, REGISTER_FILE)
        self._node.heartbeat_publisher.mode = uavcan.node.Mode_1_0.OPERATIONAL
        self._node.heartbeat_publisher.vendor_specific_status_code = os.getpid() % 100
        self._node.start()
        self.register_table = dict()

        self.rpc_client_register_access = self._node.make_client(uavcan.register.Access_1_0, DEST_NODE_ID)
        self.rpc_client_register_list = self._node.make_client(uavcan.register.List_1_0, DEST_NODE_ID)
        self.rpc_client_execute_command = self._node.make_client(uavcan.node.ExecuteCommand_1_0, DEST_NODE_ID)

    async def run(self) -> None:
        """
        The main method that runs the business logic.
        """

        await self._get_registers()

        COMMAND_STORE_PERSISTENT_STATES = 65530
        await self.call_execute_command(COMMAND_STORE_PERSISTENT_STATES)
        COMMAND_RESTART = 65535
        await self.call_execute_command(COMMAND_RESTART)

        await self._start_pub_and_sub()

        print("waiting 15 seconds...")
        await asyncio.sleep(15)

    async def _get_registers(self):
        """
        Discover the names of all registers available on the server.
        """
        for index in range(100):
            NUMBER_OF_ATTEMPTS = 10
            is_it_last_parameter = False
            for attemp_counter in range(NUMBER_OF_ATTEMPTS):
                register_name = await self.call_register_list(index)
                if register_name is not None:
                    if len(register_name) == 0:
                        is_it_last_parameter = True
                    break
                elif attemp_counter == NUMBER_OF_ATTEMPTS - 1:
                    print("error")
                    break
                await asyncio.sleep(0.01)
            if is_it_last_parameter:
                break

            new_value = REGISTERS_VALUES[register_name] if register_name in REGISTERS_VALUES else None
            read_value, data_type = await self.call_register_access(register_name, new_value)

            if read_value is None:
                print("error")
                continue

            self.register_table[register_name] = RegisterTableCell(index, data_type, read_value)

            print("{:<3} {:<30} {:<10} {:<5}".format("{}.".format(index),
                                                     register_name,
                                                     data_type,
                                                     read_value))

    async def _start_pub_and_sub(self):
        """
        Initialize all subscribers and publishers which are avaliable on the destination node.
        """
        self.subs = [
            EscHearbeatSubscriber(self._node),
            PowerSubscriber(self._node),
            PortListSubscriber(self._node),
            HearbeatSubscriber(self._node),
            FeedbackSubscriber(self._node),
            DynamicsSubscriber(self._node),
        ]

        self._pub_note_response = self._node.make_publisher(reg.udral.physics.acoustics.Note_0_1, "note_response")
        self.note_response_pub_task = asyncio.create_task(
            self.note_response_pub()
        )

        self._pub_setpoint = self._node.make_publisher(reg.udral.service.actuator.common.sp.Scalar_0_1, "setpoint")
        self.setpoint_pub_task = asyncio.create_task(
            self.setpoint_pub()
        )

        self._pub_readiness = self._node.make_publisher(reg.udral.service.common.Readiness_0_1, "readiness")
        self.readiness_pub_task = asyncio.create_task(
            self.readiness_pub()
        )

    async def note_response_pub(self):
        while True:
            await asyncio.sleep(0.5)

    async def setpoint_pub(self):
        """
        reg.udral.service.actuator.common.sp.Scalar_0_1
        """
        while True:
            await asyncio.sleep(0.05)
            await self._pub_setpoint.publish(reg.udral.service.actuator.common.sp.Scalar_0_1(0))

    async def readiness_pub(self):
        """
        reg.udral.service.common.Readiness_0_1
        """
        while True:
            await asyncio.sleep(0.5)
            SLEEP = 0
            STANDBY = 2
            ENGAGED = 3
            await self._pub_readiness.publish(reg.udral.service.common.Readiness_0_1(STANDBY))
            print("pub: STANDBY")


    async def call_register_list(self, index=0):
        """
        uavcan.register.List_1_0
        """
        req = uavcan.register.List_1_0.Request(index)
        response = await self.rpc_client_register_list.call(req)
        if response is not None:
            response = App.np_array_to_string(response[0].name.name)
        return response

    async def call_execute_command(self, cmd):
        """
        uavcan.node.ExecuteCommand_1_0
        """
        req = uavcan.node.ExecuteCommand_1_0.Request(cmd)
        response = await self.rpc_client_execute_command.call(req)
        if response is not None:
            print(EXECUTE_COMMAND_STATUS_TO_STRING[response[0].status])

    async def call_register_access(self, register_name, set_value=None):
        """
        uavcan.register.Access
        set or read register
        """
        if set_value is None:
            req = uavcan.register.Access_1_0.Request(uavcan.register.Name_1_0(register_name))
        else:
            new_value = uavcan.register.Value_1_0()
            new_value.natural16 = uavcan.primitive.array.Natural16_1_0(set_value)
            req = uavcan.register.Access_1_0.Request(\
                uavcan.register.Name_1_0(register_name),
                new_value)

        response = await self.rpc_client_register_access.call(req)
        data_type = "Unknown"
        if response is not None:
            read_value = response[0].value
            if read_value.natural16 is not None:
                read_value = read_value.natural16.value[0]
                data_type = "natural16"
            elif read_value.string is not None:
                read_value = App.np_array_to_string(read_value.string.value)
                data_type = "string"
            elif read_value.bit is not None:
                read_value = read_value.bit.value[0]
                data_type = "bit"
            elif read_value.real64 is not None:
                read_value = read_value.real64.value[0]
                data_type = "real64"
            elif read_value.integer64 is not None:
                read_value = read_value.integer64.value[0]
                data_type = "integer64"
            elif read_value.empty is not None:
                read_value = "Empty"
                data_type = "empty"
            else:
                read_value = None
        else:
            read_value = None

        return read_value, data_type

    @staticmethod
    def np_array_to_string(arr):
        return str(arr.tobytes().decode("utf-8"))

    def close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


async def main() -> None:
    logging.root.setLevel(logging.INFO)
    app = App()
    try:
        await app.run()
    except KeyboardInterrupt:
        pass
    finally:
        app.close()


if __name__ == "__main__":
    asyncio.run(main())
