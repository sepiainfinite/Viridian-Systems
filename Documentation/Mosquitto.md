# Mosquitto user guide

ssh into pi `ssh pi@ipaddress`
if config gives ip address. 
not a headless setup the pi works as the broker

publishing : `mosquitto_pub` -t esp32/qrPayload -m "message"
subscribing : `mosqutito_sub` -t (topic/thingy)mo

mosquitto -d to reset or start the mosquitto daemon

2464=p
ViridianSystemsAIM8888