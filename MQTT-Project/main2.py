from machine import Pin
import time
from machine import PWM
from mqtt import MQTTClient_lib
import machine
# from mqtt import MQTTClient_lib as MQTTClient
from network import WLAN
import pycom

def reconnect():
    pycom.heartbeat(False)
    pycom.rgbled(0x7f0000)
    time.sleep(2)
    wlan.connect("Iphone", auth=(WLAN.WPA2, "12345678"), timeout=15000)
    while not wlan.isconnected():
        machine.idle()
    time.sleep(0.5)
    client.connect()
    client.subscribe(topic='kenozzz/feeds/ddd')
    pycom.heartbeat(True)


Off = "b'OFF'"
On = "b'ON'"

x = "OFF"
val = False
def sub_cb(topic, msg):
    global x
    if "1" in msg:
        x = "ON"
    elif "0" in msg:
        x = "OFF"
    else:
        print(msg)

wlan = WLAN(mode=WLAN.STA)
wlan.connect("Ajfån 11 Pro", auth=(WLAN.WPA2, "12345678"), timeout=5000)

while not wlan.isconnected():
    machine.idle()
print("Connected to WiFi\n")

client = MQTTClient_lib("2", "io.adafruit.com",user="moayad", password="aio_EliC18Hy8zp6xGyktGRHneM2o4qv", port=1883)
client.connect()
client.set_callback(sub_cb)
client.subscribe(topic='kenozzz/feeds/ddd')
pRedLED = Pin("P7", mode=Pin.OUT)
pGreenLED = Pin("P6", mode=Pin.OUT)
count = 0
client.check_msg()
while True:
    if not wlan.isconnected():
        reconnect()
    client.check_msg()
    if x == "ON":
        pRedLED.value(0)
        pGreenLED.value(1)
        time.sleep(0.2)
    elif x == "OFF":
        pRedLED.value(1)
        pGreenLED.value(0)
        time.sleep(0.2)
    else:
        time.sleep(0.2)
