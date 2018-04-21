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

apikey = "zc4qtk7x4o"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    if req.get("result").get("action") == "trainStatus":
        res = processStatus(req)
    if req.get("result").get("action") == "trainRoute":
        res = processRoute(req)
    if req.get("result").get("action") == "stationCode":
        res = processCode(req)
    if req.get("result").get("action") == "Tr_Name_to_Code":
        res = processTrainNumber(req)
    if req.get("result").get("action") == "train_btwn_stations":
        res = processTrainBtwnStations(req)
    if req.get("result").get("action") == "TrainFare":
        res = processTrainFare(req)
    if req.get("result").get("action") == "cancelledTrain":
        res = processCancelledTrains(req)
    if req.get("result").get("action") == "train_code_to_name":
        res = processTrainName(req)
    if req.get("result").get("action") == "PNRStatus":
        res = processPNRStatus(req)
    if req.get("result").get("action") == "stationName":
        res = processStationName(req)
    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



#----------------------------------------processing Funtions---------------------------------------------------

#Train Status
def processStatus(req):
    if req.get("result").get("action") != "trainStatus":
        return {}
    baseurl = "https://api.railwayapi.com/v2/live/train/" 
    today = datetime.date.today().strftime("%d-%m-%Y")
    remain = "/date/"+today+"/apikey/"+apikey
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultStatus(data)
    return res

#Train Route
def processRoute(req):
    if req.get("result").get("action") != "trainRoute":
        return {}
    baseurl = "https://api.railwayapi.com/v2/route/train/"
    remain = "/apikey/"+apikey
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultRoute(data)
    return res

