#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: util.py

import csv
import cPickle as pickle
from collections import defaultdict


def city_ip_stats():
    ret = defaultdict(int)
    reader = csv.DictReader(open('data/output.csv', 'rb'))
    with open('data/city_ip_stats.csv', 'w') as f:
        for line in reader:
            n = int(line['network'].split('/')[1])
            if line['subdivision_1_name']:
                ret[(float(line['latitude']),
                     float(line['longitude']))] += 2**(32 - n)
        f.write('city_pos,ip_stats\n')
        for k, v in sorted(ret.iteritems(), lambda x, y: cmp(x[1], y[1])):
            f.write('%s,%d\n' % (k, v))
    print 'cities:', len(ret)
    return ret


def state_ip_stats():
    ret = defaultdict(int)
    reader = csv.DictReader(open('data/output.csv', 'rb'))
    with open('data/state_ip_stats.csv', 'w') as f:
        for line in reader:
            n = int(line['network'].split('/')[1])
            if line['subdivision_1_name']:
                ret[line['subdivision_1_name']] += 2**(32 - n)
        f.write('state,ip_stats\n')
        for k, v in sorted(ret.iteritems(), lambda x, y: cmp(x[1], y[1])):
            f.write('%s,%d\n' % (k, v))
    print 'states:', len(ret)
    return ret


def ip_block_to_pos():
    ip_blocks = []
    reader = csv.DictReader(open('data/output.csv', 'rb'))
    for line in reader:
        start, n = line['network'].split('/')
        start = map(int, start.split('.'))
        start = reduce(lambda x, y: x*256 + y, start)
        end = start + 2**(32 - int(n))
        pos = (float(line['latitude']), float(line['longitude']))
        ip_blocks.append(((start, end), pos))
    ip_blocks = sorted(ip_blocks, lambda x, y: cmp(x[0][0], y[0][0]))
    for i in xrange(1, len(ip_blocks)):
        assert(ip_blocks[i - 1][0][1] <= ip_blocks[i][0][0])
    print 'ip_blocks:', len(ip_blocks)
    print 'ip_blocks[0]', ip_blocks[0]
    with open('data/ip_blocks_to_pos', 'wb') as f:
        pickle.dump(ip_blocks, f)
    return ip_blocks


if __name__ == "__main__":
    # city_ip_stats()
    # state_ip_stats()
    ip_block_to_pos()
