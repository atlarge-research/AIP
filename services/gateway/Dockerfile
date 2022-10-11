FROM node:16 as build

WORKDIR /code

COPY ./frontend /code/

RUN npm ci
RUN npm run build

FROM nginx:latest as server

COPY ./gateway/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /code/build /usr/share/nginx/html

EXPOSE 8000