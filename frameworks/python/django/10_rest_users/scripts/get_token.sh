#!/bin/bash

# usage: 
# 1. run server
# 2. ./get_token.sh user password


username=$1
password=$2

cmd="curl --fail -v -X POST -H 'Content-type: application/json' --data '{\"username\": \"$username\", \"password\": \"$password\"}' 'http://127.0.0.1:8000/api/get_token'"
echo $cmd 1>&2

resp=$(eval $cmd)

if [ $? -eq 0 ]; then
    echo "$resp" | jq -r '.token'
else
    rc=$?
    echo ">>>>>>>> ERROR <<<<<<<<<<<<" 1>&2
    echo "TRY MANUAL: $cmd" 1>&2
    echo "$resp" 1>&2
    exit $rc
fi

