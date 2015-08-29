# dashi

Jenkins Dashboard to display test results in cards. frontend written in React, current backend written i python

install
------
```bash
$ pip install -r requirements.txt
$ npm install -g bower
$ bower install
```

copy the example config to config.yaml and configure it to to your jenkins. point to a redis host
```bash
$ cp example.config.yaml config.yaml
```

run
---
```bash
python server.py
```

you can access the webUI on http://\<host\>:3000
