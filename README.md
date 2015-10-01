# dashi

Jenkins Dashboard to display test results in cards. frontend written in React, current backend written i python

install
-------
```bash
$ pip install -r requirements.txt
$ npm install -g bower
$ bower install
```

copy the example config to config.yaml and configure it to to your jenkins. point to a redis host
```bash
$ cp example.config.yml config.yml
```

run from shell
--------------
```bash
$ python server.py
```

you can access the webUI on http://\<host\>:3000


docker build
------------
a docker container for the server.py will be built and tagged with dashi:web
```bash
$ ./docker-build.sh
```

docker run
----------
this will start a docker stack with the server.py in a container, redis and a haproxy
```bash
$ docker-compose up -d
```
