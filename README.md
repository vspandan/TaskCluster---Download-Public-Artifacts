Set the following variables in python file

baseUrl = 'https://index.taskcluster.net/v1/tasks'
namespace="gecko.v2.mozilla-central.latest.firefox"
artifactQueue='https://queue.taskcluster.net/v1/task/'
builds=['linux64-asan','linux64-asan-debug']
artifacts=['common.tests']


Run Python File
./downloadArtifacts.py
