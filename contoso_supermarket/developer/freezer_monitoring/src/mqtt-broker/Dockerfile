FROM eclipse-mosquitto

COPY entrypoint.sh /entrypoint.sh
COPY mosquitto.conf /mosquitto.conf
COPY mqtt_passwd /mqtt_passwd
COPY Baltimore.pem /Baltimore.pem
ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["/usr/sbin/mosquitto","-c","/mosquitto.conf"]



###############################################################
# DOCKER BUILD COMMANDS
# docker build -t js/mqtt-broker . ; ./Dockerrun.ps1
# docker build --progress=plain -t js/mqtt-broker .
# docker build --progress=plain --no-cache -t js/mqtt-broker .

# DOCKER RUN COMMAND
# docker run argument examples
# docker run 
# --hostname=my_test_machine 
# --mac-address makes dhcp assignment much easier!
# --mac-address=02:42:ac:11:00:03 
