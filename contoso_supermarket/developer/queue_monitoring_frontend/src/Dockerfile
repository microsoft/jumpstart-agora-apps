# build environment
FROM node:16.19.0-alpine as build
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# production environment
FROM nginx:stable-alpine
RUN apk add --update bash
COPY .env /usr/share/nginx/html
COPY ./nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/build /usr/share/nginx/html
COPY ./env-config.sh /docker-entrypoint.d/env-config.sh
RUN chmod +x /docker-entrypoint.d/env-config.sh
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]