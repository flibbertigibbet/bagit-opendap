#!/usr/bin/env python

import datetime
import json
import os
import requests
import sys
import time

BASE_URL = 'https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/'

# metadata URL is of the form
# https://opendap.co-ops.nos.noaa.gov/erddap/info/datasetID/index.json

DATASETS = [
    'IOOS_Air_Temperature',
    'IOOS_Barometric_Pressure',
    'IOOS_Conductivity',
    'IOOS_Water_Temperature',
    'IOOS_Wind',
    # water level datasets
    'IOOS_Raw_Water_Level',
    'IOOS_Daily_Verified_Water_Level',
    'IOOS_High_Low_Verified_Water_Level',
    'IOOS_Hourly_Height_Verified_Water_Level',
    'IOOS_SixMin_Verified_Water_Level',
]

# datums used by the water level datasets
DATUMS = [
    'MHHW', 'MHW', 'MTL', 'MSL', 'MLW', 'MLLW', 'STND', 'NAVD', 'IGLD'
]

# JSON list, as written by read_stations.py
STATIONS_FILE = 'station_ids.json'


TODAY = datetime.datetime.today()


def fetch_dataset(dataset, station, datum=None):

    fom = TODAY.replace(day=1)
    lom = TODAY

    # REST endpoint is picky and strange: insists first param
    # must be preceded by an ampersand, and all fields must be quoted.
    # Just concat ourselves.

    # count of consecutive months with no data found
    empty_months = 0
    going = True
    while going:
        begin = fom.strftime('%Y%m%d')
        end = lom.strftime('%Y%m%d')
        url = '{base}{dataset}.json?&STATION_ID="{station}"&BEGIN_DATE="{begin}"&END_DATE="{end}"'.format(
            base=BASE_URL,
            dataset=dataset,
            station=station,
            begin=begin,
            end=end
        )

        if datum:
            url += '&DATUM="{datum}"'.format(datum=datum)

        fname = 'data/{dataset}_{station}_{begin}_{end}.json'.format(
                dataset=dataset, station=station, begin=begin, end=end)

        # go to previous month on next iteration
        lom = fom - datetime.timedelta(days=1)
        fom = lom.replace(day=1)

        # skip files already downloaded
        if os.path.exists(fname):
            print('already have {f}'.format(f=fname))
            continue

        r = requests.get(url)
        if r.ok:
            # assumes local data directory exists
            with open(fname, 'wb') as inf:
                inf.write(r.text)
                empty_months = 0
        else:
            if r.text.find('produced no matching results') == -1:
                print('Error fetching URL {url}'.format(url=url))
                print(r.text)
                with open('errors.txt', 'wb') as error_file:
                    error_file.write('{url}\n'.format(url=url))
                time.sleep(5) # sleep a little, in case hitting server too hard
                return False  # bail on error (other than no results)
            else:
                empty_months += 1
                if empty_months > 24:
                    print('Saw more than two years of empty data for {d} station {s}'.format(d=dataset, s=station))
                    print('Last date checked: {fom}'.format(fom=fom))
                    going = False

    return True

# read stations
with open(STATIONS_FILE, 'rb') as inf:
    stations = json.load(inf)

print('loaded {n} stations'.format(n=len(stations)))

for dataset in DATASETS:
    print('processing {d}...'.format(d=dataset))
    if dataset.endswith('Water_Level'):
        for datum in DATUMS:
            print('processing datum {datum}...'.format(datum=datum))
            for station in stations:
                fetch_dataset(dataset, station, datum)
                if not status:
                    print('error')
                    sys.exit(1)
    else:
        for station in stations:
            status = fetch_dataset(dataset, station)
            if not status:
                print('error')
                sys.exit(1)

    print('\nAll done!')
