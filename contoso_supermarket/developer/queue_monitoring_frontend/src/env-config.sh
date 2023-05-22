#!/bin/sh
# line endings must be \n, not \r\n ! Use LF and not CRLF!
# dynamically converts the .env file to a javascript object
echo "window._env_ = {" > /usr/share/nginx/html/env-config.js
awk -F '=' '{ gsub(/"/, "", $2); print $1 ": \"" (ENVIRON[$1] ? ENVIRON[$1] : $2) "\"," }' /usr/share/nginx/html/.env >> /usr/share/nginx/html/env-config.js
echo "}" >> /usr/share/nginx/html/env-config.js