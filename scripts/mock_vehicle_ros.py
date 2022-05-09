#!/usr/bin/env python3.7
import rospy
import asyncio
from mock_vehicle import CyphalNodeCreator

from std_msgs.msg import Bool, Float32
from sensor_msgs.msg import Imu, Joy, MagneticField, NavSatFix


class BaseComponent:
    def __init__(self) -> None:
        pass


class EscFeedbackComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        self.esc_idx = params["esc_idx"]
        creator = CyphalNodeCreator()
        self.esc_node = creator.create_node("esc", 50 + params["esc_idx"], params)
        self.esc_node.init()


class EscGroupComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        super().__init__()
        actuators_topic = params["actuators_topic"]
        arm_topic = params["arm_topic"]

        self._actuators_msg = Joy()
        self._arm_msg = Bool()
        self.nested_components = []
        for esc_idx in range(params["esc_amount"]):
            params["esc_idx"] = esc_idx
            self.nested_components.append(EscFeedbackComponent(params))
        self.ros_setpoint_pub = rospy.Publisher(actuators_topic, Joy, queue_size=10)
        self.ros_readiness_pub = rospy.Publisher(arm_topic, Bool, queue_size=10)
        self.nested_components[0].esc_node._subs["setpoint"].register_callback(self._cyphal_actuator_cb)
        self.nested_components[0].esc_node._subs["readiness"].register_callback(self._cyphal_readiness_cb)

    def get_setpoint(self):
        return self._actuators_msg.axes

    def get_readiness(self):
        return self._arm_msg.data

    def _cyphal_actuator_cb(self, cyphal_msg):
        self._actuators_msg.axes = cyphal_msg.value
        self.ros_setpoint_pub.publish(self._actuators_msg)

    def _cyphal_readiness_cb(self, cyphal_msg):
        self._arm_msg.data = cyphal_msg.value

class BaroComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        super().__init__()
        rospy.Subscriber(params["temperature_topic"], Float32, self._ros_static_temperature_cb)
        rospy.Subscriber(params["pressure_topic"],    Float32,    self._ros_static_pressure_cb)
    def _ros_static_temperature_cb(self, msg):
        pass
    def _ros_static_pressure_cb(self, msg):
        pass


class MagComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        super().__init__()
        rospy.Subscriber(params["mag_topic"], MagneticField, self._ros_mag_cb)
    def _ros_mag_cb(self, msg):
        pass


class GpsComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        super().__init__()
        rospy.Subscriber(params["gps_topic"], NavSatFix, self._ros_gps_cb)
    def _ros_gps_cb(self, msg):
        pass

class ImuComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        super().__init__()
        rospy.Subscriber(params["imu_topic"], Imu, self._ros_imu_cb)
    def _ros_imu_cb(self, msg):
        pass


class AirDataComponent(BaseComponent):
    def __init__(self, params=None) -> None:
        super().__init__()
        rospy.Subscriber(params["air_topic"], Float32, self._ros_static_pressure_cb)
    def _ros_static_pressure_cb(self, msg):
        pass


class ComponentCreator:
    COMPONENT_TYPE_BY_NAME = {
        "esc_feedback"  : EscFeedbackComponent,
        "esc_group"     : EscGroupComponent,
        "baro"          : BaroComponent,
        "mag"           : MagComponent,
        "gps"           : GpsComponent,
        "imu"           : ImuComponent,
        "air"           : AirDataComponent,
    }
    def __init__(self) -> None:
        pass

    def create_component(self, name, params=None):
        component = None
        if name in ComponentCreator.COMPONENT_TYPE_BY_NAME:
            component = ComponentCreator.COMPONENT_TYPE_BY_NAME[name](params)
        return component


class QuadcopterWithoutSensorsAirframe:
    def __init__(self) -> None:
        self.prev_log_time = rospy.get_time()
        creator = ComponentCreator()
        self.components = [
            creator.create_component("esc_group", {
                "esc_amount"        : 4,
                "feedback_reg"      : "feedback",
                "power_reg"         : "power",
                "status_reg"        : "status",
                "dynamcis_reg"      : "dynamcis",
                "setpoint_reg"      : "setpoint",
                "readiness_reg"     : "readiness",
                "esc_status_topic"  : "uav/esc_status",
                "actuators_topic"   : "/uav/actuators",
                "arm_topic"         : "/uav/arm",
            })
        ]

    def log(self):
        crnt_time_ms = rospy.get_time()
        if crnt_time_ms > self.prev_log_time + 0.1:
            sp = self.components[0].get_setpoint()
            READINESS_TO_STR = {
                0   : "SLEEP",
                1   : "INVALID",
                2   : "STANDBY",
                3   : "ENGAGED",
            }
            readiness = self.components[0].get_readiness()
            rospy.logwarn(f"readiness={READINESS_TO_STR[readiness]}, sp={sp}")
            self.prev_log_time = rospy.get_time()


class QuadcopterAirframe(QuadcopterWithoutSensorsAirframe):
    def __init__(self) -> None:
        super().__init__()
        creator = ComponentCreator()
        self.components.append(creator.create_component("baro", {
                "pressure_reg"      : "baro_pressure",
                "temperature_reg"   : "baro_temperature",
                "status_reg"        : "baro_status",
                "pressure_topic"    : "/uav/static_pressure",
                "temperature_topic" : "/uav/static_temperature",
            }))
        self.components.append(creator.create_component("mag", {
                "data_reg"          : "mag_data",
                "status_reg"        : "mag_status",
                "mag_topic"         : "/uav/mag",
            }))
        self.components.append(creator.create_component("gps", {
                "point_reg"         : "gps_point",
                "time_reg"          : "gps_time",
                "heartbeat_reg"     : "gps_heartbeat",
                "status_reg"        : "gps_status",
                "yaw_reg"           : "gps_yaw",
                "gps_topic"         : "/uav/gps",
            }))


class StandardVtolAirframe(QuadcopterAirframe):
    def __init__(self) -> None:
        super().__init__()
        creator = ComponentCreator()
        self.components.append(creator.create_component("air", {
                "dpres_reg"         : "air_dpres",
                "temperature_reg"   : "air_temperature",
                "air_topic"         : "/uav/raw_air_data",
        }))
        # todo: add servo group
        # todo: add internal combustion engine
        # todo: add fuel tank

async def main():
    rospy.init_node('vehicle_ros', anonymous=True)
    airframe = QuadcopterWithoutSensorsAirframe()
    while not rospy.is_shutdown():
        rospy.sleep(0.001)
        await asyncio.sleep(0.001)
        airframe.log()

if __name__ == "__main__":
    asyncio.run(main())
