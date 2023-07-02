#!/bin/bash

# usage: 
# 1. run server
# 2. ./get_all_posts.sh user password


username=$1
password=$2

token=$(./get_token.sh "$username" "$password")
if [ $? -ne 0 ]; then
    exit $?
fi

cmd="curl --fail -v -H 'Authorization: Token $token' 'http://127.0.0.1:8000/api/posts'"
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

