#!/usr/bin/env python
import json
import yaml
import redis
import multiprocessing
from time import sleep
from ast import literal_eval
from flask import Flask, Response, request
from dashi.util import jenkinsResults

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
configFile = file('config.yaml', 'r')
config = yaml.load(configFile)


@app.route('/api/result', methods=['GET'])
def result_handler():
    if request.method == 'GET':
        result = redis_get('jenkins-result')
        if not result:
            print 'no redis data found!'
            _jenkins_data = jenkinsResults(config)
            result = _jenkins_data.getLastResult()

        resp = Response(
            json.dumps(result),
            mimetype='application/json',
            headers={'Cache-Control': 'no-cache'}
        )
        return resp


def run_web_service():
    app.run(
        port=config['server']['port'],
        debug=bool(config['server']['port']),
        threaded=True,
        host='0.0.0.0'
    )


def redis_connect():
    pool = redis.ConnectionPool(
        host=config['redis']['host'],
        port=int(config['redis']['port']),
        db=int(config['redis']['db'])
    )
    return pool


def redis_get(redis_key):
    r = redis.Redis(connection_pool=redis_pool)
    try:
        data_ttl = int(r.ttl(redis_key))
        if data_ttl >= 5:
            data = r.get(redis_key)
            string_to_dict = literal_eval(data)
            return string_to_dict
        else:
            return False
    except TypeError:
        return False


def run_jenkins_poller():
    r = redis.Redis(connection_pool=redis_pool)
    while True:
        sleep(10)
        print 'jenkins poll'
        _jenkins_data = jenkinsResults(config)
        result = _jenkins_data.getLastResult()
        r.set('jenkins-result', result, ex=40)


if __name__ == '__main__':
    redis_pool = redis_connect()
    poller = multiprocessing.Process(
        name='poller_service',
        target=run_jenkins_poller
    )
    poller.daemon = False

    web = multiprocessing.Process(
        name='web_service',
        target=run_web_service
    )
    web.daemon = False

    web.start()
    poller.start()
