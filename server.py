#!/usr/bin/env python
import json
import yaml
import multiprocessing
from flask import Flask, Response, request
from dashi.util import jenkinsData, redisPoller, jobPoller, redisPool

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
configFile = file('config.yaml', 'r')
config = yaml.load(configFile)


@app.route('/api/result', methods=['GET'])
def result_handler():
    if request.method == 'GET':
        _redis = redisPoller(config, redis_pool)
        result = _redis.get('jenkins-result')
        if not result:
            print 'no redis data found!'
            _jenkins_data = jenkinsData(config)
            result = _jenkins_data.getLastResult()

        resp = Response(
            json.dumps(result),
            mimetype='application/json',
            headers={'Cache-Control': 'no-cache'}
        )
        return resp


def app_service():
    app.run(
        port=config['server']['port'],
        debug=bool(config['server']['port']),
        host='0.0.0.0'
    )


if __name__ == '__main__':
    redis_pool = redisPool(config)
    jobs = jobPoller(config, redis_pool)
    poller = multiprocessing.Process(
        name='jenkins_poller_service',
        target=jobs.jenkins
    )
    poller.daemon = False
    poller.start()
    app_service()
