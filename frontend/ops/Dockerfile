# Default values build args
ARG application_endpoint
ARG frontend_port=8082
ARG backend_port=8083
ARG host=localhost
ARG backend_endpoint=/ws

FROM node as build-stage

RUN echo "${application_endpoint}, ${frontend_port}, ${backend_port}, ${host}, ${backend_endpoint}"

ARG application_endpoint
ARG host
ARG backend_port
ARG backend_endpoint

ENV APPLICATION_ENDPOINT=${application_endpoint}
ENV VITE_BACKEND_WEBSOCKET_URL=ws://${host}:${backend_port}${application_endpoint}${backend_endpoint}

WORKDIR /app
COPY ./ .
RUN npm install
RUN npm run build

FROM nginx:alpine as production-stage

ARG application_endpoint
ARG backend_port
ARG backend_endpoint
ARG frontend_port

ENV APPLICATION_ENDPOINT=${application_endpoint}
ENV BACKEND_ENDPOINT=${backend_endpoint}
ENV BACKEND_URL=host.docker.internal:${backend_port}
ENV FRONTEND_PORT=${frontend_port}

RUN echo "${APPLICATION_ENDPOINT}, ${BACKEND_ENDPOINT}, ${BACKEND_URL}, ${FRONTEND_PORT}"

RUN apk add busybox-extras
RUN rm /etc/nginx/conf.d/default.conf
ADD ./ops/templates/default.conf.template /etc/nginx/templates/default.conf.template
# COPY ./cert.pem /cert.pem // Future potential SSL build, for now serve this behind an SSL proxy server
# COPY ./key.pem /key.pem
WORKDIR /app
COPY --from=build-stage /app/dist /app
