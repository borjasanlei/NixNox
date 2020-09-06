FROM nginx:1.19-alpine

RUN rm /etc/nginx/conf.d/*
COPY nginx.conf /etc/nginx/conf.d

WORKDIR /nixnox_project

COPY . /nixnox_project/


