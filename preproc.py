#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: preproc.py

ip_blocks_file = 'data/GeoLite2/GeoLite2-City-Blocks-IPv4.csv'
locations_file = 'data/GeoLite2/GeoLite2-City-Locations-zh-CN.csv'
fout = 'data/blocks_locations.csv'
blocks_to_locations = {}

# 1.0.0.0/24,2077456,2077456,,0,0,,-27.0000,133.0000
# 5188416,zh-CN,NA,"北美洲",US,"美国",PA,"宾夕法尼亚州",,,,508,America/New_York

import csv


def get_records():
    ip_blocks_reader = csv.DictReader(open(ip_blocks_file, 'rb'))
    location_reader = csv.DictReader(open(locations_file, 'rb'))

    lookup = {row['geoname_id']: row for row in location_reader}

    for row in ip_blocks_reader:
        geoname_id = row['geoname_id']
        if not geoname_id:
            continue
        ret = {}
        ret.update(row)
        ret.update(lookup[geoname_id])
        yield ret

columns = ['network', 'subdivision_1_name', 'latitude', 'longitude']

with open('data/output.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    for row in get_records():
        if row['country_iso_code'] == 'US':
            writer.writerow([row[k] for k in columns])
