FROM eclipse-mosquitto

COPY mosquitto.conf /mosquitto.conf
COPY DigiCertGlobalRootG2.crt.pem /DigiCertGlobalRootG2.crt.pem
# CMD ["/usr/sbin/mosquitto","-c","/jumpstart-config.conf"]
ENTRYPOINT ["/usr/sbin/mosquitto"]