# Station Code
def processCode(req):
    if req.get("result").get("action") != "stationCode":
        return {}
    baseurl = "https://api.railwayapi.com/v2/suggest-station/name/"
    remain = "/apikey/"+apikey
    yql_query = makeQueryForPlace(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultCode(data)
    return res

#Train Name to Code
def processTrainNumber(req):
    if req.get("result").get("action") != "Tr_Name_to_Code":
        return {}
    baseurl = "https://api.railwayapi.com/v2/suggest-train/train/"
    remain = "/apikey/"+apikey
    yql_query = makeYqlQueryForTrain(req)
    if yql_query is None:
        return {}
    yql_url = baseurl +yql_query+ remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultTrain(data)
    return res

#Train between stations
def processTrainBtwnStations(req):
    if req.get("result").get("action") != "train_btwn_stations":
        return {}
    baseurl = "https://api.railwayapi.com/v2/between/source/"
    remain = "/apikey/"+apikey
    yql_query_src  = makeYqlQueryForSrc(req)
    if yql_query_src is None:
        return {}
    yql_query_des  = makeYqlQueryForDes(req)
    if yql_query_des is None:
        return {}
    yql_query_date  = makeYqlQueryForDat(req)
    if yql_query_date is None:
        yql_query_date = datetime.date.today().strftime("%d-%m-%Y")
    p = yql_query_src
    q = "/dest/" + yql_query_des
    date = "/date/" + yql_query_date
    x = p + q + date
    yql_url = baseurl + x + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultForBtwnStations(data)
    return res


def processTrainFare(req):
    if req.get("result").get("action") != "TrainFare":
        return {}
    trainnum = makeYqlQuery(req)
    result = req.get("result")
    parameters = result.get("parameters")
    trainSrc = parameters.get("station_code_name")
#     fromstation =  trainSrc[0]
    fromstation = "ktym"
#     tostation = trainSrc[1]
    tostation = "hyb"
    age = makeYqlQueryForAge(req)
    pref = makeYqlQueryForClass(req)
    quota = makeYqlQueryForQuota(req)
    dat = makeYqlQueryForDat(req)
    yql_url = "https://api.railwayapi.com/v2/fare/train/"+trainnum+"/source/"+fromstation+"/dest/"+tostation+"/age/"+age+"/pref/"+pref+"/quota/"+quota+"/date/"+dat+"/apikey/"+apikey
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultForFARE(data)
    return res

def processCancelledTrains(req):
    if req.get("result").get("action") != "cancelledTrain":
        return {}
    baseurl = "https://api.railwayapi.com/v2/cancelled"
    remain = "/apikey/"+apikey
    yql_query_date  = makeYqlQueryForDat(req)
    if yql_query_date is None:
        yql_query_date = datetime.date.today().strftime("%d-%m-%Y")
    #get train name or number
    result = req.get("result")
    parameters = result.get("parameters")
    trainvar = ""
    trainname = parameters.get("Train_name")
    if trainname:
        yql_query_train = trainname
        trainvar = 'name'
    trainnum = parameters.get("Train_numbers") 
    if trainnum:
        yql_query_train = trainnum
        trainvar = 'number'
    date = "/date/" + yql_query_date
    yql_url = baseurl + date + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    msg = []
    speech = ""
    flag = 0
    for train in data['trains']:
        if yql_query_train.lower() in train[trainvar].lower():
            speech = train['name'] + " having train number " + train['number'] + " is cancelled on " + yql_query_date
            msg.append( train['name'] + " having train number " + train['number'] + " is cancelled on " + yql_query_date)
            flag = 1
            break
    if flag == 0:
        speech = "The train is not cancelled on " + yql_query_date
        msg.append( "The train is not cancelled on " + yql_query_date)
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply

#Train Code to Name
def processTrainName(req):
    baseurl = "https://api.railwayapi.com/v2/name-number/train/"
    remain = "/apikey/"+apikey
    # get train number
    result = req.get("result")
    parameters = result.get("parameters")
    trainNum = parameters.get("Train_numbers")
    if trainNum is None:
        return None
    yql_url = baseurl + trainNum + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    msg = []
    speech = ""
    train = data.get('train')
    if train['number'] == trainNum:
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
	
#PNR Status
def processPNRStatus(req):
    if req.get("result").get("action") != "PNRStatus":
        return {}
    baseurl = "https://api.railwayapi.com/v2/pnr-status/pnr/" 
    remain = "/apikey/"+apikey
    pnrnum = req.get("result").get("parameters").get("pnr_number")
    if pnrnum is None:
        speech = "Please enter pnr number"
    query = baseurl + pnrnum + remain
    result = urlopen(query).read()
    data = json.loads(result)   
    #Process response
    msg = []
    speech = ""
    train = json.dumps(data.get("train").get("name"))
    if train == "null":
        speech = "Sorry, the PNR seems to be invalid or expired"
        msg.append(speech)
    else:
        speech = "The chart for the train " + train
        train_num =  json.dumps(data.get("train").get("number")) 
        print("Here "+train_num)
        speech = speech + " (" + train_num + ") from station "
        from_stat = json.dumps(data.get("from_station").get("name")) 
        to_stat = json.dumps(data.get("to_station").get("name")) 
        speech = speech + from_stat + " to the station " + to_stat
        print("Speech "+speech)
        chart_prepared = json.dumps(data.get("chart_prepared"))#.get("name")
        if chart_prepared == "false":
            speech = speech + " has not been prepared."
        else:
            speech = speech + " has been prepared."
        msg.append(speech)
        boarding_point = json.dumps(data.get("boarding_point").get("name"))
        journey_class = json.dumps(data.get("journey_class").get("code"))
        details = "The intended "+ journey_class +" class journey starts from " + boarding_point + " to "
        reservation_upto = json.dumps(data.get("reservation_upto").get("name"))
        doj =  json.dumps(data.get("doj"))
        details = details + reservation_upto + " on " + doj 
        speech = speech + " -> " + details
        msg.append(details)
        total_passengers =  json.dumps(data.get("total_passengers")) 
        details = "The booking details of "+ total_passengers +" passenger/s are as follows: "
        speech = speech + " -> " + details
        msg.append(details)
        for passenger in data['passengers']:
            speech = speech + passenger['current_status'] + ", "
            msg.append(passenger['current_status'])
	
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply

#Station Code to Name
def processStationName(req):
    baseurl = "https://api.railwayapi.com/v2/code-to-name/code/"
    remain = "/apikey/"+apikey
    result = req.get("result")
    parameters = result.get("parameters")
    stationCode = parameters.get("station_code_name").lower()
    yql_url = baseurl +stationCode+ remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    msg = []
    speech = ""
    if not data['stations']:
        speech = "Sorry, I could not find any stations in the city you mentioned."
        msg.append(speech)
    for station in data['stations']:
        if stationCode == station['code'].lower():
            speech = speech + "Station name of " + station['code'] + " is " + station['name']
            msg.append("Station name of " + station['code'] + " is " + station['name'])
            speech = speech + "Its neighbouring stations are: "
            msg.append("Its neighbouring stations are: ")
    for station in data['stations']:
        if stationCode != station['code'].lower():
            speech = speech + station['code'] + " - " + station['name']
            msg.append(station['code'] + " - " + station['name'])
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply
  
# ----------------------------------------json data extraction functions---------------------------------------------------

def makeWebhookResultStatus(data):
    speech = data.get('position')
    if data.get('response_code') == 210:
        speech = "Train may be cancelled or is not scheduled to run"
    return {
        "speech": speech,
        "displayText": speech,
        "source": "webhook-dm"
    }
def makeWebhookResultRoute(data):

#     speech = data.get('position')
    speech = ""
    for routes in data['route']:
        speech =  speech +routes['station']['name'] + " -> "
#    speech = speech.rstrip('>')
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }

def makeWebhookResultCode(data):
    msg = []
    speech = ""
    if not data['stations']:
        speech = "Sorry, I could not find any stations in the city you mentioned."
        msg.append(speech);
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


def makeWebhookResultTrain(data):
    msg = []
    speech = ""
    if not data['trains']:
        speech = "Sorry, I could not find any trains you mentioned."
        msg.append(speech);
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
    if not data['trains']:
        speech = "No Trains in that route"
        msg.append("No Trains in that route")
    for train in data['trains']:
        speech = speech + train['name'] + ", Starts at "+ train['src_departure_time'] +", Reaches at "+ train['dest_arrival_time'] +","
        msg.append( train['name'] +", Starts at "+ train['src_departure_time'] +", Reaches at "+ train['dest_arrival_time'])
#    msg.append(datetime.datetime.strptime("2018-04-20", '%Y-%m-%d').strftime('%d-%m-%Y'))
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
    return datetime.datetime.strptime(traindate, '%Y-%m-%d').strftime('%d-%m-%Y')

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



def makeQueryForfromstation(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainSrc = parameters.get("from")
    if trainSrc is None:
        return None
    return trainSrc

def makeQueryFortostation(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainSrc = parameters.get("to")
    if trainSrc is None:
        return None
    return trainSrc

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
