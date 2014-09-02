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
        "navn": query.encode('utf8'),
        "antPerSide": 1,
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

    r = requests.get(url, verify=False)
    doc = xmltodict.parse(r.text)

    # Add zoom values
    if addZoomValues:

        #convert stedsnavn to an array, even when just one dict
        if isinstance(doc["sokRes"]["stedsnavn"], list):
            stedsnavn_list = [dict(x) for x in doc["sokRes"]["stedsnavn"]]
        else:
            stedsnavn_list = [dict(doc["sokRes"]["stedsnavn"])]

        for stedsnavn in stedsnavn_list:
            #use 15 as default if not found
            stedsnavn["zoom"] = zoomValues.get(stedsnavn["navnetype"], 15)
        doc["sokRes"]["stedsnavn"] = stedsnavn_list

    resp = Response(json.dumps(doc), status=200, mimetype='application/json')
    return resp


if __name__ == "__main__":
    app.debug = False
    app.run()
