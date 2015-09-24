#!/usr/bin/env python
import requests
import json
import redis
from urlparse import urlparse
from datetime import timedelta
from ast import literal_eval
from time import sleep


class jenkinsData(object):

    def __init__(self, config):
        requests.packages.urllib3.disable_warnings()
        self.config = config
        self.host = config['jenkins']['host']
        self.user = config['jenkins']['user']
        self.token = config['jenkins']['token']
        self.jobs = config['jenkins']['jobs']
        self.data = []

    def lastCompleteBuild(self, job):
        url = 'https://%s:%s@%s/job/%s/lastCompletedBuild/api/json' % (self.user,
                                                                       self.token,
                                                                       self.host,
                                                                       job)
        req = requests.get(url, verify=False)
        if req.status_code == 200:
            data = json.loads(req.text)
            return data
        else:
            return False

    def getTestReport(self, job, buildNum):
        url = 'https://%s:%s@%s/job/%s/%s/testReport/api/json' % (self.user,
                                                                  self.token,
                                                                  self.host,
                                                                  job,
                                                                  buildNum)
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
                buildTestReuslt = self.getTestReport(job, buildNum)
                if ((buildResult == 'ABORTED') or (buildResult == 'FAILURE')):
                    if buildTestReuslt:
                        passCount = buildTestReuslt['passCount']
                        failCount = buildTestReuslt['failCount']
                    else:
                        print 'no test result found'
                        passCount = 0
                        failCount = 0
                else:
                    if buildTestReuslt:
                        passCount = buildTestReuslt['passCount']
                        failCount = buildTestReuslt['failCount']
                    else:
                        print 'no test result found'
                        passCount = 0
                        failCount = 0

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


def redisPool(config):
    pool = redis.ConnectionPool(
        host=config['redis']['host'],
        port=int(config['redis']['port']),
        db=int(config['redis']['db'])
    )
    return pool


class redisPoller(object):

    def __init__(self, config, redis_pool):
        self.config = config
        self.pool = redis_pool

    def get(self, redis_data_key):
        _redis = redis.Redis(
            connection_pool=self.pool
        )
        try:
            data_ttl = int(_redis.ttl(redis_data_key))
            if data_ttl >= 5:
                data = _redis.get(redis_data_key)
                string_to_dict = literal_eval(data)
                return string_to_dict
            else:
                return False
        except TypeError:
            return False


class jobPoller(object):

    def __init__(self, config, redis_pool):
        self.config = config
        self.redis_expire_time = int(self.config['redis']['expire_time'])
        self.jenkins_poll_interval = int(self.config['jenkins']['poll_interval'])
        self.pool = redis_pool

    def jenkins(self):
        _redis = redis.Redis(
            connection_pool=self.pool
        )
        while True:
            sleep(self.jenkins_poll_interval)
            print 'jenkins poll'
            _jenkins_data = jenkinsData(self.config)
            result = _jenkins_data.getLastResult()
            _redis.set(
                'jenkins-result',
                result,
                ex=self.redis_expire_time
            )
