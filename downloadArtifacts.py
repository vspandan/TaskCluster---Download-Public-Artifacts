import urllib
import urllib2
import json
import os
import subprocess
import sys


baseUrl = 'https://index.taskcluster.net/v1/tasks'
namespace='gecko.v2.mozilla-central.latest.firefox'
artifactQueue='https://queue.taskcluster.net/v1/task/'
builds=['linux64-asan','linux64-asan-debug']
artifacts=['jsshell','common.tests']
targetLoc='artifacts'

def doPostRequest(url,values):
	try:
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		resp = urllib2.urlopen(req)
		if(resp.getcode()==200):
			typ=resp.headers.getheader('content-type')
			if typ == 'application/json; charset=utf-8':
				return resp.read()
			else:
				raise Exception('In Correct Response Type - Expecting application/json')

		else:
			print 'Response Code:'+str(resp.getcode())
	except urllib2.URLError:
		print 'No Internet Connection'
	except Exception as e:
		print e

def doGetRequest(url):
	try:
		req = urllib2.Request(url)
		resp = urllib2.urlopen(req)
		if(resp.getcode()==200):
			typ=resp.headers.getheader('content-type')
			if typ == 'application/json; charset=utf-8':
				return resp.read()
			else:
				raise Exception('In Correct Response Type - Expecting application/json')
		else:
			print 'Response Code:'+str(resp.getcode())
	except urllib2.URLError:
		print 'No Internet Connection'
	except Exception as e:
		print e


def fetchBuildUrls(jsonResp):
	j = json.loads(jsonResp)
	tasks = j['tasks']
	taskIDList={}
	buildUrls={}
	for task in tasks:
		for build in builds:
			if (task['namespace']==namespace+'.'+build):
				taskIDList[build]=task['taskId']
	for build in builds:
		buildUrls[build]=artifactQueue+taskIDList[build]+'/artifacts'
	downloadArtifacts(buildUrls)

def downloadArtifacts(buildUrls):
	for k in buildUrls.keys():
		localLoc=os.path.abspath(targetLoc+'/'+k)
		if os.path.exists(localLoc):
			import shutil
			shutil.rmtree(localLoc)
		os.makedirs(localLoc)
		resp = doGetRequest(buildUrls[k])
		if resp is not None:
			jsonObj=json.loads(resp)
			artifactsList = jsonObj['artifacts']
			for l in  artifactsList:
				for a in artifacts:
					if a in l['name']:
						remoteLoc=buildUrls[k]+'/'+l['name']
						localLoc=localLoc+'/'+a+'.zip'
						print 'Downloading Artifact ' + k + ':' + str(a)
						if downloadUrl(localLoc,remoteLoc):
							print 'Extracting Artifact ' + k + ':' + str(a)
							unZip(localLoc,localLoc[:-4])
							os.remove(localLoc)

def unZip(local, dest):
	cmd = 'unzip '+ local + ' -d ' + dest
	p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, cwd= os.getcwdu(),
            env = os.environ)
	out, err = p.communicate()
	if p.returncode != 0:
		print 'Error in Downloading'
		return False
	return True

def downloadUrl(local, remote):
	cmd = 'wget --no-check-certificate -O '+ local + ' ' + remote
	p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, cwd= os.getcwdu(),
            env = os.environ)
	out, err = p.communicate()
	if p.returncode != 0:
		print 'Error in Downloading'
		return False
	return True

def main():
	url=baseUrl+'/'+namespace
	values={}	
	jsonResp = doPostRequest(url,values)
	fetchBuildUrls(jsonResp)
	
if __name__=='__main__':
	main()