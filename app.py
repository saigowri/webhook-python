# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import datetime
import json
import os
import re

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

#----------------------------------------Main Entry Point---------------------------------------------------

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    if req.get("result").get("action") == "trainStatus":
        res = processRequest(req)
    if req.get("result").get("action") == "trainRoute":
        res = processRoute(req)
    if req.get("result").get("action") == "stationCode":
        res = processCode(req)
    if req.get("result").get("action") == "Tr_Name_to_Code":
        res = processTrainNumber(req)
    if req.get("result").get("action") == "train_btwn_stations":
        res = processTrainBtwnStations(req)
    if req.get("result").get("action") == "Train_fare":
        res = processTrainFare(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



#----------------------------------------processing Funtions---------------------------------------------------

def processRequest(req):
    if req.get("result").get("action") != "trainStatus":
        return {}
    baseurl = "https://api.railwayapi.com/v2/live/train/" 
    today = datetime.date.today().strftime("%d-%m-%Y")
    remain = "/date/"+today+"/apikey/3gleroll53"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult1(data)
    return res

def processRoute(req):
    if req.get("result").get("action") != "trainRoute":
        return {}
    baseurl = "https://api.railwayapi.com/v2/route/train/"
    remain = "/apikey/3gleroll53"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult2(data)
    return res

def processCode(req):
    if req.get("result").get("action") != "stationCode":
        return {}
    baseurl = "https://api.railwayapi.com/v2/suggest-station/name/"
    remain = "/apikey/3gleroll53"
    yql_query = makeQueryForPlace(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult3(data)
    return res

def processTrainNumber(req):
    if req.get("result").get("action") != "Tr_Name_to_Code":
        return {}
    baseurl = "https://api.railwayapi.com/v2/suggest-train/train/"
    remain = "/apikey/3gleroll53"
    yql_query = makeYqlQueryForTrain(req)
    if yql_query is None:
        return {}
    yql_url = baseurl +yql_query+ remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult4(data)
    return res


def processTrainBtwnStations(req):
    if req.get("result").get("action") != "train_btwn_stations":
        return {}
    baseurl = "https://api.railwayapi.com/v2/between/source/"
    remain = "/apikey/3gleroll53"
    yql_query_src  = makeYqlQueryForSrc(req)
    if yql_query_src is None:
        return {}
    yql_query_des  = makeYqlQueryForDes(req)
    if yql_query_des is None:
        return {}
    yql_query_date  = makeYqlQueryForDat(req)
    if yql_query_date is None:
        yql_query_date = "18-04-2018"
    p = yql_query_src
    q = "/dest/" + yql_query_des
    date = "/date/" + yql_query_date
    x = p + q + date
    yql_url = baseurl + x + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultForBtwnStations(data)
    return res

# def processTrainFare(req):
#     if req.get("result").get("action") != "Train_fare":
#         return {}
#     baseurl = "https://api.railwayapi.com/v2/fare/train/"
#     remain = "/age/18/pref/SL/quota/PT/date/18-04-2018/apikey/3gleroll53"
#      yql_query_Trnum  = makeYqlQuery(req)
#     if yql_query_Trnum is None:
#         return {}
#     p = yql_query_Trnum
# #     p = "12555"
# #     yql_query_src  = makeYqlQueryForSrc(req)
#     yql_query_src = "gkp"
#     if yql_query_src is None:
#         return {}
#     q = "/source/"+ yql_query_src
# #     q= "/source/gkp"
# #     yql_query_des  = makeYqlQueryForDes(req)
#     yql_query_des = "ndls"
#     if yql_query_des is None:
#         return {}
#     r = "/dest/"+ yql_query_des
# #     r = "/dest/ndls"
#     yql_query_date  = makeYqlQueryForDat(req)
#     if yql_query_date is None:
#         yql_query_date = "17-04-2018"
#     s = "/date/"+yql_query_date
    
#     yql_query_class  = makeYqlQueryForClass(req)
#     if yql_query_class is None:
#         return {}
#     t = "/pref/"+yql_query_class
# #     t = "/pref/SL"
#     yql_query_quota  = makeYqlQueryForQuota(req)
#     if yql_query_quota is None:
#         return {}
#     u = "quota/"+ yql_query_quota
# #     u = "quota/PT"
#     yql_query_age  = makeYqlQueryForAge(req)
#     if yql_query_age is None:
#         return {}
#     v = "age/" + yql_query_age 
# #     v = "age/18"
    
#     w = p+q+r
# #     x = w+v+t
# #     y = x+u+s

#     yql_url = baseurl + w + remain
# #     yql_url = "https://api.railwayapi.com/v2/fare/train/12555/source/gkp/dest/ndls/age/18/pref/SL/quota/PT/date/18-04-2018/apikey/3gleroll53"
#     result = urlopen(yql_url).read()
#     data = json.loads(result)
#     res = makeWebhookResultForFARE(data)
#     return res
# ----------------------------------------json data extraction functions---------------------------------------------------

def makeWebhookResult1(data):

    speech = data.get('position')
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }
def makeWebhookResult2(data):

#     speech = data.get('position')
    speech = ""
    for routes in data['route']:
        speech =  speech +routes['station']['name'] + " -> "
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }

