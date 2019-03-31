#!/bin/bash

# usage: 
# 1. run server
# 2. ./create_message.sh user password title content


username=$1
password=$2
title=$3
content=$4

token=$(./get_token.sh "$username" "$password")
if [ $? -ne 0 ]; then
    exit $?
fi

cmd="curl --fail -v -X POST -H 'Content-type: application/json' -H 'Authorization: Token $token' --data '{\"title\": \"$title\", \"content\": \"$content\"}' 'http://127.0.0.1:8000/api/posts/new'"
echo $cmd 1>&2
resp=$(eval $cmd)

if [ $? -eq 0 ]; then
    echo "$resp" | jq
else
    rc=$?
    echo ">>>>>>>> ERROR <<<<<<<<<<<<" 1>&2
    echo "TRY MANUAL: $cmd" 1>&2
    echo "$resp" 1>&2
    exit $rc
fi

