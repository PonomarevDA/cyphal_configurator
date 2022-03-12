#!/usr/bin/env python3.7
import sys
import asyncio
import logging
import pyuavcan
import pathlib
from subscribers import SetpointSubscriber, ReadinessSubscriber, HearbeatSubscriber
from publishers import DynamicsPublisher, PowerPublisher, FeedbackPublisher, StatusPublisher
from datetime import datetime


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
            "heartbeat"         : HearbeatSubscriber(self._node),
            "setpoint"          : SetpointSubscriber(self._node),
            "readiness"         : ReadinessSubscriber(self._node),
        }

        dynamics_topic = "dynamics_{}".format(self.esc_idx + 1)
        power_topic = "power_{}".format(self.esc_idx + 1)
        feedback_topic = "feedback_{}".format(self.esc_idx + 1)
        status_topic = "status_{}".format(self.esc_idx + 1)

        try:
            self.pubs = {
                "dynamics"      : DynamicsPublisher(self._node, name=dynamics_topic),
                "power"         : PowerPublisher(self._node, name=power_topic),
                "feedback"      : FeedbackPublisher(self._node, name=feedback_topic),
                "status"        : StatusPublisher(self._node, name=status_topic),
            }

            self.pubs["power"].set_value(current=0.1  + 0.1*self.esc_idx,
                                         voltage=12.1 + 0.1*self.esc_idx)
            self.pubs["dynamics"].set_value(radian_per_second=10 + 10*self.esc_idx)
            self.pubs["status"].set_motor_temperature(273.2 + 10*self.esc_idx)

            for sub in self.subs:
                self.subs[sub].init()
        except Exception as ex:
            print("KotletaMock", self.esc_idx, ex)

    def _close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


def log_data(kotletas):
    setpoints = [0, 0, 0, 0]
    readiness = [0, 0, 0, 0]

    voltages = [0, 0, 0, 0]
    currents = [0, 0, 0, 0]

    crnt_sp_rx_counter = kotletas[0].subs["setpoint"].update_max_time_between_msgs()
    crnt_readiness_rx_counter = kotletas[0].subs["readiness"].update_max_time_between_msgs()

    for kotleta in kotletas:
        esc_idx = kotleta.esc_idx
        setpoints[esc_idx] = kotleta.subs["setpoint"].value[esc_idx]
        readiness[esc_idx] = kotleta.subs["readiness"].value
        voltages[esc_idx] = kotleta.pubs["power"].msg.value.voltage.volt
        currents[esc_idx] = kotleta.pubs["power"].msg.value.current.ampere



    print("{} {}={}, {}={}, {}={}, {}={}, {}/{}".format(\
            datetime.now().strftime("%H:%M:%S"),
            "sp", setpoints,
            "rd", readiness,
            "volt", voltages,
            "crnt", currents,
            crnt_sp_rx_counter, crnt_readiness_rx_counter,
        )
    )


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
        log_data(kotletas)

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    asyncio.run(main())
