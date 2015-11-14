FROM mad01/dashi-base-dockerfile:latest
MAINTAINER Alexander Brandstedt

RUN mkdir /opt/web
COPY . /opt/web
WORKDIR /opt/web
RUN jsx -x jsx public/jsx public/js

EXPOSE 3000
CMD python server.py
