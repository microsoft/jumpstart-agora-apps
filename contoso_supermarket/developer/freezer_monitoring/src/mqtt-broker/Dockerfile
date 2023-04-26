FROM eclipse-mosquitto

COPY entrypoint.sh /entrypoint.sh
COPY mosquitto.conf /mosquitto.conf
COPY mqtt_passwd /mqtt_passwd
COPY Baltimore.pem /Baltimore.pem
# ENTRYPOINT ["sh", "/entrypoint.sh"]
# CMD ["/usr/sbin/mosquitto","-c","/jumpstart-config.conf"]
ENTRYPOINT ["/usr/sbin/mosquitto"]


