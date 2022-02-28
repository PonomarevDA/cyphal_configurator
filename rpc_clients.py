#!/usr/bin/env python3.7

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
        self._destination_node_id = destination_node_id
        self._rpc_client = self._node.make_client(data_type, destination_node_id)
    def _call(self):
        pass


class RpcClientRegisterList(BaseRpcClient):
    def __init__(self, node, destination_node_id) -> None:
        super().__init__(node, destination_node_id, uavcan.register.List_1_0)

    async def _call(self, index, num_of_max_attempts=10):
        for attemp_counter in range(num_of_max_attempts):
            register_name = await self.call_register_list(index)

            if register_name is not None:
                if len(register_name) == 0:
                    return []
                else:
                    return register_name
            elif attemp_counter == num_of_max_attempts - 1:
                print("ERR: RegisterList has been failed {} times".format(num_of_max_attempts))
                return []
            await asyncio.sleep(0.01)
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

    async def _call(self, register_name, set_value=None):
        if set_value is None:
            req = uavcan.register.Access_1_0.Request(uavcan.register.Name_1_0(register_name))
        else:
            new_value = uavcan.register.Value_1_0()
            new_value.natural16 = uavcan.primitive.array.Natural16_1_0(set_value)
            req = uavcan.register.Access_1_0.Request(\
                uavcan.register.Name_1_0(register_name),
                new_value)

        response = await self._rpc_client.call(req)
        data_type = "Unknown"
        if response is not None:
            read_value = response[0].value
            if read_value.natural16 is not None:
                read_value = read_value.natural16.value[0]
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
            print("ERR: RegisterAccess response is None")
            read_value = None

        return read_value, data_type


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
        response = await self.rpc_client_execute_command.call(req)
        if response is not None:
            print(RpcClientExecuteCommand.EXECUTE_COMMAND_STATUS_TO_STRING[response[0].status])

