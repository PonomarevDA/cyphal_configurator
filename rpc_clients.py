#!/usr/bin/env python3.7

from multiprocessing.connection import wait
import sys
import asyncio
import pathlib

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


def np_array_to_string(arr):
        try:
            return str(arr.tobytes().decode("utf-8"))
        except UnicodeDecodeError:
            print("UnicodeDecodeError")
            return "??UnicodeDecodeError??"


class BaseRpcClient:
    def __init__(self, source_node, destination_node_id, data_type) -> None:
        self._node = source_node
        self._data_type = data_type
        self._destination_node_id = destination_node_id
        self._rpc_client = self._node.make_client(self._data_type, destination_node_id)

    async def init_with_specific_node_id(self, destination_node_id):
        self._destination_node_id = destination_node_id
        self._rpc_client = self._node.make_client(self._data_type, destination_node_id)

    def _call(self):
        pass


class RpcClientRegisterList(BaseRpcClient):
    def __init__(self, node, destination_node_id) -> None:
        super().__init__(node, destination_node_id, uavcan.register.List_1_0)

    async def _call(self, index, num_of_max_attempts=10):
        for attemp_counter in range(1, num_of_max_attempts + 1):
            print("\rRegList {}/{}".format(attemp_counter, num_of_max_attempts), flush=True, end = '')
            register_name = await self.call_register_list(index)

            if register_name is not None:
                if len(register_name) == 0:
                    register_name = []
                break
            elif attemp_counter == num_of_max_attempts:
                print("")
                register_name = []
                break
            await asyncio.sleep(0.1)
        print("\r", end = '')
        return register_name

    async def call_register_list(self, index=0):
        req = uavcan.register.List_1_0.Request(index)
        response = await self._rpc_client.call(req)
        if response is not None:
            response = np_array_to_string(response[0].name.name)
        return response

class RpcClientRegisterAccess(BaseRpcClient):
    """
    uavcan.register.Access
    """
    def __init__(self, node, destination_node_id) -> None:
        super().__init__(node, destination_node_id, uavcan.register.Access_1_0)

    async def _call(self, register_name_string, set_value=None, num_of_max_attempts=10):
        register_name = uavcan.register.Name_1_0(register_name_string)

        if set_value is None:
            req = RpcClientRegisterAccess.make_read_request(register_name)
        else:
            req = RpcClientRegisterAccess.make_write_request(register_name, set_value)

        for attempt in range(1, num_of_max_attempts + 1):
            print("\rRegAccess {}/{}".format(attempt, num_of_max_attempts), flush=True, end = '')
            response = await self._rpc_client.call(req)
            if response is not None:
                break
            await asyncio.sleep(0.1)
        if attempt != num_of_max_attempts:
            print("\r", end = '')
        else:
            print("")


        data_type = "Unknown"
        if response is not None:
            read_value = response[0].value
            if read_value.natural16 is not None:
                read_value = read_value.natural16.value
                data_type = "natural16"
            elif read_value.string is not None:
                read_value = np_array_to_string(read_value.string.value)
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
                print("ERR: RegisterAccess unknown data_type", read_value)
                read_value = None
        else:
            print("ERR: RegisterAccess response on {} is None, attempt={}/{}".format(\
                register_name_string,
                attempt,
                num_of_max_attempts))
            read_value = None

        return read_value, data_type

    @staticmethod
    def make_read_request(register_name):
        return uavcan.register.Access_1_0.Request(register_name)

    @staticmethod
    def make_write_request(register_name, set_value):
        new_value = uavcan.register.Value_1_0()

        if type(set_value) == uavcan.primitive.array.Natural16_1_0:
            new_value.natural16 = set_value
        elif type(set_value) == uavcan.primitive.array.Integer64_1_0:
            new_value.integer64 = set_value
        elif type(set_value) == uavcan.primitive.array.Bit_1_0:
            new_value.bit = set_value
        else:
            print("ERR. Can't create write request.")

        return uavcan.register.Access_1_0.Request(register_name, new_value)


class RpcClientExecuteCommand(BaseRpcClient):
    """
    uavcan.node.ExecuteCommand_1_0
    """
    EXECUTE_COMMAND_STATUS_TO_STRING = {
        0 : "STATUS_SUCCESS",
        1 : "STATUS_FAILURE",
        2 : "STATUS_NOT_AUTHORIZED",
        3 : "STATUS_BAD_COMMAND",
        4 : "STATUS_BAD_PARAMETER",
        5 : "STATUS_BAD_STATE",
        6 : "STATUS_INTERNAL_ERROR",
    }
    def __init__(self, node, destination_node_id) -> None:
        super().__init__(node, destination_node_id, uavcan.node.ExecuteCommand_1_0)

    async def _call(self, cmd):
        req = uavcan.node.ExecuteCommand_1_0.Request(cmd)
        response = await self._rpc_client.call(req)
        if response is not None:
            print(RpcClientExecuteCommand.EXECUTE_COMMAND_STATUS_TO_STRING[response[0].status])

