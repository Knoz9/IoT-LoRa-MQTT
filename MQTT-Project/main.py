from machine import Pin
import utime
import time
from machine import PWM
from mqtt import MQTTClient_lib
import machine
import pycom
# from mqtt import MQTTClient_lib as MQTTClient
from network import WLAN

def sub_cb(topic, msg):
   print(msg)


def startup():
    global msg, ch, greenLED, redLED, yellowLED, pRedLED, pGreenLED, p2
    global tim, count, time1, time2, tlights, wlan, client, pYellowLED

    msg = "0"
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect("Iphone", auth=(WLAN.WPA2, "12345678"), timeout=5000)


    while not wlan.isconnected():
        machine.idle()
    print("Connected to WiFi\n")


    client = MQTTClient_lib("1", "io.adafruit.com",user="kenozzz", password="aio_Tegc75Mo6o0AAdHRqNEfJB9gE2RP", port=1883)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic='kenozzz/feeds/ddd')
    client.publish(topic='kenozzz/feeds/ddd', msg=msg)

    pYellowLED = Pin("P12", mode=Pin.OUT)
    greenLED = Pin("P8", mode=Pin.OUT)
    redLED = Pin("P9", mode=Pin.OUT)
    yellowLED = Pin("P7", mode=Pin.OUT)
    pRedLED = Pin("P10", mode=Pin.OUT)
    pGreenLED = Pin("P6", mode=Pin.OUT)
    p2 = Pin("P5")  # Pin Y2 with timer 8 Channel 2
    tim = PWM(0, frequency=300)
    ch = tim.channel(0, duty_cycle=0.5, pin=p2)
    pRedLED.value(1)
    greenLED.value(1)
    count = 0
    time1 = 0
    time2 = (utime.ticks_ms()) - 15000
    tlights = False

def beeping(t,s,t2): # Beeping with three variables. t = how many times to play, s = how fast, t2 = sleep time every loop
    for i in range(0,t):
        for i in beep:
            if i == 0:
                ch.duty_cycle(0)
                time.sleep(t2)
            else:
                tim = PWM(0, frequency=i)
                ch.duty_cycle(0.5)
            time.sleep(s)


def reconnect():
    pycom.heartbeat(False)
    pycom.rgbled(0x7f0000)
    time.sleep(1)
    wlan.connect("Ajfån 11 Pro", auth=(WLAN.WPA2, "12345678"), timeout=15000)
    while not wlan.isconnected():
        machine.idle()
    time.sleep(1)
    client.connect()
    client.subscribe(topic='kenozzz/feeds/ddd')
    client.publish(topic='kenozzz/feeds/ddd', msg=msg)
    pycom.heartbeat(True)


def traffic_stop():
    global msg
    msg = "1"
    beeping(2,0.15,1)
    greenLED.value(0)
    yellowLED.value(1)
    beeping(3,0.15,1)
    yellowLED.value(0)
    redLED.value(1)
    beeping(2,0.15,1)


def pedestrians_go():
    global msg
    if not wlan.isconnected():
        reconnect()
    client.publish(topic='kenozzz/feeds/ddd', msg="Pedestrians Go")
    client.publish(topic='kenozzz/feeds/ddd', msg="1")
    beeping(1,0.15,1)
    pYellowLED.value(0)
    pRedLED.value(0)
    pGreenLED.value(1)
    print("Cross the road!")
    beeping(80,0.05,0)


def pedestrians_stop():
    global msg
    msg = "0"
    beeping(10,0.10,0)
    client.publish(topic='kenozzz/feeds/ddd', msg="Pedestrians Stop")
    print("Red! Stop crossing!")
    if not wlan.isconnected():
        reconnect()
    msg = "0"
    client.publish(topic='kenozzz/feeds/ddd', msg="0")
    beeping(6,0.10,0)
    pGreenLED.value(0)
    pRedLED.value(1)


def traffic_ready():
    client.publish(topic='kenozzz/feeds/ddd', msg="Traffic Ready")
    global time2,tlights
    beeping(5,0.15,1)
    yellowLED.value(1)
    beeping(1,0.15,1)
    redLED.value(0)
    yellowLED.value(0)
    client.publish(topic='kenozzz/feeds/ddd', msg="Traffic Go")
    greenLED.value(1)
    tlights = False
    time2 = utime.ticks_ms()



def buttonEventCallback(argument):
    global count
    global time1
    global time2
    global tlights
    time1 = utime.ticks_ms()
    if time1 - time2 > 15000:
        if tlights == False:
            pYellowLED.value(1)
            print("Traffic is stopping...")
            client.publish(topic='kenozzz/feeds/ddd', msg="Traffic is stopping")
            count += 1
            tlights = True
        else:
            print("Button Already Pressed!")
    else:
        pYellowLED.value(1)
        cooldown = round(((time1 - time2 - 15000) * -1) / 1000)
        print("Button pressed! Waiting for cooldown:", cooldown, "seconds") # This queues up the press but waits 15 sec because
        # it just turned red. This is how it works irl
        time.sleep(15)
        print("Traffic is stopping...")
        tlights = True

startup()

beep = [1500, 0]
buttonPin = Pin('P11', mode=Pin.IN, pull=None)
buttonPin.callback(Pin.IRQ_FALLING, buttonEventCallback)

while True:
    if not wlan.isconnected():
        reconnect()
    if tlights == True:
        traffic_stop()
        pedestrians_go()
        pedestrians_stop()
        traffic_ready()
    else:
        beeping(1,0.15,1) # traffic go