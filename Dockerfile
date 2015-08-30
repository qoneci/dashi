FROM debian:8.1
MAINTAINER Alexander Brandstedt

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y \
        nodejs-legacy \
        gcc \
        npm \
        libyaml-dev \
        python-setuptools \
        python-pip \
        python-dev

RUN mkdir /opt/web
COPY . /opt/web
WORKDIR /opt/web

RUN npm install -g bower
RUN bower install --allow-root
RUN pip install -r requirements.txt

EXPOSE 3000
CMD python server.py
