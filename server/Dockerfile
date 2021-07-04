FROM node:16 as build
WORKDIR /code
COPY ./client /code/
RUN npm ci
RUN npm run build

FROM nginx:1.21 as server
COPY ./server/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /code/build /usr/share/nginx/html
EXPOSE 8000