def makeWebhookResult3(data):

    msg = []
    speech = ""
    for station in data['stations']:
        speech = speech + station['name'] +"  -  "+ station['code'] + ", "
        msg.append(station['name'] +"  -  "+ station['code'])
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply


def makeWebhookResult4(data):
    msg = []
    speech = ""
    for train in data['trains']:
        speech = speech + train['name'] +"  -  "+ train['number'] + ", "
        msg.append(train['name'] +"  -  "+ train['number'])
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply



def makeWebhookResultForBtwnStations(data):
    msg = []
    speech = ""
#     if(data['trains']] )
#         return "No Trains in that route"
    for train in data['trains']:
        speech = speech + train['name'] + ", Starts at "+ train['src_departure_time'] +", Reaches at "+ train['dest_arrival_time'] +","
        msg.append( train['name'] +", Starts at "+ train['src_departure_time'] +", Reaches at "+ train['dest_arrival_time'])
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply

def makeWebhookResultForFARE(data):
    speech = data.get('fare')
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }
# ------------------------------------query parameter extracting functions---------------------------------------------------



def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainnum = parameters.get("Train_numbers")
    if trainnum is None:
        return None
    return trainnum

def makeYqlQueryForTrain(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainname = parameters.get("Train_name")
    if trainname is None:
        return None
    return trainname

def makeQueryForPlace(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainnum = parameters.get("geo-city")
    if trainnum:
        return trainnum
    trainnum2 = parameters.get("place") 
    if trainnum2:
        return trainnum2
    return {}


def makeYqlQueryForSrc(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainSrc = parameters.get("station_code_name")
    if trainSrc is None:
        return None
    return trainSrc[0]

def makeYqlQueryForDes(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainSrc = parameters.get("station_code_name")
    if trainSrc is None:
        return None
    return trainSrc[1]


def makeYqlQueryForDat(req):
    result = req.get("result")
    parameters = result.get("parameters")
    traindate = parameters.get("date")
    if traindate is None:
        return None
    return traindate

def makeYqlQueryForClass(req):
    result = req.get("result")
    parameters = result.get("parameters")
    traindclass = parameters.get("class")
    if traindclass is None:
        return None
    return traindclass

def makeYqlQueryForQuota(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainquota = parameters.get("quota")
    if trainquota is None:
        return None
    return trainquota

def makeYqlQueryForAge(req):
    result = req.get("result")
    parameters = result.get("parameters")
    age = parameters.get("age")
    if age is None:
        return None
    return age

# ------------------------------------extra function of weather project for referencing---------------------------------------------------


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
