FROM nginxinc/nginx-unprivileged:1.29.3-alpine3.22-slim AS nginx_base
USER root
COPY ./certs/server.crt ./certs/server.key /etc/nginx/certs/
RUN chown root:nginx /etc/nginx/certs/* \
&& chmod 640 /etc/nginx/certs/*
USER nginx
COPY ./ingress/default.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 8000

FROM nginx_base AS dev
ENV GAMEMASTER_UPSTREAM="gamemaster:8000"

FROM nginx_base AS test
ENV GAMEMASTER_UPSTREAM="host.docker.internal:50000"
