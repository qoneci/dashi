#!/usr/bin/env python
import requests
import json
from urlparse import urlparse
from datetime import timedelta


class jenkinsResults(object):

    def __init__(self, config):
        requests.packages.urllib3.disable_warnings()
        self.config = config
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
