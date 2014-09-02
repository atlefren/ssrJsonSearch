# -*- coding: utf-8 -*-

from flask import Flask
from flask import request, Response

import xmltodict
import requests
import json
from collections import OrderedDict

app = Flask(__name__)

# Add zoomvalues to the JSON result
addZoomValues = True

# Dictionary holding navnetype and zoomlevel
zoomValues = {u"By": 12, u"Kommune": 11, u"Fjellområde": 10, u"Verneområder": 10, u"Innsjø": 14}

@app.route('/')
def home():
	return "ssrJsonSearch"

@app.route('/ssr')
def ssrSok():
    query = request.args.get('query', '')
    nordLL = request.args.get('nordLL')
    ostLL = request.args.get('ostLL')
    nordUR = request.args.get('nordUR')
    ostUR = request.args.get('ostUR')

    bbox = all([nordLL, ostLL, nordUR, ostUR])

    if bbox:	
    	print """https://ws.geonorge.no/SKWS3Index/ssr/sok?navn=""" + query + """*&nordLL=""" + nordLL + """&ostLL=""" + ostLL + """&nordUR=""" + nordUR + """&ostUR=""" + ostUR + """&antPerSide=9&epsgKode=4258&eksakteForst=true"""
    	r = requests.get("""https://ws.geonorge.no/SKWS3Index/ssr/sok?navn=""" + query + """*&nordLL=""" + nordLL + """&ostLL=""" + ostLL + """&nordUR=""" + nordUR + """&ostUR=""" + ostUR + """&antPerSide=9&epsgKode=4258&eksakteForst=true""", verify=False)
    else:
        r = requests.get('https://ws.geonorge.no/SKWS3Index/ssr/sok?navn='+query+'*&antPerSide=9&epsgKode=4258&eksakteForst=true', verify=False)
    doc = xmltodict.parse(r.text)

    # Add zoom values
    if addZoomValues: 
	    i = 0 # counter
	    try:
	    	# Check to see if we only get one result
	    	ssrId = doc["sokRes"]["stedsnavn"]["ssrId"]
	    	stedsnavn = dict(doc["sokRes"]["stedsnavn"]) # convert to regular dict
	    	try:
	    		# Check if this navnetype exist in zoomValues
	    		stedsnavn["zoom"] = zoomValues[stedsnavn["navnetype"]]
	    	except KeyError:
	    		# If not set to default zoom level 15
	    		stedsnavn["zoom"] = 15
	    	doc["sokRes"]["stedsnavn"] = [stedsnavn] # Always return array
	    except TypeError:
		    for x in doc["sokRes"]["stedsnavn"]: # every stedsnavn
		    	stedsnavn = dict(x) # convert to regular dict
		    	try:
		    		# Check if this navnetype exist in zoomValues
		    		stedsnavn["zoom"] = zoomValues[stedsnavn["navnetype"]]
		    	except KeyError:
		    		# If not set to default zoom level 15
		    		stedsnavn["zoom"] = 15
		    	doc["sokRes"]["stedsnavn"][i] = stedsnavn
		    	i += 1
 
    js = json.dumps(doc)

    resp = Response(js, status=200, mimetype='application/json')
    return resp

if __name__ == "__main__":
    app.debug = False
    app.run()


