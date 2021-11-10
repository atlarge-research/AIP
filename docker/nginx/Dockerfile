FROM node:16 as node_packages

WORKDIR /code
COPY ./frontend/package.json .
COPY ./frontend/yarn.lock .
RUN yarn install --frozen-lockfile

FROM node:16 as build

WORKDIR /code
COPY --from=node_packages /code /code
COPY ./frontend .
RUN npm run build

FROM nginx:1.21 as server

COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /code/build /usr/share/nginx/html

EXPOSE 8000