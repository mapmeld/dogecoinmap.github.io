#!/usr/bin/python
import os
import json
from overpass import parser as overpass_parser

scriptdir = os.path.dirname(os.path.abspath(__file__))

coins = [
    'Dogecoin'
]

parsers = {
	'overpass': overpass_parser,
}

# update data/currencies
with open(scriptdir + '/coins.js', 'w') as f:
	f.write('function get_coins() { return ["%s"]; }\n' % '", "'.join(coins))

# call individual parsers
for name, parser in parsers.iteritems():
	for coin in coins:
		coin = coin.lower()

		# compare to existing points
		existing_json = open(scriptdir + ('/data-%s-%s.json' % (name, coin)))
		existing_pts = {}
		for pt in json.load(existing_json):
			existing_pts[pt["id"]] = pt

		# fetch points from OSM
		pts = parser.get_points(coin)

		# decide how to update map
		for pt in pts:
			if pt["id"] in existing_pts:
				# update an existing point with latest data
				# do not change physical status
				pt["physical"] = existing_pts[pt["id"]]["physical"]
				existing_pts[pt["id"]] = pt
			else:
				# new point from OSM
				print("New OSM point:")
				print(json.dumps(pt))
				physical = raw_input("Adding point unless you respond N, n, or No here: ")
				if physical.lower().replace(' ','').replace('no','n') == "n":
					# don't map it for now
					# can always be changed in the JSON
					pt["physical"] = False
				else:
					# looks good!
					pt["physical"] = True
				existing_pts[pt["id"]] = pt

		json.dump(existing_pts.values(), open(scriptdir + '/data-%s-%s.json' % (name, coin), 'w'), indent=2, sort_keys=True, separators = (',', ':'))
