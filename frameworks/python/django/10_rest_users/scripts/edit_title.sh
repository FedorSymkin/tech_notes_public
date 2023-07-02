#!/bin/bash

# usage: 
# 1. run server
# 2. ./edit_title.sh user password msgid newtitle


username=$1
password=$2
msgid=$3
newtitle=$4

token=$(./get_token.sh "$username" "$password")
if [ $? -ne 0 ]; then
    exit $?
fi

cmd="curl --fail -v -X PATCH -H 'Content-type: application/json' -H 'Authorization: Token $token' --data '{\"title\": \"$newtitle\"}' 'http://127.0.0.1:8000/api/posts/$msgid'"
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

