# -*- coding: utf-8 -*-

from flask import Flask
from flask import request, Response

import xmltodict
import requests
import json
import urllib

app = Flask(__name__)

# Add zoomvalues to the JSON result
addZoomValues = True

# Dictionary holding navnetype and zoomlevel
zoomValues = {
    u"By": 12,
    u"Kommune": 11,
    u"Fjellområde": 10,
    u"Verneområder": 10,
    u"Innsjø": 14
}

base_url = "https://ws.geonorge.no/SKWS3Index/ssr/sok"


@app.route('/')
def home():
    return "ssrJsonSearch"


@app.route('/ssr')
def ssrSok():
    query = request.args.get('query', '')
    nordLL = request.args.get('nordLL', None)
    ostLL = request.args.get('ostLL', None)
    nordUR = request.args.get('nordUR', None)
    ostUR = request.args.get('ostUR', None)

    bbox = all([nordLL, ostLL, nordUR, ostUR])

    query_params = {
        "navn": query,
        "antPerSide": 9,
        "epsgKode": "4258",
        "eksakteForst": "true"
    }

    if bbox:
        query_params.update({
            "nordLL": nordLL,
            "ostLL": ostLL,
            "nordUR": nordUR,
            "ostUR": ostUR
        })

    url = base_url + "?" + urllib.urlencode(query_params)
    print url
    r = requests.get(url, verify=False)
    doc = xmltodict.parse(r.text)
    # Add zoom values
    if addZoomValues:
        i = 0  # counter
        try:
            # Check to see if we only get one result
            ssrId = doc["sokRes"]["stedsnavn"]["ssrId"]

            # convert to regular dict
            stedsnavn = dict(doc["sokRes"]["stedsnavn"])
            try:
                # Check if this navnetype exist in zoomValues
                stedsnavn["zoom"] = zoomValues[stedsnavn["navnetype"]]
            except KeyError:
                # If not set to default zoom level 15
                stedsnavn["zoom"] = 15
            doc["sokRes"]["stedsnavn"] = [stedsnavn]  # Always return array
        except TypeError:
            for x in doc["sokRes"]["stedsnavn"]:  # every stedsnavn
                stedsnavn = dict(x)  # convert to regular dict
                try:
                    # Check if this navnetype exist in zoomValues
                    stedsnavn["zoom"] = zoomValues[stedsnavn["navnetype"]]
                except KeyError:
                    # If not set to default zoom level 15
                    stedsnavn["zoom"] = 15
                doc["sokRes"]["stedsnavn"][i] = stedsnavn
                i += 1

    resp = Response(json.dumps(doc), status=200, mimetype='application/json')
    return resp


if __name__ == "__main__":
    app.debug = False
    app.run()
