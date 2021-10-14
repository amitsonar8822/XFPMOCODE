#!/usr/bin/env python
# coding: utf-8


# !/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################################################################
# Description:python code to connect to DecisionAPI. To get Decision data from ServiceNow
# Pandas library used to convert response to CSV file.
#
# Date:09/06/2021
#
# Author:Amit Sonar
#
##############################################################################################################################
import sys
import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
from datetime import datetime, timedelta

firstarg = sys.argv[1]
N_DAYS_AGO = int(sys.argv[2])
print(N_DAYS_AGO)

today = datetime.now().date()
n_days_ago = today - timedelta(days=N_DAYS_AGO)
execute = False
bufferDate = str(n_days_ago)
print(today, bufferDate)


clientId = 'aa2bc34930b94c92b81c9445fe8eeb21'
clientSecret = '18FC000001Db42119f30A512309947b4'
appAuth = 'Basic aW50Z3JvdW06aGVvd0F4ZXdhMjEzNC1KdWlrd2w='
appContentType = 'application/json'
getKeysurl = "https://dev-eur-rcn4.apis.roche.com:37276/getDecisionsMethod"
getObjectDetailsurl = "https://dev-eur-rcn4.apis.roche.com:37276/getDecisionMethod"
# Table = ""


payload = json.dumps({
    "content": {
        "active": [
            "true",
            "false"
        ],
        "sys_updated_on": bufferDate
    },
    "header": {
        "sourcesystemid": "IDW"
    }
})
headers = {
    'Content-Type': appContentType,
    'client_id': clientId,
    'Authorization': appAuth,
    'client_secret': clientSecret
}

loopCount = 0
keysResponse = requests.request("POST", getKeysurl, headers=headers, data=payload)

json_data = json.loads(keysResponse.text)
recCount = json_data['result']['metadata']['recCount']
print("Record count is:" + str(recCount))

if int(recCount) > 0:
    while loopCount < recCount:
        decisionNumber = json_data['result']['decision'][loopCount]['number']
        print(str(loopCount) + "-->" + decisionNumber)

        decisionDatapayload = json.dumps({
            "content": {
                "number": decisionNumber
            },
            "header": {
                "sourcesystemid": "IDW"
            }
        })
        decisionDataHeaders = {
            'Content-Type': appContentType,
            'client_id': clientId,
            'Authorization': appAuth,
            'client_secret': clientSecret
        }

        decisionDataResponse = requests.request("POST", getObjectDetailsurl, headers=decisionDataHeaders,
                                                data=decisionDatapayload)

        decisionDataResponseJSON = json.loads(decisionDataResponse.text)
        df = json_normalize(decisionDataResponseJSON['result'])
        if loopCount == 0:
            mdf = df
        else:
            mdf = mdf.append(df)
        loopCount += 1

        # print(mdf)

        mdf['html_description'] = mdf['html_description'].str.slice(0, 3990).replace({r'\n': ''}, regex=True).replace(
            {r'\r': ''},
            regex=True).replace(
            {r'\r\n': ''}, regex=True)

        mdf.to_csv(r'%s/intermediaryFiles/serviceNowAPI/PPM/DecisionsData.csv' % firstarg
                   , index=False, header=True, sep="|")
# mdf.to_csv(r'C:\workdocs\PMO\API_RESPONSE/ProjectData.csv'
#           , index=False, header=True)

else:
    print("No fresh data available to fetch from API")

print("**********Proccess finished***********")

