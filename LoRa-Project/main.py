import pycom
from network import LoRa
import socket
import time
import ubinascii
import struct
import utime
from machine import Pin
from dth import DTH


# Initial Pin setup:

pirPin = Pin('P20', mode=Pin.IN, pull = Pin.PULL_UP)
pycom.heartbeat(False)
pycom.rgbled(0x000008) # blue
th = DTH('P10',0)
time.sleep(2)


lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
print("DevEUI: " + ubinascii.hexlify(lora.mac()).decode('utf-8').upper())

# Over the air authentication:

app_eui = ubinascii.unhexlify('70B3D57ED00308BF')
app_key = ubinascii.unhexlify('425A63608791C76C7DA92BB5CDDD1F0F')

# Join:
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

while not lora.has_joined():
    print('Not yet joined...')
    time.sleep(3)

print("Joined network")
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)


def uplink(): # This is the uplink. It uploads temp and humidity ALWAYS, but 
    # Motion only when motion is present. Motion value 0 is lowest, whilst 10 is much motion.
    # Also, it sends seperately and binds to different port to differenciate the values.
    global count,rt,rh
    s.bind(1)
    s.setblocking(True)
    s.send(struct.pack('>B', rt))
    s.bind(2)
    s.send(struct.pack('>B', rh)) # I send this twice because the ThingSpeak Api rejects it
    time.sleep(5)  # due to the requests sending too fast. I figured if i send it twice.
    s.send(struct.pack('>B', rh)) # It always works.
    s.setblocking(False)
    if count > 0:
        time.sleep(2)
        s.setblocking(True)
        s.bind(3)
        s.send(struct.pack('>B', count))
        s.bind(3)
        time.sleep(2)
        s.send(struct.pack('>B', count)) # send this twice too.
        s.setblocking(False)
        time.sleep(2)


def readtemp():
    global rt
    global rh
    result = th.read()
    if result.is_valid():
        rh = int(result.humidity) # Humidity is 0-100, so this is fine.
        rt = int(result.temperature) + 40 # +40 to cover from -40 to 216 degrees


# Execution:
t = utime.ticks_ms()
count = 0
while True:
    readtemp()
    if pirPin() == 1: # Checks for motion every second, and if motion is present it adds 1.
        if count != 10:
            count = count + 1
    if utime.ticks_ms() - t > 30000: # Sends data every 30 seconds
        print((rt - 40), rh, count)
        uplink()
        pycom.rgbled(0x001000) # green color to signal successful uplink
        time.sleep(0.1)
        pycom.rgbled(0x000000)
        count = 0 # Reset count on motion sensor
        t = utime.ticks_ms()
    time.sleep(1) # Updates data every second