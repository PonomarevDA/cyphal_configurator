#!/usr/bin/env python3.7
import os
import sys
import asyncio
import logging
import pyuavcan
import pathlib

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

    async def run(self) -> None:
        """
        The main method that runs the business logic.
        """

        await self._get_registers()
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
        async def print_callback(msg, _):
            print(msg)
        async def on_heartbeat_callback(msg: uavcan.node.Heartbeat_1_0, _: pyuavcan.transport.TransferFrom) -> None:
            print("sub: Heartbeat: {}, {}, {}, {}".format(msg.uptime,
                                                     VALUE_TO_HEALTH_STRING[msg.health.value],
                                                     VALUE_TO_MODE_STRING[msg.mode.value],
                                                     msg.vendor_specific_status_code))
        async def on_port_list(msg: uavcan.node.Heartbeat_1_0, _: pyuavcan.transport.TransferFrom) -> None:
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

        self._sub_port_list = self._node.make_subscriber(uavcan.node.port.List_0_1, "port")
        self._sub_port_list.receive_in_background(on_port_list)

        self._sub_heartbeat = self._node.make_subscriber(uavcan.node.Heartbeat_1_0, "heartbeat")
        self._sub_heartbeat.receive_in_background(on_heartbeat_callback)

        self._sub_esc_heartbeat = self._node.make_subscriber(reg.udral.service.common.Heartbeat_0_1, "esc_heartbeat")
        self._sub_esc_heartbeat.receive_in_background(print_callback)

        self._sub_feedback = self._node.make_subscriber(reg.udral.service.actuator.common.Feedback_0_1, "feedback")
        self._sub_feedback.receive_in_background(print_callback)

        self._sub_power = self._node.make_subscriber(reg.udral.physics.electricity.PowerTs_0_1, "power")
        self._sub_power.receive_in_background(print_callback)

        self._sub_dynamics = self._node.make_subscriber(reg.udral.physics.dynamics.rotation.PlanarTs_0_1, "dynamics")
        self._sub_dynamics.receive_in_background(print_callback)


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
        uavcan.register.List
        """
        req = uavcan.register.List_1_0.Request(index)
        response = await self.rpc_client_register_list.call(req)
        if response is not None:
            response = App.np_array_to_string(response[0].name.name)
        return response

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
