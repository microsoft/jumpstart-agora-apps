#!/bin/sh

PASSWDFILE=passwd

if [ -f $PASSWDFILE ]; then
    echo "converting password file"
    mosquitto_passwd -U $PASSWDFILE
fi

exec "$@"