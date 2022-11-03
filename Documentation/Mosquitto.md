# Mosquitto user guide

ssh into pi `ssh pi@ipaddress`
if config gives ip address. 
not a headless setup the pi works as the broker

publishing : `mosquitto_pub` -t (topic/thingy) -m "message"
subscribinig : `mosqutito_sub` -t (topic/thingy)

mosquitto -d to reset or start the mosquitto daemon