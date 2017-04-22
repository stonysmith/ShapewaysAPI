#!/bin/bash
client_id=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
client_secret=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
curl -X POST --user ${client_id}:${client_secret} --data grant_type=client_credentials https://api.shapeways.com/oauth2/token  >token.json

grep -Po '"access_token":.*?[^\\]",' token.json|cut -f4 -d \" >access_token
access_token=`cat access_token`
curl -X GET --header "Authorization: Bearer ${access_token}" https://api.shapeways.com/models/v1?page=1
