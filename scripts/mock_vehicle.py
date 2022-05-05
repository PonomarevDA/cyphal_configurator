#!/usr/bin/env python3.7
import sys
import asyncio
import logging
import pyuavcan
import pathlib
from subscribers import CyphalSubscriberCreator
from publishers import CyphalPublisherCreator
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


class BaseCyphalNode:
    """
    Each node should support at least following interface:
    type    PortId  Data type
    pub     7509    uavcan.node.Heartbeat.1.0
    pub     7510    uavcan.node.port.List.0.1
    """
    def __init__(self, node_id, params=None) -> None:
        self.node_id = node_id
        self.subs = {}
        self.pubs = {}

    def init(self):
        asyncio.create_task(self._main()) 

    async def _main(self) -> None:
        try:
            node_info = uavcan.node.GetInfo_1_0.Response(
                software_version=uavcan.node.Version_1_0(major=1, minor=0),
                name="vehicle_mock",
            )
            self._node = pyuavcan.application.make_node(node_info, REGISTER_FILE)
            self._node.heartbeat_publisher.mode = uavcan.node.Mode_1_0.OPERATIONAL
            self._node.heartbeat_publisher.vendor_specific_status_code = self.node_id
            self._node.start()
            await self._init_pub_and_sub()
            for sub in self.subs:
                self.subs[sub].init()
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._close()

    async def _init_pub_and_sub(self):
        pass

    def _close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


class EscCyphalNode(BaseCyphalNode):
    """
    Node specific interface
    type    PortId  Register    Data type                                           Pub rate
    sub     dyn     setpoint    reg.udral.service.actuator.common.sp.Scalar_0_1     ~200
    sub     dyn     readiness   reg.udral.service.common.Readiness_0_1              -20
    pub     dyn     feedback_x  reg.udral.service.actuator.common.Feedback_0_1      0.1
    pub     dyn     power_x     reg.udral.physics.electricity.PowerTs_0_1           0.1
    pub     dyn     status_x    reg.udral.service.actuator.common.Status_0_1        0.1
    pub     dyn     dynamics_x  reg.udral.physics.dynamics.rotation.PlanarTs_0_1    0.1
    """
    def __init__(self, node_id, params=None) -> None:
        super().__init__(node_id)
        self.esc_idx = params["esc_idx"]

    async def set_value(self, current, voltage, radian_per_second, temperature):
        self.pubs["power"].set_value(current=current, voltage=voltage)
        self.pubs["dynamics"].set_value(radian_per_second=radian_per_second)
        self.pubs["status"].set_motor_temperature(temperature)

    def get_setpoint(self):
        sp = self.subs["setpoint"].get_value()[self.esc_idx]
        return round(sp, 2) if sp is not None else None

    def get_readiness(self):
        return self.subs["readiness"].get_value()

    def get_voltage(self):
        voltage = self.pubs["power"].msg.value.voltage.volt
        return round(voltage, 1) if voltage is not None else None

    def get_current(self):
        current = self.pubs["power"].msg.value.current.ampere
        return round(current, 1) if current is not None else None

    async def _init_pub_and_sub(self):
        sub_creator = CyphalSubscriberCreator(self._node)
        self.subs = {
            "heartbeat" : sub_creator.create("heartbeat"),
            "setpoint"  : sub_creator.create("setpoint"),
            "readiness" : sub_creator.create("readiness"),
        }

        pub_creator = CyphalPublisherCreator(self._node)
        self.pubs = {
            "dynamics"  : pub_creator.create("dynamics", "dynamics_{}".format(self.esc_idx + 1)),
            "power"     : pub_creator.create("power",    "power_{}".format(self.esc_idx + 1)),
            "feedback"  : pub_creator.create("feedback", "feedback_{}".format(self.esc_idx + 1)),
            "status"    : pub_creator.create("status",   "status_{}".format(self.esc_idx + 1)),
        }


class CyphalNodeCreator:
    NODE_TYPE_BY_NAME = {
        "esc"           : EscCyphalNode,
        # "baro"          : BaroCyphalNode,
        # "mag"           : MagCyphalNode,
        # "gps"           : GpsCyphalNode,
        # "imu"           : ImuCyphalNode,
        # "air"           : AirCyphalNode,
    }
    def __init__(self) -> None:
        pass

    def create_node(self, name, node_id, params=None):
        component = None
        if name in CyphalNodeCreator.NODE_TYPE_BY_NAME:
            component = CyphalNodeCreator.NODE_TYPE_BY_NAME[name](node_id, params)
        return component


class QuadcopterSystem:
    def __init__(self) -> None:
        creator = CyphalNodeCreator()
        self.nodes = [
            creator.create_node("esc", node_id=50, params={"esc_idx" : 0}),
            creator.create_node("esc", node_id=51, params={"esc_idx" : 1}),
            creator.create_node("esc", node_id=52, params={"esc_idx" : 2}),
            creator.create_node("esc", node_id=53, params={"esc_idx" : 3}),
        ]

    def init(self):
        for node in self.nodes:
            node.init()

    async def set_values(self):
        await self.nodes[0].set_value(0.1, 12.1, 10.1, 273.2)
        await self.nodes[1].set_value(0.2, 12.2, 10.2, 274.2)
        await self.nodes[2].set_value(0.3, 12.3, 10.3, 275.2)
        await self.nodes[3].set_value(0.4, 12.4, 10.4, 276.2)

    def log_data_once(self):
        NUMBER_OF_ESC = 4
        escs = self.nodes[0:NUMBER_OF_ESC]

        print("{}. Total number of RX: {}/{}".format(
            datetime.now().strftime("%H:%M:%S"),
            escs[0].subs["setpoint"].get_number_of_rx_msgs(),
            escs[0].subs["readiness"].get_number_of_rx_msgs())
        )

        for esc in escs:
            print("- esc_{}: sp={}, rd={}, volt={}, crnt={},".format(
                esc.esc_idx + 1,
                esc.get_setpoint(),
                esc.get_readiness(),
                esc.get_voltage(),
                esc.get_current()))

async def main():
    quadcopter_system = QuadcopterSystem()
    quadcopter_system.init()
    await asyncio.sleep(1)
    await quadcopter_system.set_values()

    while True:
        await asyncio.sleep(2)
        quadcopter_system.log_data_once()

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    asyncio.run(main())
