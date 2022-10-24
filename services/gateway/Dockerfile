FROM node:16 as build

WORKDIR /code

COPY ./frontend /code/

RUN yarn install --frozen-lockfile
RUN yarn build

FROM nginx:latest as server

COPY ./gateway/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /code/build /usr/share/nginx/html

EXPOSE 8000
