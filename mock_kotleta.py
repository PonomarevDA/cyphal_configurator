#!/usr/bin/env python3.7
import sys
import asyncio
import logging
import pyuavcan
import pathlib
from subscribers import SetpointSubscriber, ReadinessSubscriber, HearbeatSubscriber
from publishers import DynamicsPublisher, PowerPublisher, ReadinessPublisher


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


REGISTER_FILE = "allocation_table.db"

class KotletaMock:
    def __init__(self, node_id, esc_idx=0) -> None:
        self.node_id = node_id
        self.esc_idx = esc_idx

        self.subs = {}
        self.pubs = {}

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
            name="kotleta_mock",
        )
        self._node = pyuavcan.application.make_node(node_info, REGISTER_FILE)
        self._node.heartbeat_publisher.mode = uavcan.node.Mode_1_0.OPERATIONAL
        self._node.heartbeat_publisher.vendor_specific_status_code = self.node_id
        self._node.start()


    async def _run(self) -> None:
        """
        The main method that runs the business logic.
        """
        await self._start_pub_and_sub()
        while True:
            await asyncio.sleep(10)

    async def _start_pub_and_sub(self):
        """
        Initialize all subscribers and publishers which are avaliable on the destination node.
        """

        self.subs = {
            "heartbeat"     : HearbeatSubscriber(self._node),
            "setpoint"      : SetpointSubscriber(self._node),
            "readiness"     : ReadinessSubscriber(self._node),
        }

        self.pubs = {
            "dynamics"      : DynamicsPublisher(self._node),
            "power"         : PowerPublisher(self._node),
        }

        for sub in self.subs:
            self.subs[sub].init()


    def _close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


async def main():
    kotletas = [
        KotletaMock(node_id=50, esc_idx=0),
        KotletaMock(node_id=51, esc_idx=1),
        KotletaMock(node_id=52, esc_idx=2),
        KotletaMock(node_id=53, esc_idx=3),
    ]
    for kotleta in kotletas:
        asyncio.create_task(kotleta._main())

    # log smth periodically
    while True:
        await asyncio.sleep(1)
        setpoints = []
        readiness = []
        for kotleta in kotletas:
            setpoints.append(kotleta.subs["setpoint"].value[kotleta.esc_idx])
            readiness.append(kotleta.subs["readiness"].value)
        print("setpoints={}, readiness={}".format(setpoints, readiness))

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    asyncio.run(main())
