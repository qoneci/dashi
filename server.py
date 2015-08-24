#!/usr/bin/env python
import json
import yaml
import requests
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))


class testResults():

    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        configFile = file('config.yaml', 'r')
        config = yaml.load(configFile)
        self.host = config['jenkins']['host']
        self.user = config['jenkins']['user']
        self.token = config['jenkins']['token']
        self.jobs = config['jenkins']['jobs']
        self.data = []

    def lastBuild(self, job, value):
        found = False
        url = 'https://%s:%s@%s/job/%s/lastBuild/api/json' % (self.user, self.token, self.host, job)
        req = requests.get(url, verify=False)
        if req.status_code == 200:
            data = json.loads(req.text)
            found = data[value]
        return found

    def getBuildValues(self, job, buildId):
        url = 'https://%s:%s@%s/job/%s/%s/api/json' % (self.user, self.token, self.host, job, buildId)
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
            result = buildData.get('result')
            building = buildData.get('building')
            if not (building or (result == 'ABORTED') or (result == 'FAILURE')):
                buildWithResult = True
            else:
                buildId = buildId - 1

        if buildWithResult:
            url = 'https://%s:%s@%s/job/%s/%s/api/json' % (self.user, self.token, self.host, job, buildId)
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
                # print json.dumps(data, indent=4, sort_keys=True)
                totalCount = data['actions'][-1]['totalCount']
                failCount = data['actions'][-1]['failCount']
                buildNum = data['number']
                buildDurationInSec = (data['duration'] / 1000)
                passCount = (totalCount - failCount)
                self.data.append(
                    {
                        "name": shortName,
                        "pass": passCount,
                        "fail": failCount,
                        "build": buildNum,
                        "buildDurationInSec": buildDurationInSec
                    }
                )
        return self.data


@app.route('/api/result', methods=['GET'])
def result_handler():
    if request.method == 'GET':
        result = testResults().getLastResult()
        resp = Response(
            json.dumps(result),
            mimetype='application/json',
            headers={'Cache-Control': 'no-cache'}
        )
        return resp

if __name__ == '__main__':
    app.run(
        port=3000,
        debug=True,
        threaded=True,
        host='0.0.0.0'
    )
