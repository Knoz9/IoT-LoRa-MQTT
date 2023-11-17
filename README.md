# My Wireless IoT Projects

## LoRa
LoRa is a low-power, long-range wireless communication technology used in IoT for distant device connectivity.

For my project, i used a LoPy4 development board to monitor and upload the temperature and humidity of a DHT11 Sensor. Just for fun, i also monitored a motion sensor and uploaded the amount of times it got triggered. This got uploaded to ThingsSpeak API, and then was displayed on a website.

## MQTT
MQTT is a lightweight messaging protocol for IoT, efficient in low-bandwidth or unstable networks, using a publish/subscribe model for data exchange.

For my project, i used two LoPy4 development boards to set up a traffic light. 

One of the boards was the "Main" controller and this board was responsible to check for the input (button press) and also changed the main traffic light from green to red.

The other board was listening for MQTT messages from the main board, and if it got one, we turned this light (Pedestrian light) to red. Then, it sends a "Ack" to the main board so that the main board knows that the 2nd board is linked up sucessfully.

[Live Demo](https://www.youtube.com/shorts/s_3gY6GyE5s)