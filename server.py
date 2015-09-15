#!/usr/bin/env python
import json
import yaml
import requests
import redis
import multiprocessing
from time import sleep
from ast import literal_eval
from datetime import timedelta
from urlparse import urlparse
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
configFile = file('config.yaml', 'r')
config = yaml.load(configFile)


class testResults():

    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        self.host = config['jenkins']['host']
        self.user = config['jenkins']['user']
        self.token = config['jenkins']['token']
        self.jobs = config['jenkins']['jobs']
        self.data = []

    def lastBuild(self, job, value):
        found = False
        url = 'https://%s:%s@%s/job/%s/lastBuild/api/json' % (self.user,
                                                              self.token,
                                                              self.host,
                                                              job)
        req = requests.get(url, verify=False)
        if req.status_code == 200:
            data = json.loads(req.text)
            found = data[value]
        return found

    def getBuildValues(self, job, buildId):
        url = 'https://%s:%s@%s/job/%s/%s/api/json' % (self.user,
                                                       self.token,
                                                       self.host,
                                                       job,
                                                       buildId)
        req = requests.get(url, verify=False)
        if req.status_code == 200:
            data = json.loads(req.text)
            result = data['result']
            building = data['building']
            return {'result': result, 'building': building}
        else:
            return False

    def lastCompleteBuild(self, job):
        buildWithResult = False
        buildId = self.lastBuild(job, 'number')
        while buildWithResult is False:
            buildData = self.getBuildValues(job, buildId)
            building = buildData.get('building')
            if not building:
                buildWithResult = True
            else:
                buildId = buildId - 1

        if buildWithResult:
            url = 'https://%s:%s@%s/job/%s/%s/api/json' % (self.user,
                                                           self.token,
                                                           self.host,
                                                           job,
                                                           buildId)
            req = requests.get(url, verify=False)
            if req.status_code == 200:
                data = json.loads(req.text)
                return data
        else:
            return False

    def getLastResult(self):
        for jobData in self.jobs:
            job = jobData.get('job')
            shortName = jobData.get('short')
            data = self.lastCompleteBuild(job)
            if data:
                buildUrl = urlparse(data['url'])
                buildLink = '%s://%s%s' % (buildUrl.scheme, self.host, buildUrl.path)
                buildNum = data['number']
                buildResult = data['result']
                buildDurationInSec = (data['duration'] / 1000)

                if ((buildResult == 'ABORTED') or (buildResult == 'FAILURE')):
                    try:
                        totalCount = data['actions'][-1]['totalCount']
                        failCount = data['actions'][-1]['failCount']
                    except KeyError:
                        totalCount = 0
                        failCount = 0
                else:
                    try:
                        totalCount = data['actions'][-1]['totalCount']
                        failCount = data['actions'][-1]['failCount']
                    except KeyError:
                        totalCount = 0
                        failCount = 0

                passCount = (totalCount - failCount)
                self.data.append(
                    {
                        "name": shortName,
                        "pass": passCount,
                        "fail": failCount,
                        "build": buildNum,
                        "result": buildResult,
                        "buildLink": buildLink,
                        "buildDurationInSec": str(timedelta(seconds=buildDurationInSec))
                    }
                )
        return self.data


@app.route('/api/result', methods=['GET'])
def result_handler():
    if request.method == 'GET':
        result = redis_get('jenkins-result')
        if not result:
            print 'no redis data found!'
            result = testResults().getLastResult()

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
        result = testResults().getLastResult()
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
