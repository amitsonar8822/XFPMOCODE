#!/usr/bin/env python
# coding: utf-8


# !/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################################################################
# Description:python code to connect to getProjectsMethod and getProjectMethod methods from API. To get project data from ServiceNow
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

N_DAYS_AGO = int(sys.argv[2])

today = datetime.now().date()
n_days_ago = today - timedelta(days=N_DAYS_AGO)

bufferDate = str(n_days_ago)
print(today, bufferDate)

appKey = 'b4ea648c-f44a-4d53-925d-7b208985d34a'
appAuth = 'Basic aW50Z3JvdW06aGVvd0F4ZXdhMjEzNC1KdWlrd2w='
appContentType = 'application/json'
getKeysurl = "https://send.roche.com/api/ServiceNow/ppm_project/v1.0/ppm_project/getProjectsMethod"
getObjectDetailsurl = "https://send.roche.com/api/ServiceNow/ppm_project/v1.0/ppm_project/getProjectMethod"
# Table = ""
firstarg = sys.argv[1]

payload = json.dumps({
    "content": {
        "active": [
            "true",
            "false"
        ],
        "updated_date": bufferDate
    },
    "header": {
        "sourcesystemid": "IDW"
    }
})
headers = {
    'Content-Type': appContentType,
    'Api-Key': appKey,
    'Authorization': appAuth
}

keysResponse = requests.request("POST", getKeysurl, headers=headers, data=payload)

# print(response.text)
json_data = json.loads(keysResponse.text)
loopCount = 0
recCount = json_data['result']['metadata']['recCount']
print(recCount)

while loopCount < recCount:
    projectSysId = json_data['result']['projects'][loopCount]['sys_id']
    projectNumber = json_data['result']['projects'][loopCount]['number']
    print(str(loopCount) + "-->" + projectNumber)

    projectDatapayload = json.dumps({
        "content": {
            "number": projectNumber
        },
        "header": {
            "sourcesystemid": "IDW"
        }
    })
    projectDataHeaders = {
        'Content-Type': appContentType,
        'Api-Key': appKey,
        'Authorization': appAuth
    }

    projectDataResponse = requests.request("POST", getObjectDetailsurl, headers=projectDataHeaders,
                                           data=projectDatapayload)

    # print(projectDataResponse.text)

    projectDataResponseJSON = json.loads(projectDataResponse.text)

    # print(projectDataResponseJSON)
    df = json_normalize(projectDataResponseJSON['result'])
    df['sys_id'] = projectSysId

    if loopCount == 0:
        mdf = df
    else:
        mdf = mdf.append(df)
    loopCount += 1

# print(mdf)

mdf['description'] = mdf['description'].str.slice(0, 3990).replace({r'\n': ''}, regex=True).replace({r'\r': ''},
                                                                                                    regex=True).replace(
    {r'\r\n': ''}, regex=True)

mdf['comments_and_work_notes'] = mdf['comments_and_work_notes'].str.slice(0, 3990).replace({r'\n': ''},
                                                                                           regex=True).replace(
    {r'\r': ''},
    regex=True).replace(
    {r'\r\n': ''}, regex=True)

mdf['work_notes'] = mdf['work_notes'].str.slice(0, 3990).replace({r'\n': ''}, regex=True).replace({r'\r': ''},
                                                                                                  regex=True).replace(
    {r'\r\n': ''}, regex=True)

mdf['key_deliverables'] = mdf['key_deliverables'].replace({r'\n': ''}, regex=True).replace({r'\r': ''},
                                                                                           regex=True).replace(
    {r'\r\n': ''}, regex=True)

mdf['primary_objectives'] = mdf['primary_objectives'].str.slice(0, 3990).replace({r'\n': ''}, regex=True).replace(
    {r'\r': ''},
    regex=True).replace(
    {r'\r\n': ''}, regex=True)

mdf['additional_comments'] = mdf['additional_comments'].str.slice(0, 3990).replace({r'\n': ''}, regex=True).replace(
    {r'\r': ''},
    regex=True).replace(
    {r'\r\n': ''}, regex=True)

mdf.to_csv(r'%s/intermediaryFiles/serviceNowAPI/PPM/ProjectsData.csv' % firstarg
           , index=False, header=True, sep="|")

# mdf.to_csv(r'C:\workdocs\PMO\API_RESPONSE/ProjectData.csv'
#           , index=False, header=True)
print("**********Proccess finished***********")
