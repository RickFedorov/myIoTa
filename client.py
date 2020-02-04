import threading
import paho.mqtt.client as mqtt
from device import Device, RemoteControler, PowerOutlet, LighBulb, MotionSensorHall
from connect import Email2Mqtt, Mqtt2Email

class IOTA(mqtt.Client):

    def __init__(self):
        super().__init__()
        self.server = "192.168.1.10"
        self.port = 1883
        self.keepalive = 60
        self.devices = []
        self.email_monitor = Email2Mqtt(self)
        self.email = Mqtt2Email(self)

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.process_message(msg)
        if msg.topic == "$SYS/broker/uptime":
            self.publish("Test/test3", "OK")


    def process_message(self, msg):
        for device in self.devices:
            device.on_message(msg)

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def init_devices(self):
        self.devices.append(RemoteControler("remote_control1", self))
        self.devices.append(PowerOutlet("control_outlet1", self))

        light_group_hall = []
        light_group_hall.append(LighBulb("light_bulb1", self))
        light_group_hall.append(LighBulb("light_bulb2", self))

        self.devices = self.devices + light_group_hall

        self.devices.append(MotionSensorHall("motion_sensor_hall",self, sub_devices=light_group_hall))

    def init_email(self):
        x = threading.Thread(target=self.email_monitor.run, args=(2,))
        x.start()

    def run(self):
        self.connect(self.server, self.port, self.keepalive)
        self.subscribe("$SYS/broker/uptime")
        self.init_devices()
        self.init_email()

        rc = 0
        while rc == 0:
            rc = self.loop_forever()
        return rc

