#!/usr/bin/python3
import json
from requests import Session
from datetime import datetime, timedelta, time
import time

list_data=[]
now=datetime.now()
hours=1 # you can customize this variable
hours_added=timedelta(hours=hours)
past=now-hours_added
epoc_now=int(time.mktime(now.timetuple()))*1000
epoc_past=int(time.mktime(past.timetuple()))*1000
organizationID='<your organization id>'
class NoRebuildAuthSession(Session):
    def rebuild_auth(self, prepared_request, response):
        """
        """

session=NoRebuildAuthSession()

url = "https://management.api.umbrella.com/auth/v2/oauth2/token"
dns_top = "https://reports.api.umbrella.com/v2/organizations/"+organizationID+"/activity/dns"

header = {
  'Authorization': 'Basic <base64-encoded string username:password.>'
}
"""
'categories':'109' << Potentially harmful
'categories':'67' << Malware
'
"""
params ={'from':epoc_past,'to':epoc_now,'limit':'100','offset':'0','identitytypes':'directory_user','verdict':'blocked','categories':'109,67'}
def get_tok():
    r = session.request("POST", url, headers=header)
    body=json.loads(r.content)
    return body['access_token']

def get_dns_top(access_token,dns_top,params):
    r=session.request("GET",dns_top,headers={'Authorization':'Bearer '+access_token},params=params)
    body=json.loads(r.content)
    return body

def sendtoteams(data):
    date_time=datetime.strptime(data[1],'%H:%M:%S')
    timenow=date_time.time()
    webhook_url = '<teams webhook url>'

    scheme = {
        "@context": "https://schema.org/extensions",
        "@type": "MessageCard",
        "themeColor": "0072C6",
        "title": "Umbrella Alert",
        "text": "Click **Dashboard Umbrella** to Check !",
        "sections": [
            {
                "facts": [
                    {
                        "name": "Time:",
                        "value": str(timenow.hour+7).zfill(2)+':'+str(timenow.minute).zfill(2)+':'+str(timenow.second).zfill(2)
                    },
                    {
                        "name": "Domain:",
                        "value": data[3]
                    },
                    {
                        "name": "Categories:",
                        "value": data[2]
                    },
                    {
                        "name": "Identity:",
                        "value": data[4]
                    },
                    {
                        "name": "IP Address",
                        "value": data[0]
                    }
                ]
            }
        ],
        "potentialAction": [

            {
                "@type": "OpenUri",
                "name": "Dashboard Umbrella",
                "targets": [
                    {"os": "default", "uri": "https://dashboard.umbrella.com"}
                ]
            }

        ]
    }

    headers = {
        "Accept": "application/json", "Content-Type": "application/json"
    }

    response = session.request('POST', webhook_url, json=scheme, headers=headers)
    print(response.text)



access_token=get_tok()
report=get_dns_top(access_token,dns_top,params)
find=report
l=0
for i in report['data']:
    l += 1

    if i == report['data'][-1]:
        print(i['internalip'])
        print(i['time'])
        print(i['categories'][0]['label'])
        print(i['domain'])
        print(i['identities'][1]['label'])
        list_data.append([i['internalip'],i['time'],i['categories'][0]['label'],i['domain'],i['identities'][1]['label']])
    elif i['internalip'] == report['data'][l]['internalip']:
        if i['domain'] == report['data'][l]['domain']:
            pass
    else:
        print(i['internalip'])
        print(i['time'])
        print(i['categories'][0]['label'])
        print(i['domain'])
        print(i['identities'][1]['label'])
        list_data.append([i['internalip'], i['time'], i['categories'][0]['label'], i['domain'], i['identities'][1]['label']])

list_data.reverse()
for i in list_data:
    sendtoteams(i)
