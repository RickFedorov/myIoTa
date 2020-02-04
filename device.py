from typing import List, Any

import paho.mqtt.client as mqtt
import ast
from lib import schedule
from datetime import datetime
import time
from logs.logger import logger


class Device:
    sub_devices: List[Any]

    def __init__(self, name, client, **kwargs):
        """

        :type client: IOTA
        """
        self.name = name
        self.state_topic = "zigbee2mqtt/{}".format(name)
        self.availability_topic = "zigbee2mqtt/bridge/state"
        self.cmd_topic = self.state_topic + "/cmd"
        self.client = client
        self.client.subscribe(self.state_topic)
        self.client.subscribe(self.cmd_topic)  # email cmd

        self.payload = []
        self.battery = 0

        self.on_init(**kwargs)

    # method will be used by child on time of init
    def on_init(self, **kwargs):
        pass

    def decode_payload(self, payload):
        return ast.literal_eval(payload.decode("utf-8"))

    def on_message(self, msg):
        if msg.topic == self.state_topic:
            self.payload = self.decode_payload(msg.payload)
            self.do_action()
        if msg.topic == self.cmd_topic:
            self.payload = self.decode_payload(msg.payload)
            self.do_cmd_action()

    # method will be used by child to do its action
    def do_action(self):
        pass

    def do_cmd_action(self):
        pass


class RemoteControler(Device):

    def do_action(self):
        try:
            if self.payload["action"] == "toggle":
                self.client.publish("Test/Outlet", "power")

            elif self.payload["action"] == "brightness_up_click":
                self.client.publish("Test/Outlet", "up")

            elif self.payload["action"] == "brightness_down_click":
                self.client.publish("Test/Outlet", "down")

            elif self.payload["action"] == "arrow_left_click":
                self.client.publish("Test/Outlet", "left")

            elif self.payload["action"] == "arrow_right_click":
                self.client.publish("Test/Outlet", "right")

            else:
                pass

        except KeyError:
            print("Exception in action {}".format(self.name))
        except Exception as inst:
            print("Exception in action {}".format(self.name))
            logger.exception("Exception in action {}".format(self.name))


# wifi router power off
class PowerOutlet(Device):
    def on_init(self, **kwargs):
        schedule.every().day.at("03:00").do(self.turn_off)
        schedule.every().day.at("05:50").do(self.turn_on)
        # schedule.every(10).seconds.do(self.turn_off)
        # schedule.every(10).seconds.do(self.turn_on)
        schedule.run_continuously()

    def do_cmd_action(self):
        try:
            if self.payload["action"] == "restart":
                self.restart()
                self.client.email.send_mail(self.cmd_topic, '{"response":"Restart completed"}')
            else:
                pass
        except KeyError:
            print("Exception in action {}".format(self.name))
        except Exception as inst:
            print("Exception in action {}".format(self.name))
            logger.exception("Exception in action {}".format(self.name))

    def turn_off(self):
        print("Turning off: " + datetime.now().strftime("%H:%M:%S"))
        self.client.publish(self.state_topic + "/set", "OFF")

    def turn_on(self):
        print("Turning on: " + datetime.now().strftime("%H:%M:%S"))
        self.client.publish(self.state_topic + "/set", "ON")

    def restart(self):
        self.turn_off()
        time.sleep(60)
        self.turn_on()


# Light bulb
class LighBulb(Device):
    pass


# motionsensor hall
class MotionSensorHall(Device):
    sub_devices: List[Device]

    def __init__(self, name, client: mqtt.Client, **kwargs):
        self.sub_devices = []
        if "sub_devices" in kwargs:
            self.sub_devices = kwargs["sub_devices"]

        self.last_motion = datetime.fromtimestamp(0)

        super().__init__(name, client, **kwargs)

    def on_init(self, **kwargs):
        pass

    def do_action(self):
        try:
            if not self.sub_devices:  # no devices
                return

            if self.payload["motion"] == "ON":
                if self.last_motion + 30 < datetime.now():
                    self.send_command("ON")

                self.last_motion = datetime.now()

            else:
                pass

        except Exception as inst:
            print("Exeption in motion {}".format(self.name))

    def send_command(self, command):
        for device in self.sub_devices:
            self.client.publish(device.state_topic + "/set", command)
