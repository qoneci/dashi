#!/usr/bin/env python
import json
import yaml
import requests

"""
data structure that should be returned
var data = [
  {name: "selenium mobile integration", pass: 13, fail: 0},
  {name: "selenium mobile mainSite", pass: 10, fail: 1},
  {name: "selenium desktop integration", pass: 23, fail: 2},
  {name: "selenium desktop mainSite", pass: 11, fail: 4},
  {name: "selenium desktop game flash", pass: 21, fail: 5},
]
"""


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

    def jobShortenName(self, job):
        short = job.replace('-', ' ').split()
        return ' '.join(short[2:])

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
                passCount = (totalCount - failCount)
                self.data.append({"name": shortName, "pass": passCount, "fail": failCount, "build": buildNum})
        return self.data

result = testResults().getLastResult()
print json.dumps(result, indent=4, sort_keys=True)
