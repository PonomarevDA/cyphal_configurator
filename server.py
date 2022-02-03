#!/usr/bin/env python3.7

import os
import sys
import pathlib
import asyncio
import logging
import importlib
import pyuavcan

compiled_dsdl_dir = pathlib.Path(__file__).resolve().parent / "compile_output"
sys.path.insert(0, str(compiled_dsdl_dir))

try:
    import pyuavcan.application
    import uavcan.node
    import uavcan.register.List_1_0
    import uavcan.register.Access_1_0
except (ImportError, AttributeError):
    logging.warning("There is no compiled DSDL in {}.".format(compiled_dsdl_dir))
    exit()

DEST_NODE_ID = 122
REGISTER_FILE = "allocation_table.db"

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

    async def run(self) -> None:
        """
        The main method that runs the business logic.
        """

        for index in range(100):
            register_name = await self.call_register_list(index)
            if register_name is None:
                print("error")
                continue
            elif len(register_name) == 0:
                break

            if register_name == "uavcan.pub.feedback.id":
                value, data_type = await self.call_register_access(\
                    register_name=register_name)
            else:
                value, data_type = await self.call_register_access(register_name=register_name)

            if value is None:
                print("error")
                continue

            self.register_table[register_name] = RegisterTableCell(idx=index,
                                                                   value_type=data_type,
                                                                   value=value)

            print("{:<3} {:<30} {:<10} {:<5}".format("{}.".format(index),
                                                     register_name,
                                                     data_type,
                                                     value))

    async def call_register_list(self, index=0):
        """uavcan.register.List"""
        rpc_client = self._node.make_client(uavcan.register.List_1_0, DEST_NODE_ID)
        req = uavcan.register.List_1_0.Request(index)
        response = await rpc_client.call(req)
        if response is not None:
            response = str(response[0].name.name.tobytes().decode("utf-8"))
        else:
            response = None
        return response

    async def call_register_access(self, register_name, value=None):
        """uavcan.register.Access"""
        rpc_client = self._node.make_client(uavcan.register.Access_1_0, DEST_NODE_ID)

        if value is None:
            req = uavcan.register.Access_1_0.Request(uavcan.register.Name_1_0(register_name))
        else:
            new_value = uavcan.register.Value_1_0()
            new_value.natural16 = uavcan.primitive.array.Natural16_1_0(value)
            req = uavcan.register.Access_1_0.Request(\
                uavcan.register.Name_1_0(register_name),
                new_value)

        response = await rpc_client.call(req)
        data_type = "Unknown"
        if response is not None:
            value = response[0].value
            if value.natural16 is not None:
                value = value.natural16.value[0]
                data_type = "natural16"
            elif value.string is not None:
                value = App.np_array_to_string(value.string.value)
                data_type = "string"
            elif value.bit is not None:
                value = value.bit.value[0]
                data_type = "bit"
            elif value.real64 is not None:
                value = value.real64.value[0]
                data_type = "real64"
            elif value.integer64 is not None:
                value = value.integer64.value[0]
                data_type = "integer64"
            elif value.empty is not None:
                value = "Empty"
                data_type = "empty"
            else:
                value = None
        else:
            value = None

        return value, data_type

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