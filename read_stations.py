#!/usr/bin/env python

import json
import requests

STATIONS_URL = 'https://tidesandcurrents.noaa.gov/cgi-bin/stationbarsearch.cgi'

params = {
    'term': '',
    'type': 'active'
}

STATION_ID_FILE = 'station_ids.json'


def transform_stations(raw_stations):
    station_ids = []
    print('Have {num} stations'.format(num=len(raw_stations)))
    for station in raw_stations:
        raw_name = station['name']
        station_id, station_name = raw_name.split(' ', 1)
        station_name = station_name.strip(', ')
        # 365 of 423 with usable IDs
        if len(station_id) != 7:
            print('station {sname} should have 7-character ID, but has {id}'.format(sname=station_name, id=station_id))
            continue
        station_ids.append(station_id)

    print('Have {num} usable station IDs'.format(num=len(station_ids)))
    with open(STATION_ID_FILE, 'wb') as outf:
        json.dump(station_ids, outf)
    print('Wrote station IDs to {outf}'.format(outf=STATION_ID_FILE))

r = requests.get(STATIONS_URL, params=params)
if r.ok:
    # response is JSON, but sent as text wrapped in parens and borked
    txt = r.text
    txt = txt[1:-6] + '"}]'
    j = json.loads(txt)
    print(j)
    transform_stations(j)
else:
    print('failed to fetch stations')
