#!/usr/bin/env bash
set -e

cd /tmp/generic-similarity-search

# /buildvars/pypiproxy and /buildvars/version file are set by teamcity and
# are copied by docker to /tmp/generic-similarity-search/buildvars/
pypiproxy=`cat buildvars/pypiproxy`
version=`cat buildvars/version`

# 'version' environment variable is used within build.py
export version=${version}
pyb -C -v -X -E teamcity

cd target/dist/*

pip install devpi-client --index=${pypiproxy}
devpi use ${pypiproxy}
devpi login dev --password=dev
devpi upload --no-vcs